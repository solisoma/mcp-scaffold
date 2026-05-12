#!/bin/bash
# ============================================================
# Loom Video Bulk Downloader — Generic Edition
# Reads entries from a text file and downloads each video.
#
# Requires: yt-dlp  →  pip install yt-dlp  (or brew install yt-dlp)
#
# Usage:
#   bash download_loom_generic.sh
#   bash download_loom_generic.sh loom_urls.txt
#   bash download_loom_generic.sh loom_urls.txt /path/to/output
#
# URL file format (loom_urls.txt):
#   # Comments and blank lines are ignored
#   # group, name, video_num, url
#   Neural-Forge, Cynthia Omovoiye, 1, https://www.loom.com/share/4aeeaaa751bf4ac49a0285fd888687e4
# ============================================================

set -e

URL_FILE="${1:-loom_urls.txt}"
DEST="${2:-.}"

# ── Sanity checks ────────────────────────────────────────────
if ! command -v yt-dlp &>/dev/null; then
  echo "❌ yt-dlp not found. Install it with: pip install yt-dlp"
  exit 1
fi

if [[ ! -f "$URL_FILE" ]]; then
  echo "❌ URL file not found: $URL_FILE"
  exit 1
fi

# ── Download function ────────────────────────────────────────
download() {
  local group="$1"
  local name="$2"
  local video_num="$3"
  local url="$4"

  local folder="${DEST}/${group}"
  mkdir -p "$folder"

  local safe_name
  safe_name=$(echo "$name" | tr ' ' '_' | tr -cd '[:alnum:]_-')

  local output_template="${folder}/${safe_name}_Video${video_num}.%(ext)s"

  echo "⬇️  [$group] $name — Video $video_num"
  yt-dlp --quiet --no-warnings \
    -o "$output_template" \
    "$url" && echo "   ✅ Done" || echo "   ⚠️  Failed: $url"
}

# ── Main ─────────────────────────────────────────────────────
echo ""
echo "=============================="
echo "  Loom Video Bulk Downloader  "
echo "=============================="
echo "  Source : $URL_FILE"
echo "  Output : $DEST"
echo "=============================="
echo ""

entry_count=0
failed_count=0

while IFS= read -r raw_line || [[ -n "$raw_line" ]]; do
  # Strip leading/trailing whitespace
  line="${raw_line#"${raw_line%%[![:space:]]*}"}"
  line="${line%"${line##*[![:space:]]}"}"

  # Skip blank lines and comments
  [[ -z "$line" || "$line" == \#* ]] && continue

  # Split on commas (up to 4 fields: group, name, video_num, url)
  IFS=',' read -r group name video_num url <<< "$line"

  # Trim whitespace from each field
  group="${group#"${group%%[![:space:]]*}"}"; group="${group%"${group##*[![:space:]]}"}"
  name="${name#"${name%%[![:space:]]*}"}"; name="${name%"${name##*[![:space:]]}"}"
  video_num="${video_num#"${video_num%%[![:space:]]*}"}"; video_num="${video_num%"${video_num##*[![:space:]]}"}"
  url="${url#"${url%%[![:space:]]*}"}"; url="${url%"${url##*[![:space:]]}"}"

  if [[ -z "$group" || -z "$name" || -z "$video_num" || -z "$url" ]]; then
    echo "   ⚠️  Skipping malformed line: $line"
    continue
  fi

  download "$group" "$name" "$video_num" "$url" && ((entry_count++)) || ((failed_count++))

done < "$URL_FILE"

echo ""
echo "=============================="
if [[ "$failed_count" -gt 0 ]]; then
  echo "  ⚠️  $failed_count failed, $entry_count succeeded."
else
  echo "  ✅ All $entry_count download(s) complete!"
fi
echo "=============================="
echo ""
