# EduAdvise International — Landing Page

Marketing landing page for [EduAdvise International](https://eduadvise.in), study-abroad consultants in Margao, Goa.

**Design**: "Airmail / travel documents" concept — boarding-pass hero, departures-board university listing, postcard testimonials — in the brand's purple `#660066` / orange `#f76a0c` palette.

## Features

- 47 partner universities with photos, info cards and official links (`unis.js`, sourced from eduadvise.in + Wikipedia)
- Interactive 3D night-earth globe (Three.js) with animated flight routes out of Goa
- AOS scroll animations, mobile hamburger nav, tap-to-call/email contact card
- Static site — no build step. Open `index.html` or host the folder anywhere.

## Structure

- `index.html` — the whole site (styles + scripts inlined)
- `unis.js` — university dataset
- `img/` — university photos, logo, favicon
- `substance/` — Substance 3D Painter export pipeline for custom globe PBR textures (see its README)
- `fetch_unis.py` / `patch_unis.py` / `download_images.py` — data refresh scripts
