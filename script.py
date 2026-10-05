import asyncio
import os
from urllib.parse import urljoin, urlparse, unquote

import aiohttp
from playwright.async_api import async_playwright


START_URL = "https://www.prosetmodular.com/"
OUTPUT_DIR = "media"


async def scrape_page(page, url):
    await page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=60000
    )

    # Give lazy-loaded content a chance to appear
    await page.evaluate("""
        async () => {
            window.scrollTo(0, document.body.scrollHeight);
            await new Promise(resolve => setTimeout(resolve, 2000));
            window.scrollTo(0, 0);
        }
    """)

    media_urls = set()

    # Images
    image_urls = await page.locator("img").evaluate_all("""
        imgs => imgs.flatMap(img => [
            img.src,
            img.currentSrc,
            img.getAttribute("data-src"),
            img.getAttribute("data-lazy-src"),
            img.getAttribute("data-original")
        ]).filter(Boolean)
    """)

    for src in image_urls:
        media_urls.add(urljoin(url, src))

    # Videos
    video_urls = await page.locator("video, video source").evaluate_all("""
        els => els.flatMap(el => [
            el.src,
            el.getAttribute("src"),
            el.getAttribute("data-src")
        ]).filter(Boolean)
    """)

    for src in video_urls:
        media_urls.add(urljoin(url, src))

    # Audio
    audio_urls = await page.locator("audio, audio source").evaluate_all("""
        els => els.flatMap(el => [
            el.src,
            el.getAttribute("src"),
            el.getAttribute("data-src")
        ]).filter(Boolean)
    """)

    for src in audio_urls:
        media_urls.add(urljoin(url, src))

    return media_urls


def get_filename(url):
    path = urlparse(url).path
    filename = unquote(os.path.basename(path))

    if not filename:
        return None

    return filename


async def download_media(media_urls):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timeout = aiohttp.ClientTimeout(total=300)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/154.0.0.0 Safari/537.36"
        )
    }

    async with aiohttp.ClientSession(
        timeout=timeout,
        headers=headers
    ) as session:

        for index, url in enumerate(sorted(media_urls), start=1):

            filename = get_filename(url)

            if not filename:
                print(f"Skipping: {url}")
                continue

            filepath = os.path.join(OUTPUT_DIR, filename)

            # Avoid overwriting files with the same name
            if os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                counter = 1

                while os.path.exists(filepath):
                    filepath = os.path.join(
                        OUTPUT_DIR,
                        f"{name}_{counter}{ext}"
                    )
                    counter += 1

            try:
                print(f"[{index}/{len(media_urls)}] Downloading:")
                print(f"  {url}")

                async with session.get(url) as response:

                    if response.status != 200:
                        print(
                            f"  FAILED - HTTP {response.status}"
                        )
                        continue

                    with open(filepath, "wb") as file:

                        while True:
                            chunk = await response.content.read(
                                1024 * 64
                            )

                            if not chunk:
                                break

                            file.write(chunk)

                size = os.path.getsize(filepath)

                print(
                    f"  ✓ Saved: {filepath} "
                    f"({size / 1024:.1f} KB)"
                )

            except Exception as e:
                print(f"  ✗ Failed: {e}")


async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch()

        page = await browser.new_page()

        print(f"Scraping: {START_URL}")
        print()

        media = await scrape_page(page, START_URL)

        print(f"Found {len(media)} media files")
        print()

        await browser.close()

    # Download everything
    await download_media(media)

    print()
    print("================================")
    print("Download complete!")
    print(f"Files saved in: {OUTPUT_DIR}/")
    print("================================")


if __name__ == "__main__":
    asyncio.run(main())