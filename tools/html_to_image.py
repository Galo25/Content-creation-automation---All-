#!/usr/bin/env python3
"""
html_to_image.py — Convert HTML ad files to PNG using html-to-image + Playwright.

Usage:
  python3 tools/html_to_image.py ads/ad-01-medicare-overpaying.html
  python3 tools/html_to_image.py ads/ad-01-medicare-overpaying.html --out output.png --width 600 --height 600
  python3 tools/html_to_image.py ads/        # converts all HTML files in a folder
"""

import sys
import os
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROMIUM = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
REPO_ROOT = Path(__file__).parent.parent
HTML_TO_IMAGE_LIB = REPO_ROOT / 'node_modules' / 'html-to-image' / 'dist' / 'html-to-image.js'


def convert_file(html_path: Path, output_path: Path, width: int, height: int) -> Path:
    html_to_image_js = HTML_TO_IMAGE_LIB.read_text()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROMIUM,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--allow-file-access-from-files',
            ]
        )
        page = browser.new_page(viewport={'width': width, 'height': height})
        page.goto(f'file://{html_path.resolve()}')
        page.wait_for_load_state('networkidle', timeout=10000)

        # Inject html-to-image UMD bundle and attempt capture
        try:
            page.evaluate(html_to_image_js)
            data_url = page.evaluate(f"""
                () => {{
                    const node = document.querySelector('body > *:first-child') || document.body;
                    return htmlToImage.toPng(node, {{
                        width: {width},
                        height: {height},
                        pixelRatio: 2,
                        skipAutoScale: false,
                        fetchRequestInit: {{ mode: 'no-cors' }},
                    }});
                }}
            """)
            browser.close()
            import base64
            img_data = base64.b64decode(data_url.split(',', 1)[1])
        except Exception:
            # Fallback: use Playwright native screenshot (handles external images)
            print('  (html-to-image fallback → Playwright screenshot)')
            img_data = page.screenshot(
                clip={'x': 0, 'y': 0, 'width': width, 'height': height},
                scale='device',
            )
            browser.close()
    output_path.write_bytes(img_data)
    size_kb = len(img_data) // 1024
    print(f'  ✓  {output_path.name}  ({size_kb} KB)')
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Convert HTML ads to PNG using html-to-image')
    parser.add_argument('input', help='HTML file or folder containing HTML files')
    parser.add_argument('--out', '-o', help='Output PNG path (single file only)')
    parser.add_argument('--width', '-W', type=int, default=600, help='Viewport width (default: 600)')
    parser.add_argument('--height', '-H', type=int, default=600, help='Viewport height (default: 600)')
    parser.add_argument('--outdir', '-d', help='Output directory (for folder input)')
    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_dir():
        html_files = sorted(input_path.glob('*.html'))
        if not html_files:
            print(f'No HTML files found in {input_path}')
            sys.exit(1)
        out_dir = Path(args.outdir) if args.outdir else input_path
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f'Converting {len(html_files)} files → {out_dir}\n')
        for f in html_files:
            out = out_dir / f.with_suffix('.png').name
            try:
                convert_file(f, out, args.width, args.height)
            except Exception as e:
                print(f'  ✗  {f.name}: {e}')
    elif input_path.is_file():
        out = Path(args.out) if args.out else input_path.with_suffix('.png')
        print(f'Converting {input_path.name} → {out}\n')
        convert_file(input_path, out, args.width, args.height)
    else:
        print(f'Error: {input_path} not found')
        sys.exit(1)


if __name__ == '__main__':
    main()
