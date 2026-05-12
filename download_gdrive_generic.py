"""
Google Drive Video Downloader — Generic Edition
================================================
Reads entries from a text file and downloads each file via Playwright.

Setup:
    pip install playwright
    playwright install chromium

Run:
    python download_gdrive_generic.py
    python download_gdrive_generic.py --urls my_urls.txt
    python download_gdrive_generic.py --dest /path/to/output

URL file format (gdrive_urls.txt):
    # Comments and blank lines are ignored
    # group, name, video_num, file_id_or_url
    Neural-Forge, Andrés Renaud, 1, 1GC2Tr_y7rKq1tgy09yLjRMSZCEEmcM5J
    Neural-Forge, Andrés Renaud, 2, https://drive.google.com/file/d/1-IFXsqgQatEVF9Ufydcfpc7bMPTJq4Ad/view
"""

import argparse
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright


def safe_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in name.replace(" ", "_"))


def extract_file_id(value: str) -> str:
    """Accept a bare file ID or a full Drive URL."""
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", value)
    return match.group(1) if match else value.strip()


def load_entries(url_file: Path) -> list[tuple[str, str, str, str]]:
    entries = []
    with url_file.open() as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",", 3)]
            if len(parts) != 4:
                print(f"   ⚠️  Line {lineno} skipped (expected 4 fields): {line!r}")
                continue
            group, name, video_num, id_or_url = parts
            entries.append((group, name, video_num, extract_file_id(id_or_url)))
    return entries


def run(url_file: Path, dest: Path) -> None:
    entries = load_entries(url_file)
    if not entries:
        print(f"No entries found in {url_file}. Exiting.")
        return

    print(f"\n   Loaded {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} from {url_file}")
    failed = []

    with sync_playwright() as p:
        print("   Launching browser...")
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )
        context = browser.new_context(
            accept_downloads=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
            viewport={"width": 1280, "height": 800},
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()
        print("   ✅ Browser launched.")

        print("\n   Navigating to Google login...")
        page.goto("https://accounts.google.com", wait_until="domcontentloaded")
        print("\n" + "=" * 50)
        print("  👉  Log in to your Google account in the browser.")
        print("      Once logged in and you can see Google Drive,")
        print("      come back here and press ENTER.")
        print("=" * 50)
        input("\n  [Press ENTER when logged in] ")
        print("\n✅  Starting downloads...\n")

        current_group = None
        for group, name, video_num, file_id in entries:
            if group != current_group:
                current_group = group
                print(f"\n── {group} ──\n")

            folder = dest / group
            folder.mkdir(parents=True, exist_ok=True)
            output_path = folder / f"{safe_name(name)}_Video{video_num}.mp4"

            if output_path.exists():
                print(f"   ⏭️  Skipping: {output_path.name}")
                continue

            print(f"⬇️  {name} — Video {video_num} ... ", end="", flush=True)
            view_url = f"https://drive.google.com/file/d/{file_id}/view"

            try:
                page.goto(view_url, wait_until="domcontentloaded", timeout=30_000)
                print("page loaded ... ", end="", flush=True)

                download_btn = page.locator(
                    "button[aria-label='Download'], "
                    "button[aria-label='Download file'], "
                    "[data-tooltip='Download'], "
                    "[aria-label='More actions'] "
                )
                download_btn.first.wait_for(timeout=10_000)
                print("clicking ... ", end="", flush=True)

                try:
                    with context.expect_page(timeout=6_000) as new_page_info:
                        download_btn.first.click()
                    warning_page = new_page_info.value
                    warning_page.wait_for_load_state("domcontentloaded")
                    print("confirming large file ... ", end="", flush=True)

                    with warning_page.expect_download(timeout=180_000) as dl_info:
                        warning_page.locator(
                            "a:has-text('Download anyway'), "
                            "a:has-text('download anyway'), "
                            "#uc-download-link"
                        ).first.click()

                    download = dl_info.value
                    print("saving ... ", end="", flush=True)
                    download.save_as(output_path)
                    warning_page.close()

                except Exception:
                    with page.expect_download(timeout=180_000) as dl_info:
                        download_btn.first.click()
                    download = dl_info.value
                    print("saving ... ", end="", flush=True)
                    download.save_as(output_path)

                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"✅  {output_path.name} ({size_mb:.1f} MB)")

            except Exception as e:
                print(f"\n   ⚠️  Failed: {e}")
                failed.append((group, name, video_num, file_id))

            time.sleep(2)

        browser.close()

    print("\n" + "=" * 50)
    if failed:
        print(f"\n⚠️  {len(failed)} download(s) failed:\n")
        for group, name, vid, fid in failed:
            print(f"   [{group}] {name} — Video {vid}")
            print(f"   https://drive.google.com/file/d/{fid}/view\n")
    else:
        print("\n✅  All downloads complete!")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Google Drive videos listed in a text file.")
    parser.add_argument("--urls", default="gdrive_urls.txt", help="Path to the URL list file (default: gdrive_urls.txt)")
    parser.add_argument("--dest", default=".", help="Base output directory (default: current directory)")
    args = parser.parse_args()

    run(Path(args.urls), Path(args.dest))
