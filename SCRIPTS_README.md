# Download Scripts

Two companion scripts for bulk-downloading videos from **Google Drive** and **Loom**. Both share the same simple, comma-separated URL-file format so you can keep all your video links in one place or split them by source.

---

## Table of Contents

- [Shared URL File Format](#shared-url-file-format)
- [download\_gdrive\_generic.py — Google Drive Downloader](#download_gdrive_genericpy--google-drive-downloader)
- [download\_loom\_generic.sh — Loom Downloader](#download_loom_genericsh--loom-downloader)
- [Output Structure](#output-structure)

---

## Shared URL File Format

Both scripts read from a plain-text file where each line describes one video:

```
# Comments and blank lines are ignored
# group, name, video_num, url_or_file_id
Neural-Forge, Andrés Renaud,  1, 1GC2Tr_y7rKq1tgy09yLjRMSZCEEmcM5J
Neural-Forge, Cynthia Omovoiye, 1, https://www.loom.com/share/4aeeaaa751bf4ac49a0285fd888687e4
```

| Field | Description |
|-------|-------------|
| `group` | Top-level folder name for the downloaded file |
| `name` | Person / series name (spaces become underscores) |
| `video_num` | Video number within the series |
| `url_or_file_id` | Full URL **or** bare Google Drive file ID (gdrive script only) |

Lines that don't have exactly four comma-separated fields are skipped with a warning.

---

## `download_gdrive_generic.py` — Google Drive Downloader

Downloads videos from Google Drive by automating a real Chromium browser via **Playwright**. Because it uses a real browser session you can log in normally, which bypasses most anti-bot and large-file confirmation screens.

### Requirements

```bash
pip install playwright
playwright install chromium
```

> **Python ≥ 3.12** is required (as set in `pyproject.toml`).

### Usage

```bash
# Uses defaults: gdrive_urls.txt → current directory
python download_gdrive_generic.py

# Custom URL file
python download_gdrive_generic.py --urls my_urls.txt

# Custom output directory
python download_gdrive_generic.py --dest /path/to/output

# Both custom
python download_gdrive_generic.py --urls my_urls.txt --dest /path/to/output
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--urls` | `gdrive_urls.txt` | Path to the URL list file |
| `--dest` | `.` (current dir) | Base output directory |

### How It Works

1. Launches a **visible** Chromium window (non-headless so Google doesn't flag it as a bot).
2. Opens `accounts.google.com` and **pauses** — you log in manually.
3. After you press **Enter** in the terminal, the script iterates over every entry and downloads each file.
4. Already-downloaded files are **skipped** automatically (idempotent).
5. Large files that trigger Google's "virus scan" warning are handled automatically.
6. A 2-second delay is added between requests to be polite to Google's servers.
7. Any failures are collected and reported as a summary at the end.

### URL File

Default filename: **`gdrive_urls.txt`**

The 4th field accepts either a **bare file ID** or a **full Drive URL**:

```
# Both formats are valid
Neural-Forge, Alice, 1, 1GC2Tr_y7rKq1tgy09yLjRMSZCEEmcM5J
Neural-Forge, Bob,   2, https://drive.google.com/file/d/1-IFXsqgQatEVF9Ufydcfpc7bMPTJq4Ad/view
```

---

## `download_loom_generic.sh` — Loom Downloader

Downloads Loom videos in bulk using **yt-dlp** — no browser required, no login needed for public Loom links.

### Requirements

```bash
# Either:
pip install yt-dlp
# Or:
brew install yt-dlp
```

### Usage

```bash
# Uses defaults: loom_urls.txt → current directory
bash download_loom_generic.sh

# Custom URL file
bash download_loom_generic.sh my_loom_urls.txt

# Custom URL file + output directory
bash download_loom_generic.sh my_loom_urls.txt /path/to/output
```

### Arguments

| Position | Default | Description |
|----------|---------|-------------|
| `$1` | `loom_urls.txt` | Path to the URL list file |
| `$2` | `.` (current dir) | Base output directory |

### How It Works

1. Checks that `yt-dlp` is installed and the URL file exists.
2. Reads each line, trims whitespace, and skips comments/blank lines.
3. Calls `yt-dlp` for each entry, saving to `<dest>/<group>/<Name>_Video<N>.<ext>`.
4. Prints a ✅/⚠️ per entry and a summary at the end.

### URL File

Default filename: **`loom_urls.txt`**

```
# group, name, video_num, loom_share_url
Neural-Forge, Cynthia Omovoiye, 1, https://www.loom.com/share/4aeeaaa751bf4ac49a0285fd888687e4
```

---

## Output Structure

Both scripts produce the same directory layout:

```
<dest>/
└── <group>/
    ├── <Name>_Video1.mp4
    ├── <Name>_Video2.mp4
    └── ...
```

**Example** — with `dest = ./downloads` and a group named `Neural-Forge`:

```
downloads/
└── Neural-Forge/
    ├── Andr_s_Renaud_Video1.mp4
    ├── Andr_s_Renaud_Video2.mp4
    └── Cynthia_Omovoiye_Video1.mp4
```

> Special characters in names (spaces, accents, etc.) are replaced with underscores to keep filenames shell-safe.
