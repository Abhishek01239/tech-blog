---
title: "Seven Versions of a Resume Screener: From Keyword Matching to FAISS"
date: 2026-11-27T07:20:00+05:30
draft: false
description: "How my resume screening project evolved over seven versions, from one cosine-similarity score to a FAISS index behind a FastAPI app, and the hidden problems at each step: truncated embeddings, substring matching, fragile regexes and a FAISS -1 bug."
categories: ["AI"]
image: "/images/covers/resume-screener-seven-versions-v2.jpg"
author: "Jaiswar Abhishek"
---

Applicant tracking systems (ATS) rank resumes against a job description before a human reads them. I wanted to understand how that ranking could work, so I built one, and then rebuilt it six more times as each version showed me something the previous one got wrong.

All seven versions are in my [Resume-Screening-System](https://github.com/Abhishek01239/Resume-Screening-System) repository, side by side. This post goes through them in order. Each version is short, so you can follow the code, and each one has a lesson that applies well beyond resumes: to search, recommendation and any project that compares text.

## Version 1: one number from two embeddings

The first version is 34 lines. It embeds a job description and a resume with the `all-MiniLM-L6-v2` sentence-transformer model and compares them with cosine similarity:

```python
model = SentenceTransformer("all-MiniLM-L6-v2")

job_embedding = model.encode(job_description)
resume_embedding = model.encode(resume)

score = cosine_similarity([job_embedding], [resume_embedding])
print("Match Score: ", round(score[0][0] * 100, 2), "%")
```

An embedding turns text into a list of 384 numbers that represents its meaning, so texts about similar things end up with similar vectors. Cosine similarity measures the angle between two vectors: 1 means they point the same way, 0 means unrelated.

**The lesson:** this works surprisingly well for a first try, and the "%" sign is misleading. Cosine similarity is not a percentage of requirements met. Two unrelated texts in the same language often score well above zero, so a "45% match" means very little on its own. The number is only useful for *comparing* candidates against the same job description.

## Version 2: ranking several candidates, plus a skills list

Version 2 scores three candidates, sorts them, and adds an explicit check for required skills:

```python
for skill in required_skills:
    if skill in resume_lower:
        matched_skills.append(skill)

missing_skills = list(required_skills - set(matched_skills))
```

Now the output explains itself: Candidate C ranks first, has all five skills, and is missing none. Explanations matter in screening, because a recruiter needs to know *why* someone was ranked low.

**The lesson:** plain substring matching has two failure modes that pull in opposite directions.

- **False negatives.** A resume that says "Natural Language Processing" does not contain "nlp", so the skill is marked missing.
- **False positives.** If "java" were on the list, every resume mentioning "JavaScript" would match it, because "java" is inside "javascript".

The second problem is fixed by matching whole words with a regular expression such as `\bjava\b`. The first needs something smarter, which is what version 3 tried.

## Version 3: semantic skill matching

Instead of exact text, version 3 embeds each required skill and each skill on the resume, and accepts the best match above a threshold of 0.70:

```python
for job_skill in required_skills:
    job_embedding = model.encode(job_skill)
    best_score, best_match = 0, None
    for resume_skill in resume_skills:
        similarity = cosine_similarity([job_embedding], [model.encode(resume_skill)])[0][0]
        if similarity > best_score:
            best_score, best_match = similarity, resume_skill
    if best_score >= threshold:
        matched_skills.append({"required_skill": job_skill, "matched_with": best_match})
```

The test data makes a good stress test: the job asks for "PyTorch" and "Natural Language Processing", the resume says "Torch" and "NLP".

**Two lessons.** First, a fixed threshold like 0.70 is a guess. Short phrases such as skill names produce less reliable embeddings than full sentences, and abbreviations like "NLP" may or may not land close to their full form. The only way to set the threshold is to label some real pairs by hand and measure where correct and incorrect matches separate. Second, the loop calls `model.encode` on every resume skill again for every job skill. Encoding the lists once, in batches (`model.encode(list_of_skills)`), does the same work far faster.

## Version 4: real PDF resumes

Version 4 drops the hard-coded strings, reads every PDF in a folder with `pypdf`, embeds the full text of each and ranks them.

**The lesson, and the most important one in this project:** `all-MiniLM-L6-v2` only reads the first **256 word pieces** of its input and silently ignores the rest. Its model card says so plainly, but nothing warns you at runtime. A one-page resume is often 400 to 700 words, which is far more than 256 word pieces. So version 4 is really comparing the job description with the *top* of each resume: the name, contact details, summary and maybe the education section. The skills and projects lower down may never be seen.

That explains results that otherwise look random. There are three practical fixes:

1. **Chunk the resume** into passages, embed each, and score the resume by its best-matching (or average of top-3) passages. This is the same idea as chunking in RAG, which I explain in [Chunk Size and Overlap in RAG](/posts/rag-chunk-size-overlap-explained/).
2. **Extract sections first** (skills, experience, projects) and embed the ones that matter.
3. **Use a model with a longer input limit**, and still check its limit rather than assuming.

You can check any sentence-transformers model's limit with `model.max_seq_length`, and count a text's tokens with `len(model.tokenizer(text)["input_ids"])`. It's worth doing for every project that embeds documents.

## Version 5: a weighted ATS score

Version 5 moves away from a single similarity number to a score built from four parts:

```python
final_score = (
    skills * 0.4 +
    experience * 0.3 +
    education * 0.2 +
    certification * 0.1
)
```

Each part is between 0 and 100. Skills are the share of required skills found, education and certifications add points for matching keywords, and experience compares the years found with the years required.

**The lesson:** a weighted formula is easy to explain and easy to break. The years of experience come from this regex:

```python
match = re.search(r'(\d+)\s+years', text, re.IGNORECASE)
```

It takes the **first** number followed by "years", wherever it appears. Real resumes defeat it in several ways:

- "3+ years of experience" doesn't match, because the `+` sits between the number and the space.
- "5 yrs" doesn't match at all.
- "Completed a 4 years B.Tech programme" matches, and reports four years of work experience.
- "Moved to Pune 2 years ago" matches too, if it appears before the real figure.

Rules like this are fine for a prototype as long as you know their limits. A better approach is to compute experience from the date ranges in the work history section, or at least to collect every match and show the recruiter which line produced the number.

## Version 6: a FAISS index

Embedding every resume each time a new job comes in doesn't scale. Version 6 splits the work in two scripts: `build_index.py` embeds every resume once and saves a FAISS index plus a list of file names, and `search_index.py` embeds only the job description and searches the index.

```python
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
faiss.write_index(index, "resume_index.faiss")
...
distances, indices = index.search(query_embedding, k)
```

**Lesson one: the direction of the score flipped.** Versions 1 to 5 printed similarities, where higher is better. `IndexFlatL2` returns squared distances, where *lower* is better. Because `all-MiniLM-L6-v2` produces unit-length vectors, ranking by L2 distance gives exactly the same order as ranking by cosine similarity, so the results are right. But anyone used to the earlier "match %" will read the printout backwards. I explain the maths, with runnable examples, in [Cosine Similarity vs L2 Distance in FAISS](/posts/faiss-cosine-vs-l2-distance/).

**Lesson two: a quiet bug when there are fewer resumes than `k`.** The search asks for the top 3. If the index holds only two resumes, FAISS fills the missing slot with the index `-1`. I tested this directly:

```python
index.add(two_vectors)
D, I = index.search(query, 3)
print(I)                          # [[ 0  1 -1]]
print([names[j] for j in I[0]])   # ['alice.pdf', 'bob.pdf', 'bob.pdf']
```

In Python, `names[-1]` is the *last* item in the list, so the third "candidate" is Bob again, with an enormous distance that is easy to miss. Always skip negative indices:

```python
results = [(names[j], d) for j, d in zip(I[0], D[0]) if j != -1]
```

## Version 7: a FastAPI service and a Streamlit front end

The final version, in `resume-screening-bert`, wraps the search in a FastAPI app with `/upload_resume` and `/search` endpoints and a Streamlit interface, plus a separate ATS score module. It is the first version someone else could use.

**The lessons here are about turning a script into a service:**

- **Uploaded files aren't searchable yet.** `/upload_resume` saves the PDF to disk, but the FAISS index is only rebuilt when `build_index.py` runs. Either rebuild (or `index.add`) after each upload, or tell the user the upload will be searchable after the next re-index.
- **Never trust the uploaded file name.** The code saves to `os.path.join(UPLOAD_FOLDER, file.filename)`. A file name like `../../app.py` can write outside the upload folder on some setups. Generate your own name (for example a UUID plus `.pdf`) and keep the original name only as data.
- **Resumes are personal data.** A real screener needs a retention policy, access control and a way to delete a candidate's file on request.

## What seven versions taught me

Looking back, the biggest improvements didn't come from a better model. They came from understanding the tools I already had: that the model truncates long input, that substring matches can lie, that FAISS returns distances rather than scores and pads results with `-1`. Each of those took one line to check once I knew to look.

There is also a fairness point that matters more than any of the code. Automated screening can reject good candidates for reasons that have nothing to do with ability, such as an unusual resume layout, a skill written differently, or a career break. A tool like this should rank and explain, and leave the decision to a person.

## Sources

- [sentence-transformers/all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) (384 dimensions; input truncated at 256 word pieces)
- [Sentence Transformers documentation: max sequence length](https://sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html)
- [FAISS wiki: getting started and search results](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [Python `re` documentation: word boundaries](https://docs.python.org/3/library/re.html)
- [OWASP: unrestricted file upload](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)
- Source code: [github.com/Abhishek01239/Resume-Screening-System](https://github.com/Abhishek01239/Resume-Screening-System)
