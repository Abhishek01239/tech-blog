---
title: "Claude Solves 25-Year Mystery Behind NIST Elliptic Curve Seeds"
date: 2026-10-21
draft: false
description: "Anthropic says an internal Claude research model traced the unexplained seeds for NIST curves including P-256 to lrand48 outputs seeded with Unix timestamps from 1997–1998, weakening long-standing backdoor suspicions."
image: "https://res.cloudinary.com/csacimzi/image/upload/v1792553932/techpulse/articles/claude-nist-curve-seeds-mystery.png"
tags: [Anthropic, Claude, NIST, cryptography, ECDSA, P-256, elliptic curves, AI research, cybersecurity]
categories: [Artificial Intelligence, Cybersecurity]
author: "TechPulse"
---
Anthropic’s Frontier Red Team reported on October 16, 2026, that an internal Claude research model reconstructed the origin of the seeds behind five widely used NIST elliptic curves in under half an hour. The seeds for P-192, P-224, P-256, P-384 and P-521 were not the result of a secret hash or passphrase, as many cryptographers had long assumed. They are ordinary output from the C library’s `lrand48` pseudorandom number generator, started from Unix timestamps between May 1997 and April 1998.

The finding addresses a question that has lingered since NIST published the curves in 2000. Because the NSA supplied the seeds without explanation, some researchers worried the numbers might hide a backdoor. Anthropic stresses that the discovery is not a break of ECDSA, not a new attack, and not evidence of a weakness in the curves themselves. It does, however, make a deliberate backdoor far less plausible.

## What Claude found

An Anthropic employee asked the model to determine how the seeds were generated and deliberately withheld the popular rumor that they came from hashing a humorous phrase such as “Give Bob and Jerry a raise.” Claude instead reasoned about what software a 1990s government team would have used. It wrote a scanner that tested 34 combinations of period generators and output slices against the published seeds.

A statistical fingerprint stood out. In four of the ten seeds examined, the top bit of every 32-bit word was zero—a pattern that would occur by chance roughly once in 5,810 trials. That signature matches `lrand48`, which returns only the top 31 bits of its 48-bit internal state. Claude recovered the missing bits, applied lattice techniques to reconstruct the generator states, and ran the process backward to the initial seeds.

Every recovered initialization value was a Unix timestamp from the late 1990s. Anthropic and independent verification by cryptographer Filippo Valsorda list the same range: roughly May 15, 1997, to April 3, 1998. For P-256, the most widely deployed of the set, the seed corresponds to the 1,842nd 20-byte candidate produced by a run started at 01:52:34 UTC on August 16, 1997. Anthropic published reproduction code so others can regenerate the exact byte strings that have appeared in the NIST standards for a quarter century.

The model also accounted for the base points of six curves, tracing them to the random generator in Arjen Lenstra’s FreeLIP library, seeded with small integers. Some binary-curve seeds appear to use a halved clock value that resolves to April 17, 1998.

## Why the mystery mattered

Elliptic-curve cryptography underpins a large share of modern digital signatures and key exchange. P-256 in particular appears in TLS certificates, code signing, cryptocurrency systems, and countless enterprise deployments. When the curves were standardized, the lack of a transparent seed-generation story fed two decades of suspicion. Jerry Solinas, the late NSA mathematician associated with the curves, had indicated in 2015 that the seeds came from hashing a phrase; several researchers, including Anthropic staff, pursued that lead without success.

A resolved origin story does not prove the curves are perfect, but it removes the most dramatic explanation for the unexplained numbers. Anthropic notes that a few viable candidate curves appear to have been skipped during generation; the team judges the selection of deliberately weakened curves implausible given how few candidates were discarded.

## Bounty and independent confirmation

Cryptographer Filippo Valsorda had offered a bounty for a complete explanation of the seeds. Anthropic’s team claimed it on October 15, 2026. Under the bounty terms the prize was tripled when donated to charity, producing a $36,864 donation to the Internet Security Research Group, the nonprofit behind Let’s Encrypt. Independent write-ups have reproduced the timestamps and generator states, confirming that the published seeds match `lrand48` output from those clock values.

## Practical implications

For most users and developers the immediate operational impact is limited: no patches are required and no existing keys are known to be compromised by this revelation. The episode does illustrate how frontier language models can accelerate specialized cryptanalysis when given a well-scoped research question and the ability to write and run supporting code. It also underscores the value of transparent parameter generation in future cryptographic standards. Designers of new curves and protocols have long preferred “nothing-up-my-sleeve” constructions precisely to avoid the kind of ambiguity that surrounded the NIST seeds for 25 years.

Security teams should treat the finding as historical clarification rather than an urgent vulnerability. Organizations that rely on P-256 and related curves can continue to do so on the same risk basis they already accepted; the new information simply makes the original parameter selection process more ordinary than many had feared.

## Why it matters

A quarter-century of speculation about possible NSA backdoors in foundational internet cryptography has been replaced by a mundane technical explanation: a standard library RNG and a handful of clock readings from 1997 and 1998. The result does not eliminate every theoretical concern about the curves, but it closes one of the longest-running open questions in applied cryptography and demonstrates that modern AI systems can contribute genuine progress on problems that had resisted conventional human effort.

### Sources
[1] [Anthropic Frontier Red Team research post (Oct. 16, 2026)](https://www.anthropic.com)
[2] [Coverage summarizing Claude’s reconstruction of the NIST seeds](https://aivy.com.au/news/claude-encryption-mystery/)
[3] [Independent technical accounts of the lrand48 timestamps and P-256 candidate 1842](https://www.bitsminds.com/news/claude-nist-ecdsa-curve-seeds-lrand48)
[4] [Reports on the $36,864 bounty donation to the Internet Security Research Group](https://ccleaks.com/news/anthropic-claude-nist-curve-seeds-oct-2026)
