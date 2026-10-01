# Stories and Strategies — Mobile-First Preview Build

> **GUARDRAIL: This is a PREVIEW build. It must never be deployed to, uploaded
> to, or used to overwrite the live site at https://storiesandstrategies.ca.**
> The live site was only *read* (public content and image URLs) to build it.

## What this is
`stories-and-strategies.html` is a single, self-contained page (inline CSS and
JS, no build step) that rebuilds the storiesandstrategies.ca homepage as a
mobile-first, responsive design so Doug can preview it on his iPhone. Open it
directly in a browser. All images are stored locally in `images/` (resized
and compressed copies of the live-site files), so it needs no connection to
the live site.

It was rebuilt from the decisions in `BUILD_SPEC.md` after the earlier
session's page was lost.

## What's in it
- **Look:** dark navy header so the white logo reads; Oswald display type
  (echoing the logo's condensed lettering) with Source Sans 3 for body text.
- **Branding:** primary colour `#3687B4` throughout; orange (`#F7941D`) is
  used only for call-to-action buttons and the podcast play button.
- **Logo:** the Stories & Strategies logo from the live site, saved as
  `images/logo.png` (640px wide, transparent).
- **Header:** sticky, with a tap-to-open hamburger menu on mobile and inline
  links on desktop.
- **Hero:** rotating headline ("brands / corporations / people / leaders")
  and an animated audio waveform. Both respect `prefers-reduced-motion`.
- **Stats:** 18+ client shows on air, 40% listen monthly, 1 in 3 listen
  daily, #1 most listened-to PR podcast in the world.
- **About:** copy from the live site.
- **Services:** Create, Grow, Advertise, Coaching (copy approved by Doug).
- **Team:** in the order Doug Downs, Emily Page, Jocelyn Floralde, Filip
  Krstevski, Neal Matyas, with live-site photos and bios.
- **Podcast:** show artwork with a play-button overlay. The artwork and the
  "Listen now" button both link to https://lnkfi.re/nA25kt.
- **Client shows:** a grid of 18 client cover images (S&S's own show is
  featured in the podcast section instead), each linking to the same
  destination as on the live site.
- **Testimonials:** all 8, in a swipeable scroll-snap carousel with dot
  indicators.
- **Contact:** no form (removed at Doug's request). info@storiesandstrategies.ca
  is shown as a large clickable email link, plus the Calendly booking button
  and social links.
- **Responsive:** tuned for phone, tablet and desktop. Hero goes two-column
  from 1000px, services go four-across and team sits 3 + 2 from 1100px.
  Checked with no horizontal scroll at 390, 768, 1280 and 1600px.
- **Image fallbacks:** if an image fails to load, a branded tile replaces it
  (initials for people, "Client show" for covers, a wordmark for the logo).
- **Layout:** no horizontal scroll at 390px. Inputs use 16px text to prevent
  iOS zoom-on-focus. The page is marked `noindex`.

## Placeholders / open items
| Item | Status |
|---|---|
| "18+ client shows on air" | **Unverified.** Inferred from the cover grid on the live site, which shows 19 covers, one of them S&S's own show. |
| Team role titles | Taken from the live bios. Filip's and Neal's title ("Audio & Video Editor") set per Doug. |
| "#1 most listened-to PR podcast" | Taken from the show's own description (Podchaser, Goodpods and Rephonic data), not from the website. The live homepage has only two stats. |
| "1 in 3 listen daily" | Changed from the live site's "1 in 4" at Doug's request. |
| Podcast blurb | Short descriptive line written for the preview. Replace it with an official show description if one exists. |

## Sources (all read-only from the live site)
- Content: homepage text from https://storiesandstrategies.ca
- Images: downloaded once from `https://storiesandstrategies.ca/wp-content/uploads/...`
  and saved to `images/`, including
  the logo, the team photos (`2026/03/{Doug,Emily,Jocelyn,Filip,Neal}.jpg`),
  testimonial headshots, client cover art, the podcast artwork
  (`2026/02/Untitled-design-60*.png`), and the hero background
  (`2022/07/Mic-and-pop-screen-scaled-1.jpg`).
