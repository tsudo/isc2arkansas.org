"""Static checks for site/. Exits non-zero on any failure.

- every local href/src in the HTML points at a file that exists
- every local target in _redirects exists
- security.txt has not expired and has more than 30 days left

Run from the repo root:  py -3.14 tools/check_site.py
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

SITE = Path(__file__).resolve().parent.parent / "site"
ATTR = re.compile(r'(?:href|src)="([^"]+)"|srcset="([^"]+)"')


def resolve(url: str) -> Path | None:
    """Map a site-absolute URL to a file under site/, or None if external."""
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or url.startswith(("mailto:", "#")):
        return None
    path = parts.path
    if not path.startswith("/"):
        return None
    target = SITE / path.lstrip("/")
    return target / "index.html" if path.endswith("/") else target


def check_html(errors: list[str]) -> None:
    for page in SITE.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        for m in ATTR.finditer(text):
            urls = [m.group(1)] if m.group(1) else [u.split()[0] for u in m.group(2).split(",")]
            for url in urls:
                target = resolve(url)
                if target is not None and not target.exists():
                    errors.append(f"{page.relative_to(SITE)}: missing {url}")


def check_redirects(errors: list[str]) -> None:
    for n, line in enumerate((SITE / "_redirects").read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 3:
            errors.append(f"_redirects:{n}: expected 3 fields, got {len(fields)}")
            continue
        target = resolve(fields[1])
        if target is not None and not target.exists():
            errors.append(f"_redirects:{n}: target {fields[1]} does not exist")


def check_security_txt(errors: list[str]) -> None:
    text = (SITE / ".well-known" / "security.txt").read_text(encoding="utf-8")
    m = re.search(r"^Expires:\s*(\S+)", text, re.M)
    if not m:
        errors.append("security.txt: no Expires field")
        return
    expires = datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
    if expires - datetime.now(timezone.utc) < timedelta(days=30):
        errors.append(f"security.txt: expires {m.group(1)}, renew it")


def main() -> None:
    errors: list[str] = []
    check_html(errors)
    check_redirects(errors)
    check_security_txt(errors)
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        sys.exit(1)
    print("check_site.py: all checks passed")


if __name__ == "__main__":
    main()
