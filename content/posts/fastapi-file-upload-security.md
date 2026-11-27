---
title: "Securing File Uploads in FastAPI: Five Mistakes I Found in My Own Code"
date: 2026-11-27T08:00:00+05:30
draft: false
description: "A tested walkthrough of common FastAPI upload vulnerabilities, from path traversal through os.path.join to missing size limits and spoofed extensions, using real endpoints from two of my projects, plus a safe upload handler you can copy."
categories: ["Cybersecurity"]
image: "/images/covers/fastapi-file-upload-security.jpg"
author: "Jaiswar Abhishek"
---

Two of my projects accept file uploads through FastAPI: a [resume screener](/posts/resume-screener-seven-versions/) and a [chat-with-your-PDF app](/posts/rag-pdf-chat-app-architecture/). Both upload endpoints were written quickly to get a demo working, which is how most upload code starts.

When I reviewed them with a security mindset, I found five problems. None of them is exotic; they're among the most common mistakes in upload handling, which is exactly why they're worth walking through. For each one I'll show the original code, a test that demonstrates the problem, and the fix. Every result below comes from running the code with FastAPI 0.165 and Starlette 1.7 using FastAPI's `TestClient`.

## The original endpoint

This is the upload handler from the resume screener:

```python
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "file": file.filename}
```

It's short and looks harmless. It contains three of the five problems.

## Mistake 1: trusting the file name (path traversal)

`file.filename` is whatever the client put in the upload request. A browser sends the real file name, but anyone can send any string with a tool like `curl`. I sent three uploads to the endpoint above and logged where each file was written:

```python
for name in ["resume.pdf", "../escaped.txt", "/tmp/absolute.txt"]:
    r = client.post("/upload_resume", files={"file": (name, b"hello", "application/pdf")})
```

```
'resume.pdf'        -> saved to .../upl/uploads/resume.pdf
'../escaped.txt'    -> saved to .../upl/escaped.txt
'/tmp/absolute.txt' -> saved to /tmp/absolute.txt
```

The second upload climbed out of the `uploads` folder using `../`. That's **path traversal**, and it means an attacker can write files wherever the server process has permission, potentially overwriting the application's own code or configuration.

The third result surprises many Python developers. **If any argument to `os.path.join` is an absolute path, everything before it is discarded.** `os.path.join("uploads", "/tmp/absolute.txt")` returns just `/tmp/absolute.txt`. No `../` is needed at all. This is documented behaviour of `os.path.join`, and `pathlib`'s `/` operator does the same.

**Fix:** never use the client's file name as a path. Generate your own:

```python
stored_name = f"{uuid.uuid4().hex}.pdf"
target = UPLOAD_DIR / stored_name
```

If you want to show the original name later, store it as data (in a database row, for example), and strip any directory parts with `Path(file.filename).name`.

## Mistake 2: no size limit

The PDF app reads the whole upload into memory in one call:

```python
contents = await file.read()
```

There's no limit on how large `contents` can be. A few uploads of multi-gigabyte files can exhaust the server's memory and take it down for everyone. That's a denial-of-service problem, and on a small free-tier server it takes very little to trigger.

**Fix:** read in chunks and stop once a limit is crossed:

```python
MAX_BYTES = 5 * 1024 * 1024   # 5 MB
size = 0
while chunk := await file.read(64 * 1024):
    size += len(chunk)
    if size > MAX_BYTES:
        raise HTTPException(413, "File is larger than 5 MB.")
    out.write(chunk)
```

It's also worth setting a request body limit in front of the app, in your reverse proxy or hosting platform, so oversized requests are rejected before they reach Python at all.

## Mistake 3: checking the extension, and checking it badly

The PDF app checks file types like this:

```python
if not file.filename.endswith(".pdf"):
    return {"success": False, "message": "Only PDF files are allowed."}
```

There are two problems. First, it's case-sensitive, so a perfectly good `CV.PDF` is rejected. Second, and more important, the extension proves nothing about the contents. Any file can be renamed to end in `.pdf`.

The `Content-Type` header the client sends is no better; it's also chosen by the client. My test uploads all claimed `application/pdf`, including the one that wasn't.

**Fix:** check the extension case-insensitively for a friendly error message, then check the file's actual first bytes. Every PDF starts with the five characters `%PDF-`, a so-called "magic number":

```python
if not (file.filename or "").lower().endswith(".pdf"):
    raise HTTPException(400, "Only PDF files are allowed.")

head = await file.read(5)
if head != b"%PDF-":
    raise HTTPException(400, "File is not a valid PDF.")
```

A magic-number check stops casual mistakes and simple disguises, such as an executable renamed to `.pdf` (which starts with `MZ`). It isn't a complete defence against a crafted malicious PDF, so the parser that opens the file should still be kept up to date and treated as handling untrusted input.

## Mistake 4: temporary files that leak on errors

The PDF app writes uploads to a temporary file so PyPDF2 can read it:

```python
with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
    tmp.write(contents)
    tmp_path = tmp.name

reader = PdfReader(tmp_path)
...
os.unlink(tmp_path)
```

`delete=False` means the file stays on disk until the code removes it, and the `os.unlink` only runs if everything before it succeeds. When a corrupt or malicious PDF makes the parser raise an exception, the function jumps to its error handler and the temporary file is never deleted. Each bad upload leaves a file behind, slowly filling the disk.

**Fix:** clean up in a `finally` block, which runs whether or not an exception occurred:

```python
try:
    reader = PdfReader(tmp_path)
    text = "".join(page.extract_text() or "" for page in reader.pages)
finally:
    os.unlink(tmp_path)
```

Even simpler, `PdfReader` accepts a file-like object, so you can often skip the temporary file entirely and pass `io.BytesIO(contents)`.

## Mistake 5: CORS wide open

The PDF app enables cross-origin requests like this:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

CORS controls which *websites* may call your API from a visitor's browser. `allow_origins=["*"]` lets any site do so. For an API with no logins, the immediate risk is limited: anyone can call it directly with `curl` anyway. But it does mean any web page can quietly use your API, and your embedding and LLM quota, from its visitors' browsers. Combining a wildcard with `allow_credentials=True` is the kind of setting that becomes a real vulnerability the day authentication is added.

**Fix:** list the exact origins that host your frontend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.example"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

Since my PDF app serves its React frontend from the same FastAPI server, it barely needs CORS at all; same-origin requests aren't subject to it.

## A safer upload handler

Putting the fixes together:

```python
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()
UPLOAD_DIR = Path("uploads").resolve()
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_BYTES = 5 * 1024 * 1024
CHUNK = 64 * 1024

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed.")

    head = await file.read(5)
    if head != b"%PDF-":
        raise HTTPException(400, "File is not a valid PDF.")

    stored_name = f"{uuid.uuid4().hex}.pdf"
    target = UPLOAD_DIR / stored_name
    size = len(head)
    try:
        with open(target, "wb") as out:
            out.write(head)
            while chunk := await file.read(CHUNK):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(413, "File is larger than 5 MB.")
                out.write(chunk)
    except Exception:
        target.unlink(missing_ok=True)   # never leave partial files behind
        raise

    return {"id": stored_name, "original_name": Path(file.filename).name, "bytes": size}
```

I ran the same kinds of hostile uploads against it:

```
'resume.pdf'          200  stored as 633f348c...pdf, original_name 'resume.pdf'
'../escaped.pdf'      200  stored as 0f25f56b...pdf, original_name 'escaped.pdf'
'/tmp/absolute.pdf'   200  stored as 83182881...pdf, original_name 'absolute.pdf'
'CV.PDF'              200  stored as 4d349c3d...pdf
'notes.pdf' (not PDF) 400  File is not a valid PDF.
'big.pdf' (6 MB)      413  File is larger than 5 MB.
```

Every file now lands inside `uploads/` under a random name, nothing was written to `/tmp`, the disguised file was rejected, and the oversized upload was refused with its partial file deleted.

## A checklist for any upload endpoint

- Generate stored file names yourself; treat the client's name as untrusted text.
- Enforce a maximum size while reading, not after.
- Validate the content (magic bytes, or a real parser), not just the extension or `Content-Type`.
- Clean up temporary and partial files in `finally` or `except` blocks.
- Store uploads outside any folder your web server serves directly.
- Restrict CORS to the origins you actually use.
- Treat uploaded documents like resumes as personal data: limit who can read them and delete them when they're no longer needed.

## Sources

- [OWASP: file upload cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [OWASP: path traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [Python documentation: `os.path.join`](https://docs.python.org/3/library/os.path.html#os.path.join) (absolute components discard earlier ones)
- [FastAPI documentation: request files and `UploadFile`](https://fastapi.tiangolo.com/tutorial/request-files/)
- [FastAPI documentation: CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN: cross-origin resource sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
