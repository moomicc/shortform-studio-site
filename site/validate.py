"""Guard public download/help copy against broken links and unsupported claims."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
HTML_FILE = ROOT / "index.html"


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.anchors: list[str] = []
        self.local_assets: list[str] = []
        self.external_assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            if element_id in self.ids:
                raise ValueError(f"중복 id: {element_id}")
            self.ids.add(element_id)
        if tag == "a":
            href = values.get("href", "") or ""
            if href.startswith("#"):
                self.anchors.append(href[1:])
        if tag == "link" and values.get("rel") == "stylesheet":
            href = values.get("href", "") or ""
            (self.external_assets if urlparse(href).scheme else self.local_assets).append(href)
        if tag == "script" and values.get("src"):
            src = values["src"] or ""
            (self.external_assets if urlparse(src).scheme else self.local_assets).append(src)


def validate() -> list[str]:
    html = HTML_FILE.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)
    parser.close()
    errors: list[str] = []
    missing_anchors = sorted(set(parser.anchors) - parser.ids)
    if missing_anchors:
        errors.append(f"존재하지 않는 내부 앵커: {', '.join(missing_anchors)}")
    missing_assets = [asset for asset in parser.local_assets if not (ROOT / asset).is_file()]
    if missing_assets:
        errors.append(f"찾을 수 없는 로컬 리소스: {', '.join(missing_assets)}")
    if parser.external_assets:
        errors.append(f"외부 CSS/JS 리소스는 허용하지 않습니다: {', '.join(parser.external_assets)}")
    css_path = ROOT / "styles.css"
    if css_path.is_file() and re.search(r"@import\s+url\(['\"]?https?://", css_path.read_text(encoding="utf-8"), flags=re.IGNORECASE):
        errors.append("스타일시트의 외부 폰트/CDN 요청은 허용하지 않습니다.")
    required_disclosures = (
        "공식 설치 파일은 공개되지 않았습니다",
        "정식 배포 준비 중",
        "일부 프레임과 분석 텍스트",
        "요금이 발생할 수 있습니다",
    )
    for disclosure in required_disclosures:
        if disclosure not in html:
            errors.append(f"필수 공개 안내 누락: {disclosure}")
    if re.search(r"OPENAI_API_KEY\s*=", html):
        errors.append("API 키 설정 문자열이 사이트 콘텐츠에 포함되어 있습니다.")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        raise SystemExit(1)
    print("Static site checks passed: disclosures, anchors, local assets, and no external code/font requests.")
