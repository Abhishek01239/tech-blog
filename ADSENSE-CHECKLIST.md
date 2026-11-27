# AdSense re-application checklist

The first application was rejected for "low value content". This branch rebuilds the site around original, first-hand content. Some steps need the site owner and can't be automated.

## Done on this branch

- [x] **Retired all 8 remaining news-rewrite posts** to `archive/posts/` (not built). Rewritten news is the most common cause of a "low value content" decision. Combined with the earlier 20, all 28 news posts are now out of the build.
- [x] **10 new guides built from the owner's own repositories**, each using real code from those projects, with outputs that were actually run (FAISS, chunking, CVSS, FFmpeg, loudnorm, git and FastAPI tests were all executed while writing):
  - AI: RAG PDF app architecture, chunk size and overlap, resume screener's seven versions, cosine vs L2 in FAISS
  - Automation: Thompson-sampling bandit (with simulation chart), 16:9 → 9:16 FFmpeg layouts (with real output frames), two-pass loudnorm
  - DevOps: GitHub Actions cron gotchas, the `git rebase -X ours` trap
  - Cybersecurity: FastAPI file upload security
- [x] **Finished the 3 drafts** (CVSS, CVE tracker, Hugo on Vercel) and published them. Removed the owner checklists, filled the "what I'd do differently" section, added a tested CVSS calculator, and documented a real local/production Hugo version mismatch.
- [x] **Original cover image for every post** (generated, no stock or AI photos) plus two real figures.
- [x] **New category structure** matching the content: AI, Automation, DevOps, Cybersecurity, each with an intro paragraph.
- [x] **Homepage, footer, About and Editorial Policy** updated to describe the site honestly, including that AI tools may help with drafting and that the author reviews everything.
- [x] **Weekly Vulnerability Watch refresh workflow.** The snapshot had not been refreshed since 13 November.
- [x] **Local Hugo now matches production** (`hugo-bin` pinned to 0.167.0 in `package.json`).

## Owner to-do before re-applying

1. **Read every post before merging.** You are the named author. Fix anything that doesn't sound like you, and correct any detail about your projects that is wrong. Each post links to the repo it describes.
2. **Fix the bugs the posts describe, or keep the posts honest.** Several posts say "here is what I'd fix". If you fix them in the repos, add a short "Update:" note to the post.
3. **Merge, then run the Vulnerability Watch workflow once** (Actions → Refresh Vulnerability Watch snapshot → Run workflow).
4. **Search Console:** submit `sitemap.xml` again, and let the retired URLs return 404 (or use Removals).
5. **Keep publishing, slowly.** Aim for 1–2 new guides a week for the next 4–6 weeks, in the same style: something you built, with real code and output. 20+ strong posts is a comfortable target.
6. **Consent management:** create the GDPR message in AdSense (Privacy & messaging) so ads can serve in the EEA, UK and Switzerland.
7. **Re-apply** after a few weeks of steady publishing, once Google has recrawled the site.

## After approval

Keep following the editorial policy. Mass-published, unedited AI articles can get ads limited or the account disabled after approval.
