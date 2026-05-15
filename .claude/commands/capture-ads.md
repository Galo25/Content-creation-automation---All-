# /capture-ads — Convert HTML Ads to PNG Images

Converts one or all HTML ad files to high-resolution PNG images using
**html-to-image** (bubkoo/html-to-image) running inside Playwright/Chromium.

Output is 2× pixel ratio (1200×1200px from a 600×600 viewport) for
crisp display and retina screens.

## Usage

```
/capture-ads                         # convert all ads/  HTML files
/capture-ads ads/ad-01-*.html        # convert a specific file
/capture-ads ads/ --width 300 --height 250   # custom size (e.g. 300×250 banner)
```

## What to do when invoked

1. Identify which HTML file(s) the user wants to convert:
   - No argument → all `*.html` files under `ads/`
   - Specific file(s) → those files only

2. Run the conversion tool:
   ```bash
   python3 tools/html_to_image.py <input> --outdir ads/images/
   ```
   Or for a single file with custom output:
   ```bash
   python3 tools/html_to_image.py <file.html> --out ads/images/<name>.png --width 600 --height 600
   ```

3. After conversion, **Read each output PNG** and display it inline in the
   chat so the user can review the creative immediately.

4. Report: file name, size in KB, and path for each image created.

5. If the user approves, commit and push the images:
   ```bash
   git add ads/images/ && git commit -m "Add rendered PNG ad images" && git push
   ```

## Options

| Flag | Default | Description |
|---|---|---|
| `--width` | 600 | Viewport width in px |
| `--height` | 600 | Viewport height in px |
| `--out` | same name as input | Output PNG path (single file) |
| `--outdir` | same dir as input | Output directory (folder input) |

## Requirements (pre-installed)
- `html-to-image` npm package — `node_modules/html-to-image/`
- Playwright Chromium — `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`
- Python 3 + `playwright` package
