---
title: "Cosine Similarity vs L2 Distance in FAISS, With Runnable Examples"
date: 2026-11-27T07:25:00+05:30
draft: false
description: "When do IndexFlatL2 and IndexFlatIP give the same ranking, and when do they disagree? A hands-on explanation with real FAISS output, the 2 − 2cos relationship, and a checklist for choosing an index."
categories: ["AI"]
image: "/images/covers/faiss-cosine-vs-l2-distance.jpg"
author: "Jaiswar Abhishek"
---

If you build semantic search with FAISS, you choose an index type before you write your first query. The two most common beginner choices are `IndexFlatL2` and `IndexFlatIP`. Tutorials use them interchangeably, and most of the time that's fine. Sometimes it isn't, and the results quietly come back in the wrong order.

I ran into the confusing side of this in my [resume screener](/posts/resume-screener-seven-versions/): earlier versions printed similarity scores where higher was better, and the FAISS version printed distances where lower was better. This post explains exactly how the two measures relate, using a small script you can run yourself. All numbers below are real output from that script (FAISS 1.16, NumPy, fixed random seed).

## Three ways to compare two vectors

An embedding is a list of numbers, a point in a space with hundreds of dimensions. "How similar are two texts?" becomes "how close are two points?" There are three common answers:

- **L2 (Euclidean) distance**: the straight-line distance between the points. Lower is more similar. `IndexFlatL2` returns the *squared* L2 distance, which saves a square root and doesn't change the order.
- **Inner product (dot product)**: multiply matching coordinates and add them up. Higher is more similar. It grows with the *length* of the vectors as well as their direction.
- **Cosine similarity**: the dot product of the two vectors after scaling each to length 1. It depends only on direction, ranging from -1 to 1. Higher is more similar.

FAISS doesn't have a separate cosine index. You get cosine similarity by normalising your vectors and using `IndexFlatIP`.

## The experiment

I made five random 384-dimensional "document" vectors, then made document 3 a copy of document 0 multiplied by three, plus a little noise. Documents 0 and 3 therefore point in nearly the same direction, which in embedding terms means they say nearly the same thing, but document 3's vector is about three times longer. The query is document 0 plus some noise.

```python
import numpy as np, faiss

rng = np.random.default_rng(42)
d = 384
docs = rng.normal(size=(5, d)).astype("float32")
docs[3] = docs[0] * 3 + rng.normal(scale=0.3, size=d)
query = (docs[0] + rng.normal(scale=0.8, size=d)).astype("float32")[None, :]
```

### Raw vectors, L2 distance

```python
l2 = faiss.IndexFlatL2(d); l2.add(docs)
D, I = l2.search(query, 5)
```

```
IndexFlatL2 raw   ids: [0, 2, 1, 4, 3]   dist: [259.8, 899.4, 922.9, 953.1, 1750.1]
```

Document 3, which has the same meaning as the query, comes **last**. L2 distance punishes it for being far away in absolute terms, even though it points in the right direction.

### Raw vectors, inner product

```python
ip = faiss.IndexFlatIP(d); ip.add(docs)
D, I = ip.search(query, 5)
```

```
IndexFlatIP raw   ids: [3, 0, 1, 2, 4]   score: [982.8, 329.4, 22.6, 15.5, 3.9]
```

Now document 3 comes **first**, with a score three times higher than document 0. The inner product rewards it for being long. Neither ranking reflects meaning alone.

### Normalised vectors

```python
dn, qn = docs.copy(), query.copy()
faiss.normalize_L2(dn); faiss.normalize_L2(qn)

ipn = faiss.IndexFlatIP(d); ipn.add(dn)   # cosine similarity
l2n = faiss.IndexFlatL2(d); l2n.add(dn)   # L2 on unit vectors
```

```
IP normalised     ids: [0, 3, 1, 2, 4]   cos:  [0.739, 0.734, 0.047, 0.034, 0.008]
L2 normalised     ids: [0, 3, 1, 2, 4]   dist: [0.522, 0.532, 1.905, 1.932, 1.984]
```

After normalising, both indexes agree. Documents 0 and 3 sit together at the top with almost identical scores, and the three unrelated documents are far behind. This is the ranking we actually wanted.

## Why they agree: dist² = 2 − 2·cos

For two vectors of length 1, the squared L2 distance and the cosine similarity are tied together by a simple identity:

> ‖a − b‖² = ‖a‖² + ‖b‖² − 2·(a · b) = 1 + 1 − 2·cos(a, b) = **2 − 2·cos(a, b)**

The script checks it numerically:

```python
print(np.round(2 - 2 * cos, 3))
# [0.522, 0.532, 1.905, 1.932, 1.984]   <- identical to the L2 distances above
```

So on unit vectors, a smaller distance always means a larger cosine similarity. The two indexes return the same neighbours in the same order; only the numbers and their direction differ. You can convert one to the other: `cos = 1 − dist / 2`.

The identity also explains the range of values. Squared L2 distance between unit vectors runs from 0 (identical) to 4 (opposite), and unrelated vectors in high dimensions tend to land near 2, which is exactly where documents 1, 2 and 4 are.

## What this means for real embedding models

Many sentence-embedding models already return unit-length vectors. For example, `all-MiniLM-L6-v2` from sentence-transformers ends with a normalisation layer, so `model.encode()` gives vectors of length 1. With those models, `IndexFlatL2` and `IndexFlatIP` produce the same ranking, which is why tutorials can use either and still get sensible results.

Problems appear when vectors aren't normalised:

- You switch to a model or API that doesn't normalise its output.
- You average several embeddings together (for example, to represent a long document), which produces a shorter vector.
- You concatenate or scale vectors yourself.

In those cases, L2 search starts favouring short vectors and inner-product search starts favouring long ones, exactly as the experiment showed. Since you can't always know what a model does, the safest habit is to normalise explicitly before adding to the index *and* before searching:

```python
faiss.normalize_L2(embeddings)        # in place, float32 only
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

faiss.normalize_L2(query)
scores, ids = index.search(query, k)
```

Normalising vectors that are already unit length does no harm. Note that `faiss.normalize_L2` works in place and expects a `float32` array, so convert with `.astype("float32")` first.

## Two more FAISS details that catch people out

**Missing results come back as `-1`.** If you ask for more neighbours than the index contains, FAISS fills the extra slots with the id `-1` and a huge distance. In Python, `names[-1]` silently returns the last element of a list, so you get a fake result instead of an error. Filter them out:

```python
hits = [(ids[0][i], scores[0][i]) for i in range(k) if ids[0][i] != -1]
```

**The meaning of "score" depends on the index.** With `IndexFlatL2` lower is better; with `IndexFlatIP` higher is better. If you pass results to a frontend or store them, name the field accordingly (`distance` or `similarity`) so nobody sorts or filters in the wrong direction. Other vector databases have the same issue: Qdrant, for instance, returns a similarity score for cosine collections, where higher is better.

## Which should you use?

| Situation | Index | Notes |
|---|---|---|
| Text embeddings, you want cosine similarity | `IndexFlatIP` on normalised vectors | Scores are easy to read (1 = identical) |
| Vectors already unit length, existing L2 code | `IndexFlatL2` | Same ranking; convert with `cos = 1 − d/2` |
| Magnitude genuinely carries meaning | Raw `IndexFlatIP` or `IndexFlatL2` | Rare for text; decide deliberately |
| Millions of vectors | `IndexHNSWFlat` or `IndexIVFFlat` | Approximate search; same metric choice applies |

The flat indexes compare the query with every stored vector, which is exact and fast enough for tens of thousands of items. Beyond that, approximate indexes trade a little accuracy for a lot of speed, but the metric question stays exactly the same.

## Try it yourself

The full script is about 25 lines. Install the dependencies with `pip install faiss-cpu numpy`, paste the snippets above into one file in order, and change the scale factor on document 3 from 3 to 0.3. When I did, document 3 jumped from last place to second under raw L2 search, and its raw inner-product score fell from 982.8 to 93.3. Its direction, and so its meaning, didn't change at all; only its length did. The normalised results stay the same. That is the clearest way to convince yourself why normalising matters.

## Sources

- [FAISS wiki: MetricType and distances](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances) (cosine similarity via normalised inner product)
- [FAISS wiki: getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [sentence-transformers/all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Qdrant documentation: distance metrics](https://qdrant.tech/documentation/concepts/search/)
