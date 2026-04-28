import sys
import yt_dlp



class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    GREEN  = "\033[92m"
    CYAN   = "\033[96m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    WHITE  = "\033[97m"

def c(color: str, text: str, bold: bool = False) -> str:
    b = C.BOLD if bold else ""
    return f"{b}{color}{text}{C.RESET}"



BANNER = f"""
{c(C.GREEN, '╔══════════════════════════════════════╗', bold=True)}
{c(C.GREEN, '║   ', bold=True)}{c(C.CYAN, 'YouTube Downloader', bold=True)}  {c(C.DIM, 'by VanTue')}{c(C.GREEN, '     ║', bold=True)}
{c(C.GREEN, '║   ', bold=True)}{c(C.DIM,  'video & playlist · multi-resolution')}{c(C.GREEN, '  ║', bold=True)}
{c(C.GREEN, '╚══════════════════════════════════════╝', bold=True)}
"""

def print_box(title: str, items: list[tuple[str, str]]) -> None:
    """Vẽ menu dạng box với màu sắc."""
    width = 37
    print(c(C.CYAN, f"┌─ {title} {'─' * (width - len(title) - 3)}┐"))
    for key, label in items:
        key_color = C.RED if key == "0" else C.DIM
        line = f"  {c(key_color, f'[{key}]')} {c(C.WHITE, label)}"
        # Tính độ dài thực (bỏ escape codes)
        visible_len = len(f"  [{key}] {label}")
        pad = width - visible_len - 1
        print(c(C.CYAN, "│") + line + " " * pad + c(C.CYAN, "│"))
    print(c(C.CYAN, f"└{'─' * (width + 1)}┘"))

def prompt(text: str) -> str:
    return input(f"{C.DIM}» {C.RESET}{c(C.WHITE, text)}")



RESOLUTION_OPTIONS: dict[str, int] = {
    "1": 360,
    "2": 480,
    "3": 720,
    "4": 1080,
    "5": 1440,
    "6": 2160,
}

RESOLUTION_LABELS: dict[str, str] = {
    "1": "360p",
    "2": "480p",
    "3": "720p",
    "4": f"1080p {C.DIM}(Full HD){C.RESET}",
    "5": f"1440p {C.DIM}(2K){C.RESET}",
    "6": f"2160p {C.DIM}(4K){C.RESET}",
    "7": "Tùy chỉnh",
    "0": f"{C.DIM}Thoát{C.RESET}",
}

DEFAULT_HEIGHT = 1080
BAR_WIDTH      = 25



def draw_progress(percent_str: str, speed: str, eta: str) -> None:
    try:
        pct = float(percent_str.strip().replace("%", "").replace(" ", ""))
    except:
        pct = 0.0

    filled = int(BAR_WIDTH * pct / 100)
    bar = c(C.GREEN, "█" * filled) + c(C.DIM, "░" * (BAR_WIDTH - filled))
    pct_label = c(C.WHITE, f"{pct:6.1f}%", bold=True)

    print(
        f"\033[2K\r  {c(C.DIM, 'Tiến độ:')} {bar} {pct_label}"
        f"   {c(C.DIM, 'Tốc độ:')} {c(C.GREEN, speed)}"
        f"   {c(C.DIM, 'Còn lại:')} {c(C.YELLOW, eta)}",
        end=""
    )


def list_resolutions() -> int | None:
    print()
    print_box("Chọn độ phân giải", list(RESOLUTION_LABELS.items()))
    choice = prompt("\nLựa chọn (0-7): ").strip()

    if choice == "0":
        return None
    if choice in RESOLUTION_OPTIONS:
        return RESOLUTION_OPTIONS[choice]
    if choice == "7":
        try:
            return int(prompt("Nhập chiều cao tối đa (vd: 720): "))
        except ValueError:
            print(c(C.YELLOW, f"⚠ Giá trị không hợp lệ, dùng mặc định {DEFAULT_HEIGHT}p."))
            return DEFAULT_HEIGHT

    print(c(C.YELLOW, f"⚠ Lựa chọn không hợp lệ, dùng mặc định {DEFAULT_HEIGHT}p."))
    return DEFAULT_HEIGHT


def my_hook(d: dict) -> None:
    if d["status"] == "downloading":
        percent_str = d.get("_percent_str") or "0%"
        speed = d.get("_speed_str", "N/A")
        eta = d.get("_eta_str", "N/A")

        if d.get("total_bytes") and d.get("downloaded_bytes"):
            try:
                pct = (d["downloaded_bytes"] / d["total_bytes"]) * 100
                percent_str = f"{pct:.1f}%"
            except:
                pass

        draw_progress(percent_str, speed, eta)

    elif d["status"] == "finished":
        print("\033[2K\r" + c(C.DIM, "  ✅ Ghép file video + audio..."))
    elif d.get("status") == "error":
        print("\n" + c(C.RED, f"  ❌ Lỗi: {d.get('error', 'Unknown')}"))


def build_ydl_opts(max_height: int, is_playlist: bool) -> dict:
    return {
        "format": f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]",
        "merge_output_format": "mp4",
        "outtmpl": "%(title)s [%(id)s].%(ext)s",
        "progress_hooks": [my_hook],
        "quiet": False,
        "no_warnings": True,
        "noprogress": False,
        "progress_with_newline": False,
        "noplaylist": not is_playlist,
    }


def download_video(url: str, max_height: int = DEFAULT_HEIGHT, is_playlist: bool = False) -> None:
    print(f"\n{c(C.CYAN, '▶ Đang xử lý:')} {c(C.DIM, url)}")
    ydl_opts = build_ydl_opts(max_height, is_playlist)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", url)
            print(f"  {c(C.DIM, 'Tiêu đề:')} {c(C.WHITE, title)}\n")
            ydl.download([url])
        print("\n" + c(C.GREEN, "✔ Hoàn tất! ", bold=True) + c(C.DIM, f"{title}.mp4"))
    except Exception as e:
        print("\n" + c(C.RED, f"✘ Lỗi: {e}"))


def collect_urls(mode: str) -> list[str]:
    if mode in ("1", "3"):
        label = "video" if mode == "1" else "playlist"
        url = prompt(f"Link YouTube ({label}): ").strip()
        return [url] if url else []
    if mode == "2":
        print(c(C.DIM, "Nhập link (mỗi dòng 1 link, dòng trống để kết thúc):"))
        urls = []
        while True:
            line = input(f"  {C.BLUE}→{C.RESET} ").strip()
            if not line:
                break
            urls.append(line)
        return urls
    return []


def main() -> None:
    print(BANNER)

    max_h = list_resolutions()
    if max_h is None:
        print(c(C.DIM, "\nĐã thoát."))
        sys.exit(0)
    print(f"\n{c(C.GREEN, '✔ Chất lượng tối đa:')} {c(C.YELLOW, f'{max_h}p', bold=True)}\n")

    print_box("Chế độ tải", [
        ("1", "Tải một video"),
        ("2", "Tải nhiều video"),
        ("3", "Tải playlist"),
    ])
    mode = prompt("\nLựa chọn (1-3): ").strip()

    if mode not in ("1", "2", "3"):
        print(c(C.RED, "✘ Lựa chọn không hợp lệ!"))
        sys.exit(1)

    urls = collect_urls(mode)
    if not urls:
        print(c(C.RED, "✘ Không có link nào được nhập!"))
        sys.exit(1)

    is_playlist_mode = mode == "3"
    for url in urls:
        download_video(url, max_height=max_h, is_playlist=is_playlist_mode)

    print(f"\n{c(C.GREEN, '═' * 15 + ' Tất cả đã xong! ' + '═' * 15)}")
    input(c(C.DIM, "Nhấn Enter để thoát..."))


if __name__ == "__main__":
    main()