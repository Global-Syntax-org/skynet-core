Skynet Core Website

This directory contains a small static marketing site intended to live in the repository alongside the project source.

Goals
- Keep the website modular and self-contained under `website/` so we can extract it into a separate repo later.
- Provide a minimal, easy-to-edit HTML/CSS preview that can be deployed via GitHub Pages.

Moving to a new project later
1. Create a new repository (e.g. `skynet-core-website`).
2. In the new repo, create a `website/` directory and copy the files from this project.
3. Update CI/deploy workflows to publish from the new repo.

Local preview
- Run:

```bash
python3 -m http.server --directory website 8000
```

Deployment
- This repo contains `.github/workflows/gh-pages.yml` which deploys `website/` to GitHub Pages on push to `main`.
