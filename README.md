# Extract Media From Website

A Python utility that uses **Playwright** and **aiohttp** to discover and download media files from a live website.

The current script extracts:

- Images (`<img>`)
- Lazy-loaded images
- Videos (`<video>`, `<source>`)
- Audio (`<audio>`, `<source>`)

Downloaded files are saved locally in the `media/` directory.

## Project Structure

```text
extract-media-from-website/
├── .gitignore
├── README.md
├── requirements.txt
├── script.py
└── media/
    └── .gitkeep
```

The downloaded media and Python virtual environment are intentionally excluded from Git.

## Requirements

- Python 3.9+
- Playwright
- aiohttp

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd extract-media-from-website
```

### 2. Create a virtual environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browser

```bash
playwright install chromium
```

## Usage

Update `START_URL` in `script.py`:

```python
START_URL = "https://www.prosetmodular.com/"
```

Then run:

```bash
python script.py
```

The script will:

1. Open the target website using Chromium.
2. Wait for the page DOM to load.
3. Scroll the page to trigger lazy-loaded content.
4. Discover media URLs.
5. Download the discovered media.
6. Save the files under:

```text
media/
```

Example output:

```text
Scraping: https://www.prosetmodular.com/

Found 10 media files

[1/10] Downloading:
  https://www.prosetmodular.com/.../markets-icon.png
  ✓ Saved: media/markets-icon.png

...

================================
Download complete!
Files saved in: media/
================================
```

## Git Setup

The repository ignores:

- `.venv/`
- downloaded files inside `media/`
- Python cache files
- OS files such as `.DS_Store`
- IDE configuration

The `media/.gitkeep` file can be committed so the output directory exists after cloning.

Initialize Git:

```bash
git init
git add .
git commit -m "Initial commit"
```

Check what will be committed:

```bash
git status
```

Downloaded media should **not** appear as files to commit.

## Current Limitations

The current implementation processes the configured `START_URL` page only.

It does not yet recursively crawl every internal page on the website.

Future improvements could include:

- Recursive internal-page crawling
- CSS background-image extraction
- `srcset` / responsive image extraction
- Open Graph image extraction
- Better duplicate detection
- Separate image/video/audio directories
- Command-line URL arguments
- Concurrent downloads
- Download progress reporting
- Sitemap-based crawling

## License

Add the license appropriate for your project before publishing publicly.

## Disclaimer

Only download and use media that you have permission to access and reuse. Respect website terms, copyright, robots policies, and applicable laws.
