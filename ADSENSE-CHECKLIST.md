# AdSense re-application checklist

This branch fixes the problems found in the "low value content" rejection. Some steps need the site owner and can't be automated. Work through them in order.

## Done on this branch

- [x] Rebranded the site to **Nexivo** so it matches the domain (nav, footer, titles, legal pages).
- [x] Moved 20 thin news rewrites from `content/posts/` to `archive/posts/`. They are no longer built or published. 8 more technical posts remain live.
- [x] Added a real author: byline linking to the About page, an author box on every post, and `Person` author structured data in place of "TechPulse" as an organisation.
- [x] Rewrote **About** and **Editorial Policy**: removed the "newly generated articles" / "earlier publishing workflow" wording and described a real review process.
- [x] Fixed the "January 1, 2025" dates on the About, Contact, Privacy, Terms and Disclaimer pages, and hid the date and reading time on those pages.
- [x] Updated the Disclaimer so it no longer describes an "AI-assisted editorial pipeline".
- [x] **Vulnerability Watch**: the weekly snapshot is now rendered into the HTML at build time (roughly 99 → 4,000+ words visible to crawlers), plus a "how to read / how to use" guide.
- [x] Wrote three evergreen guides as **drafts** (not published):
  - `content/posts/cvss-scores-explained.md`
  - `content/posts/build-free-cve-tracker-nvd-api.md`
  - `content/posts/hugo-vercel-pin-version-build-script.md`

## Owner to-do (needed for approval)

1. ~~Confirm your name~~ Done: "Jaiswar Abhishek".
2. ~~Finish the About page~~ Done. Optional: add a photo of yourself to `content/about.md`.
3. **Finish the three drafts.** Each one has a checklist comment at the top. Add your own screenshots and experience, then set `draft: false` and `review_status: approved`. Do not publish them unchanged.
4. **Review the 8 remaining news posts.** Check the facts against the linked sources, add a paragraph of your own analysis to each, and move any you can't stand behind to `archive/posts/`.
5. **Write 10–15 more evergreen posts** in the same style: guides, explainers, things you built or tested. Aim for about 20–25 good posts in total.
6. **Publish steadily** (2–3 posts a week) for 4–8 weeks. Don't publish a batch all on one day.
7. **Set up consent management** in AdSense (Privacy & messaging → European regulations → create a GDPR message). It is required to serve ads in the EEA, UK and Switzerland.
8. **Search Console:** verify the site, submit `sitemap.xml`, and use "Removals" or let the archived URLs return 404.
9. **Re-apply** only after steps 1–8.

## After approval

Keep following the editorial policy. Mass-published, unedited AI articles can get ads limited or the AdSense account disabled after approval, and can also hurt search rankings.
