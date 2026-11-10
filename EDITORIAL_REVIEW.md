# TechPulse editorial review checklist

New AI-assisted articles are saved as unpublished Hugo drafts. They are not eligible for the public site or social distribution until a human editor completes this review.

## Review every draft

1. Open every URL in the article's Sources section. Confirm that the page exists and actually supports the specific claims attributed to it.
2. Prefer primary sources: official company announcements, product documentation, regulatory filings, research papers, court documents, and government publications.
3. Cross-check names, dates, prices, statistics, quotes, product availability, and technical specifications. Remove any claim that cannot be verified.
4. Add original explanation: how the technology works, who benefits, practical limitations, trade-offs, and what readers should do with the information.
5. Check that the headline and description accurately represent the article. Do not exaggerate or imply certainty the sources do not support.
6. Confirm that the cover image is relevant and does not misrepresent a real person, product, or event.
7. Correct grammar, broken links, duplicate coverage, and unsupported conclusions.

A generated source list is a starting point, not proof. A reachable URL does not establish that its content supports the article.

## Approve and publish

Only after the checks above are complete, update the article front matter:

    draft: false
    review_status: "approved"

Commit the approved article to main. The Vercel build will publish it, and the marketing workflow can then distribute it. Do not change draft to false while review_status is needs-review.

## Editorial rule

AI may assist with research organization, drafting, and editing. It is not a source of facts and must never invent sources, quotes, statistics, or events. If the evidence is insufficient, do not publish the story.
