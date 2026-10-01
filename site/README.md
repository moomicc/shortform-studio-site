# Shortform Studio download site

This directory is a static Korean landing/download/help page. It never contains application user data, API keys, videos, renders, BGM, fonts, or CapCut project templates. To keep the application source private while using the free GitHub Pages tier, publish only this directory from a separate public `moomicc/shortform-studio-site` repository.

The site intentionally points visitors to the site-only repository's GitHub Releases page instead of inventing direct package links. It reports the verified native CI package smoke scope accurately while stating that clean-machine setup, FFmpeg packaging, signing/notarization, and CapCut validation remain open. It explicitly says no official installer has been released yet.

The separate site's `.github/workflows/publish-site.yml` deploys on updates to its main branch and supports manual dispatch. GitHub Pages on the free plan requires a public repository, so the app's private source repository must not be the Pages source. The deployment repository contains only this static site. GitHub Pages processes visitor connection metadata such as IP addresses; the page discloses this.

Before announcing downloads, publish only signed/versioned release assets that passed clean-machine OS tests. Do not link temporary package-smoke CI artifacts as installers.
