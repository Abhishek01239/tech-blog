---
title: "I Built a \"Chat With Your PDF\" App: The RAG Pipeline Step by Step, and What I'd Fix"
date: 2026-11-27T07:10:00+05:30
draft: false
description: "A walkthrough of a real retrieval-augmented generation (RAG) app built with FastAPI, Jina embeddings, Qdrant and Llama 3.3 on Groq: how each stage works, the actual code, and five design problems worth fixing."
categories: ["AI"]
image: "/images/covers/rag-pdf-chat-app-architecture-v2.jpg"
author: "Jaiswar Abhishek"
---

"Chat with your PDF" is one of the first projects most people build when they start working with large language models. It looks simple from the outside: upload a document, ask a question, get an answer. Inside, it is a small pipeline with five or six moving parts, and each part has its own ways of going wrong.

This post walks through the version I built, which is open source in my [pdf-semantic-search-faiss](https://github.com/Abhishek01239/pdf-semantic-search-faiss) repository. (The name is a leftover: the first version kept vectors in FAISS, and the current one stores them in Qdrant.) I'll go stage by stage with the real code, then cover five problems in that code that I would fix before anyone else relied on it. Those problems are the useful part. Most RAG tutorials stop at "it works", and none of these issues shows up until you look closely.

## What RAG actually means

A language model only knows what was in its training data. It has never seen your lecture notes, your company handbook or the PDF you downloaded this morning. **Retrieval-augmented generation** fixes that without retraining anything:

1. Split your documents into small passages (chunks).
2. Turn each chunk into a vector, a list of numbers that captures its meaning (an embedding).
3. When a question arrives, embed the question the same way and find the chunks whose vectors are closest.
4. Paste those chunks into the prompt and ask the model to answer *using only that text*.

The model does the writing; the retrieval step decides what it is allowed to know. If retrieval returns the wrong chunks, even the best model will give a confident wrong answer, so most of the engineering effort goes into steps 1 to 3.

## The stack

| Stage | What the app uses |
|---|---|
| API server | FastAPI |
| PDF text extraction | PyPDF2 |
| Chunking | LangChain `RecursiveCharacterTextSplitter`, with a plain-Python fallback |
| Embeddings | Jina AI `jina-embeddings-v3` over its REST API |
| Vector database | Qdrant Cloud, cosine distance |
| Answer generation | `llama-3.3-70b-versatile` on Groq |
| Frontend | React (Vite), served by FastAPI |

Everything here has a free tier, which is why I picked it as a student. None of the choices is unusual, so the lessons carry over to other stacks.

## Stage 1: upload and extract text

The `/upload` endpoint saves the uploaded file to a temporary path, reads every page and joins the text:

```python
reader = PdfReader(tmp_path)
text = ""
for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"
os.unlink(tmp_path)

if not text.strip():
    return {"success": False, "message": "No text could be extracted."}
```

The empty-text check matters more than it looks. A scanned PDF is just images of pages, so `extract_text()` returns nothing. Without this check the app would happily store zero chunks and then answer every question with "I could not find relevant information", which looks like a retrieval bug when it is really an input problem. Telling the user straight away is much better. Handling scans properly needs OCR (for example Tesseract) before chunking.

## Stage 2: chunking

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
return splitter.split_text(text)
```

Chunks are at most 500 characters, with up to 100 characters shared between neighbours so a sentence that falls on a boundary is not cut in half. The recursive splitter tries to break on paragraph breaks first, then line breaks, then spaces, so chunks usually end at natural boundaries.

Chunk size is the single setting that most changes answer quality, and the fallback splitter in this file has a subtle bug. I wrote a separate post on both: [Chunk Size and Overlap in RAG: What the Numbers Actually Do](/posts/rag-chunk-size-overlap-explained/).

## Stage 3: embeddings

Every chunk goes to Jina's embedding API in one request:

```python
response = requests.post(
    "https://api.jina.ai/v1/embeddings",
    headers={"Authorization": f"Bearer {JINA_API_KEY}",
             "Content-Type": "application/json"},
    json={"model": "jina-embeddings-v3", "input": texts},
)
response.raise_for_status()
return [item["embedding"] for item in response.json()["data"]]
```

Using a hosted embedding API instead of running a model locally kept the server small enough for a free hosting plan. The trade-off is that every upload and every question costs a network round trip, and the API key has to live on the server, never in the React code.

## Stage 4: storing vectors in Qdrant

```python
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
)
...
PointStruct(
    id=str(uuid.uuid4()),
    vector=embeddings[i],
    payload={"text": chunks[i], "source": filename, "chunk_id": i},
)
```

Two details are worth copying. First, the collection is created lazily with the vector size taken from the first embedding, so switching embedding models does not mean editing a hard-coded dimension. Second, the payload stores the chunk text, the file name and the chunk number. That metadata is what lets the API return sources with each answer, which is the only way a user can check whether the model's answer actually came from their document.

## Stage 5: retrieval and the prompt

A question is embedded, the five nearest chunks are fetched, and their text is joined into a context block:

```python
results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_embedding,
    limit=top_k,
)
```

The prompt then gives the model strict rules. The most important ones are "use ONLY the document context below" and a fixed sentence to say when the answer is missing: *"The uploaded documents do not contain this information."* Giving the model an exact fallback sentence works better than a vague instruction like "don't make things up", because it gives the model an acceptable way to say no. A low temperature (0.2) keeps answers close to the text.

The prompt also tells the model never to ask the user to upload a PDF. That rule exists because, without it, the model sometimes replied as if it had no document at all, even with context in the prompt. Writing rules against the specific failures you observe is normal prompt work, and those rules are worth keeping in version control next to the code.

## Five things I would fix

This is where the project becomes interesting. Each of these works in a demo with one user and one document and breaks in real use.

### 1. Conversation memory is shared by everyone

```python
conversation_history = []

def add_message(role, content):
    conversation_history.append({"role": role, "content": content})
```

The chat history is a module-level Python list. Every request from every user appends to the same list, so if two people use the app at once, each one's questions leak into the other's prompt. The list also grows forever until someone calls `/clear`, which makes prompts longer and slower over time.

**Fix:** give each browser a session ID (a random UUID sent with each request), keep history per session (in Redis, a database, or at least a dictionary keyed by session), and only send the last few turns to the model.

### 2. Every upload goes into one shared collection

All chunks land in a single collection called `pdf_chunks`, and search never filters by file. Upload a physics textbook and then a menu, and a question about pasta can retrieve physics chunks. The model is told to use only the context, so it will try to answer from whatever it gets.

**Fix:** store a `document_id` (or user ID) in each payload and pass a Qdrant filter on that field at query time, so a question only searches the documents it belongs to.

### 3. "Summarise this PDF" doesn't do what it looks like

```python
if question.lower() in special_queries:
    results = search_chunks("", top_k=15)
```

For questions like "summarize pdf", the code searches with an empty string and asks for 15 results. The intent is "give me the whole document", but a vector search always returns the chunks nearest to *some* vector, here the embedding of an empty string. Those 15 chunks are not the beginning of the document, not a representative sample, and may not even come from the right file.

**Fix:** treat summaries as a different job. Fetch the document's chunks in order using a payload filter (Qdrant's scroll API does this), then summarise in stages: summarise groups of chunks, then summarise the summaries. This is often called map-reduce summarisation.

### 4. The "distance" field is actually a similarity score

The API returns each source with a field named `distance`, filled from `point.score`. With cosine distance in Qdrant, that score is a similarity: **higher means more relevant**. Anyone reading the field name would assume the opposite. Small naming mistakes like this end up in frontend logic ("hide sources with distance above 0.5") and quietly invert it. I wrote more about how similarity and distance relate in [Cosine Similarity vs L2 Distance in FAISS](/posts/faiss-cosine-vs-l2-distance/).

**Fix:** rename it to `score` and document the direction. While you're there, set a minimum score below which chunks are dropped, so an unrelated question gets the "not in your documents" answer instead of five weak matches.

### 5. Large PDFs go to the embedding API in one request

The whole list of chunks is sent in a single call. A 300-page PDF produces well over a thousand chunks, and embedding APIs limit how many inputs and tokens one request may contain. When that limit is hit, the upload fails with an HTTP error and nothing is stored.

**Fix:** embed in batches (64 or 128 chunks at a time), retry a batch with a short back-off when it fails, and upsert each batch as it completes so a failure halfway through doesn't lose everything.

## A smaller one: use `pypdf`

PyPDF2 is no longer developed; its work continues in the [`pypdf`](https://pypi.org/project/pypdf/) package with a nearly identical API. My later projects already use `from pypdf import PdfReader`. It's a one-line change and worth making in any new project.

## What I took away

The model call is about ten lines. Everything else (extraction, chunking, storage, filtering, sessions, batching) is ordinary backend engineering, and that is where quality comes from. If your RAG app gives strange answers, print the retrieved chunks before blaming the model. My code already logs the question, results and context on every request, and that habit is the most useful debugging tool in the whole project.

## Sources

- [Qdrant documentation: distance metrics and search](https://qdrant.tech/documentation/concepts/search/)
- [Qdrant documentation: filtering](https://qdrant.tech/documentation/concepts/filtering/)
- [LangChain: RecursiveCharacterTextSplitter](https://python.langchain.com/docs/how_to/recursive_text_splitter/)
- [Jina AI embeddings API](https://jina.ai/embeddings/)
- [pypdf on PyPI](https://pypi.org/project/pypdf/)
- Source code: [github.com/Abhishek01239/pdf-semantic-search-faiss](https://github.com/Abhishek01239/pdf-semantic-search-faiss)
