# isc2arkansas.org

The static site for the ISC2 Arkansas chapter. It is plain HTML and CSS, with no build step. Cloudflare Workers (static assets) serves the `site/` folder as-is; `wrangler.jsonc` holds the config.

## Edit content

Edit `site/index.html` or `site/privacy/index.html`, then push to `main`. Workers Builds deploys on push.

## Change the photos

1. Edit `tools/photos.json`. Each pick is a number from the source set, with a caption and alt text. Alt text describes the scene and never names people.
2. Run `py -3.14 tools/photos.py` from the repo root. The script resizes the photos, strips their metadata, writes them to `site/img/photos/`, and rewrites the photo grid in `index.html`.

Add `--review` to rebuild `site/photo-review/`, a numbered page showing every source photo. That folder is for choosing picks; delete it before the site goes live on the custom domain.

## Preview locally

```bash
py -3.14 -m http.server 8125 --directory site
```

The local server ignores `_redirects` and `_headers`. Check those on the `workers.dev` deploy.

## Checks

`py -3.14 tools/check_site.py` confirms that every local link, image, and redirect target exists, and that `security.txt` has more than 30 days left before it expires. GitHub Actions runs the same check on every push and once a month.

## Files

- `site/_redirects` maps old WordPress URLs to their new locations.
- `site/_headers` sets the security headers and CSP.
- `site/.well-known/security.txt` expires 2027-09-24. Renew it before then.

## License

The code, HTML, and CSS are licensed under [CC BY 4.0](LICENSE).

That license does not cover:

- event photos in `site/img/photos/` and `site/photo-review/`, which belong to the chapter and its members;
- the ISC2 documents in `site/docs/`, which belong to ISC2, Inc. and the chapter;
- the ISC2 name, logo, and chapter seal, which are ISC2 trademarks used under ISC2's chapter guidelines.

The Inter font is licensed under the SIL Open Font License 1.1.
