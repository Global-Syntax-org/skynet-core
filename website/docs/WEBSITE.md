Website and GitHub Pages

This project includes a small static marketing site in `website/` meant for GitHub Pages deployment.

Contents
- `website/index.html` — landing page
- `website/pricing.html` — pricing and CTA
- `website/style.css` — simple stylesheet

Deployment
- A GitHub Actions workflow at `.github/workflows/gh-pages.yml` deploys `website/` to GitHub Pages on push to `main`.
- The Pages workflow uses the official `actions/setup-pages` and `actions/deploy-pages` actions.

Local testing
- You can preview the site locally with any static server, for example:

```bash
python3 -m http.server --directory website 8000
# then open http://localhost:8000
```

Customization
- Update HTML/CSS in `website/` and push to `main` to redeploy.
- For a production marketing site, replace placeholder emails and links (sales@stuxnetstudios.example) with your real contact endpoints.
