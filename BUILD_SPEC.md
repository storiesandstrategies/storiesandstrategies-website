# Site Rebuild — Build Spec

Source: Doug Downs' Claude Code session "iPhone responsiveness and design"
(claude.ai, account "Doug Downs Stories and Strategies Pro"). The previous
session's built page was lost in a workspace reset; this is a rebuild from
the locked-in decisions recorded there.

## Goal
Rebuild storiesandstrategies.ca as a mobile-first, responsive, good-looking
single HTML page (`stories-and-strategies.html`) that Doug can preview on his
iPhone. This is a PREVIEW ONLY — never deploy to or modify the live site.

## Guardrails
- Do NOT touch https://storiesandstrategies.ca (no writes, no deploys).
- Work happens in this directory only; it will be pushed to a GitHub backup
  repo afterwards.
- Reading the public live site (images, content) is allowed and encouraged.

## Locked-in decisions (from the prior session)
1. Logo: proper high-resolution Stories & Strategies logo, sourced from the
   existing live site.
2. Branding: primary colour #3687B4 (navy blue) throughout; orange reserved
   for call-to-action buttons.
3. Team section order: Doug Downs → Emily Page → Jocelyn Floralde → Filip → Neal.
   5 team member profiles with photos and bios.
4. Podcast integration: episode/show artwork with a play button overlay; both
   the button and the artwork link to the Linkfire page https://lnkfi.re/nA25kt.
5. Mobile-first design: tap-to-open menu, swipeable testimonials, grid of
   client show covers, rotating headline ("brands / corporations / people /
   leaders"), animated audio waveform; no horizontal scroll at iPhone width
   (390px); images loaded from the existing website.
6. Content integrated: company stats, team bios, all 8 testimonials,
   contact info.

## Open items (use placeholders, clearly marked)
- Services section (Create, Grow, Advertise, Coaching): placeholder
  descriptions for now; Doug will supply real copy later. Mark each block
  visibly as placeholder in an HTML comment.
- Client show count: use "18+ client shows on air" (unverified, inferred).
- Contact form: preview-only, no backend. Add an HTML comment noting a
  developer must wire it to a backend before any real use.

## Deliverables
- `stories-and-strategies.html`: single self-contained page (inline CSS/JS
  preferred; hotlink images from the live site where the prior session did).
- `README.md`: what this is, the placeholder list, and the guardrail that
  this is a preview build, not the live site.
