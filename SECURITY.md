# Security Policy

## Reporting a vulnerability

Report security issues with this site or repository privately. Either:

- use GitHub's **Report a vulnerability** button on the Security tab, or
- email [keith@keithcrawford.me](mailto:keith@keithcrawford.me). GPG key: [pages.keithcrawford.me/gpg-key](https://pages.keithcrawford.me/gpg-key) (Key ID `0xC4C53435`)

Please do not open a public issue for a security report.

## Scope

This is a static site served by Cloudflare Workers static assets. It has no forms, accounts, or server-side code. Reports are welcome for:

- Content Security Policy or security-header weaknesses (`site/_headers`)
- Open redirects in `site/_redirects`
- Secrets, credentials, or personal data committed to the repository
- DNS or email-authentication issues on `isc2arkansas.org`

Out of scope: theoretical issues with no exploit path, social engineering, and denial of service.

## Response

You'll get an acknowledgement within 48 hours. Fixes are prioritized by severity. Please allow reasonable time for a fix before disclosing publicly. If you'd like credit, say so in your report and it will appear in the fix commit.
