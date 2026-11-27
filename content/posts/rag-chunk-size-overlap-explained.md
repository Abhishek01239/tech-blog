---
title: "Chunk Size and Overlap in RAG: What the Numbers Actually Do"
date: 2026-11-27T07:15:00+05:30
draft: false
description: "How chunk_size and chunk_overlap really behave in a RAG pipeline, shown with runnable Python: why a naive splitter creates duplicate chunks, why the recursive splitter often applies no overlap at all, and how to choose values."
categories: ["AI"]
image: "/images/covers/rag-chunk-size-overlap-explained-v2.jpg"
author: "Jaiswar Abhishek"
---

Almost every retrieval-augmented generation (RAG) tutorial contains a line like `chunk_size=500, chunk_overlap=100`. The numbers are copied from project to project, mine included, and rarely explained. They matter a lot: chunking decides what the retriever can find, and the model can only answer from what the retriever finds.

This post looks at what those two numbers actually do, using the splitter from my [PDF chat app](/posts/rag-pdf-chat-app-architecture/) and LangChain's `RecursiveCharacterTextSplitter`. Every output below comes from running the code shown, so you can paste it into a file and check it yourself.

## Why we chunk at all

Embedding models turn a piece of text into one vector. If you embed a whole 40-page PDF as a single vector, that vector is an average of everything in it, and it will match almost no specific question well. Embedding models also have an input limit and silently cut off anything longer. (For example, the popular `all-MiniLM-L6-v2` model truncates input after 256 word pieces, which I ran into in my [resume screener](/posts/resume-screener-seven-versions/).)

So we split documents into passages small enough to be about one thing, embed each passage, and retrieve the few that match a question. Two settings control the split:

- **`chunk_size`**: the maximum length of a chunk. In LangChain's character splitters this is measured in **characters** by default, not words or tokens.
- **`chunk_overlap`**: how much text neighbouring chunks may share, so a fact that sits on a boundary appears whole in at least one chunk.

## The naive splitter, and its duplicate-chunk bug

My app uses LangChain when it is installed and falls back to this simple loop otherwise:

```python
def naive_chunks(text, chunk_size=500, chunk_overlap=100):
    if not text:
        return []
    chunks, start, length = [], 0, len(text)
    while start < length:
        end = start + chunk_size
        chunks.append(text[start:end])
        start = max(0, end - chunk_overlap)
    return chunks
```

Each step moves forward by `chunk_size - chunk_overlap` (400) characters. That looks right. Here are the chunk lengths it produces for three text lengths:

```python
for n in (450, 1000, 1250):
    print(n, "chars ->", [len(c) for c in naive_chunks("x" * n)])
```

```
450 chars -> [450, 50]
1000 chars -> [500, 500, 200]
1250 chars -> [500, 500, 450, 50]
```

Look at the 450-character case. The first chunk already contains the whole text. The loop still runs once more, starting at character 400, and produces a 50-character chunk that is an exact copy of the end of the first one. The 1,250-character case has the same problem: its last chunk sits entirely inside the one before it.

Duplicates like this are not harmless. When a question matches that passage, both copies come back in the top results, so one of your five context slots is wasted on text the model already has. Tiny fragments also tend to embed poorly because there is so little text to go on.

The fix is to stop as soon as a chunk reaches the end of the text:

```python
while start < length:
    end = min(start + chunk_size, length)
    chunks.append(text[start:end])
    if end == length:
        break
    start = end - chunk_overlap
```

If you ever write your own splitter, also check that `chunk_overlap` is smaller than `chunk_size`. If it isn't, `start` never moves forward and the loop runs forever.

## Character boundaries cut sentences in half

The second problem with a fixed-width splitter is where it cuts. I built a small test document from a short refund-and-shipping policy repeated four times (1,216 characters) and split it into 200-character chunks with 40 characters of overlap:

```python
nv = naive_chunks(doc, 200, 40)
print(repr(nv[0][-40:]))
print(repr(nv[1][:40]))
```

```
'en downloaded.\n\nShipping takes 5 to 7 bu'
'en downloaded.\n\nShipping takes 5 to 7 bu'
```

The first chunk ends in the middle of the word "business", and the overlap repeats that broken fragment at the start of the next chunk. The overlap did its job mechanically, but the result is two chunks that each mix the refund topic with half a sentence about shipping. Mixed chunks produce blurry embeddings that match neither topic strongly.

## The recursive splitter, and why overlap often does nothing

`RecursiveCharacterTextSplitter` tries a list of separators in order: paragraph breaks (`"\n\n"`), then line breaks, then spaces, then single characters. It only falls back to a smaller separator when a piece is still too long. Running it on the same document:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

rs = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=40).split_text(doc)
print(len(rs), [len(x) for x in rs])
print(repr(rs[0]))
print(repr(rs[1]))
```

```
8 [174, 126, 174, 126, 174, 126, 174, 126]
'Refunds are available within 30 days of purchase. To request one, email support with your order number. Digital products are refundable only if they have not been downloaded.'
'Shipping takes 5 to 7 business days within India. International orders take 10 to 15 business days and may incur customs fees.'
```

Every chunk is now exactly one paragraph and exactly one topic. That is a big improvement.

But notice something the documentation doesn't make obvious: **there is no overlap at all**. Each paragraph fitted under 200 characters, so the splitter never had to cut inside one, and it doesn't copy text across paragraph boundaries. Overlap is only applied when the splitter has to break a long piece into smaller ones. With well-structured text and a generous `chunk_size`, your `chunk_overlap` setting may be doing nothing. That is usually fine, because a clean paragraph boundary is exactly where you don't need overlap.

## How to choose the numbers

There is no universal best value, but there is a sensible way to choose:

1. **Look at your documents.** If your PDFs are made of short paragraphs or numbered clauses, a `chunk_size` slightly larger than a typical paragraph keeps one idea per chunk. For dense textbooks, a larger size (1,000 to 1,500 characters) keeps explanations together.
2. **Remember the embedding model's limit.** Roughly four characters make one token in English. A 500-character chunk is around 125 tokens, comfortably inside every common model's limit. A 4,000-character chunk may be silently truncated.
3. **Count your context budget.** Retrieving five 500-character chunks puts about 2,500 characters into the prompt. If answers need more surrounding detail, increasing `top_k` and increasing `chunk_size` are two different levers: more small chunks gives variety, fewer large chunks gives continuity.
4. **Use 10 to 20 percent overlap** as a starting point, and accept that with paragraph-aware splitting it will only apply to long paragraphs.
5. **Test with real questions.** Write ten questions you know the answers to, print the retrieved chunks for each, and check whether the answer is actually inside them. If it isn't, the problem is chunking or retrieval, not the language model.

## A quick checklist

- Splitting by characters? Know that 500 means characters, not words.
- Writing your own loop? Stop at the end of the text, and keep overlap smaller than chunk size.
- Seeing duplicate sources in results? Look for tail chunks contained inside their neighbour.
- Answers missing details that sit across a paragraph break? That is the one case where you may want to add the previous paragraph to each chunk as context.

## Sources

- [LangChain: recursively split text by characters](https://python.langchain.com/docs/how_to/recursive_text_splitter/)
- [sentence-transformers/all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) (input truncation at 256 word pieces)
- [OpenAI: what are tokens and how to count them](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them) (the four-characters-per-token rule of thumb)
- Original splitter: [chunker.py in pdf-semantic-search-faiss](https://github.com/Abhishek01239/pdf-semantic-search-faiss/blob/main/backend/chunker.py)
