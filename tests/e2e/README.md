# Portfolio browser tests

These Playwright tests exercise the actual static site over HTTP, using its
served CSS and minified JavaScript. Both desktop Chrome and a mobile Chromium
viewport run the same scenarios. This is mobile emulation, not a real phone.

## Run locally

Install Node.js 22 and Python 3, then run from the repository root:

```sh
npm ci --prefix tests/e2e
cd tests/e2e
npx playwright install chromium
cd ../..
npm run test:e2e
```

Playwright starts and stops a local server at http://127.0.0.1:4173. Keep that
port free. The test package is separate because the original Gulp tooling uses
legacy node-sass; browser tests do not need that build toolchain installed.

```sh
npm run test:e2e:ui
npm run test:e2e:report
npm run test:e2e -- --project=mobile-chromium
```

## GitHub Actions

`.github/workflows/playwright.yml` runs on pushes, pull requests, and manual
dispatch. GitHub checks out the commit, installs the test package and Chromium,
serves that checkout, runs tests, and uploads an HTML report plus failure
screenshots, videos, and traces. Open the repository's **Actions** tab, select a
**Playwright Tests** run, and download **playwright-results** under Artifacts.
Extract the archive and use `npx playwright show-report /path/to/playwright-report`
from this directory to inspect it.

The suite covers local assets, section navigation, mobile menu closing, contact
destinations, and video embed configuration. It does not send email, open social
accounts, or verify YouTube playback. jQuery currently loads from the site's real
Google CDN, so network availability can affect navigation tests.

This workflow tests the checked-out site; it does not deploy GitHub Pages or
automatically make passing tests a requirement for deployment. Push these files
to enable it. Configure branch protection/rulesets separately if merges should
require the `test` job to pass.

To grow coverage, add independent `*.spec.js` files under `specs`. Add browsers
or parallel jobs when the suite needs them. No production secrets or database
are required for this static site.
