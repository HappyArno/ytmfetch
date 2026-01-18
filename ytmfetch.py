import yt_dlp
import logging
import json
import argparse
from pathlib import Path
from pathvalidate import is_valid_filename
from dataclasses import dataclass
from importlib import metadata


@dataclass
class Downloader:
    config: argparse.Namespace
    logger: logging.Logger

    def get_ydl_opts(self, output_path: Path, song_name: str | None = None):
        return {
            "format": "bestaudio/best",
            "paths": {"home": str(output_path)},
            "outtmpl": f"{song_name if song_name else '%(title)s'}.%(ext)s",
            "postprocessors": [
                # Extract audio and convert it to MP3
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": self.config.quality,
                },
                # Inject metadata parsed by yt-dlp into the output file
                {"key": "FFmpegMetadata"},
                # Convert the thumbnail to JPG format
                {
                    "key": "FFmpegThumbnailsConvertor",
                    "format": "jpg",
                },
                # Attach the video thumbnail as embedded cover artwork
                {"key": "EmbedThumbnail"},
                # {
                #     "key": "FFmpegSubtitlesConvertor",
                #     "format": "lrc",
                # },
                # # Embed lyrics
                # # [EmbedSubtitle] Subtitles can only be embedded in mp4, mov, m4a, webm, mkv, mka files
                # {"key": "FFmpegEmbedSubtitle"},
            ],
            "postprocessor_args": {
                # Process thumbnail
                "embedthumbnail+ffmpeg_o": [
                    "-c:v",
                    "mjpeg",
                    "-vf",
                    "crop='min(iw,ih)':'min(iw,ih)':'(iw-ow)/2':'(ih-oh)/2'",
                ],
                # "default": ["-id3v2_version", "3"],
            },
            "writethumbnail": True,
            # "embedthumbnail": True,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "quiet": not self.config.verbose,
            "no_warnings": not self.config.verbose,
            "continuedl": True,
            "ignoreerrors": False,
            "overwrites": self.config.overwrite,
            # "postoverwrites": False, # useless
            # "logger": self.logger,
        }

    def download_song(self, url: str, song_name: str, output_path: Path) -> bool:
        if not is_valid_filename(song_name):
            self.logger.error(f"Invalid filename: {song_name}")
            return False
        output_path.mkdir(parents=True, exist_ok=True)
        mp3 = output_path / f"{song_name}.mp3"
        if (not self.config.overwrite) and mp3.exists() and mp3.stat().st_size > 0:
            return True
        self.logger.info(f"Downloading: {song_name}")
        opts = self.get_ydl_opts(output_path, song_name)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                error_code = ydl.download([url])
                # info = ydl.extract_info(url, download=True)
            return error_code == 0
        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            return False

    def walk_music_tree(self, node: dict, path: Path):
        for key, value in node.items():
            if not is_valid_filename(key):
                self.logger.error(f"Invalid filename: {key}")
                continue
            if isinstance(value, str):
                self.download_song(value, key, path)
            elif isinstance(value, dict):
                self.walk_music_tree(value, path / key)
            else:
                self.logger.error(f"Invalid value for key {key}")
                continue

    def download(self, songs: dict):
        self.walk_music_tree(songs, self.config.dir)


def get_version() -> str:
    try:
        return metadata.version("ytmfetch")
    except metadata.PackageNotFoundError:
        return "0+unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download songs from YouTube Music using a JSON song list"
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + get_version()
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable verbose logging",
    )
    parser.add_argument(
        "-w",
        "--overwrite",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Overwrite existing files",
    )
    parser.add_argument(
        "-d", "--dir", type=Path, default=Path.cwd(), help="Change base directory"
    )
    parser.add_argument(
        "-s",
        "--songs-file",
        type=Path,
        default=Path("songs.json"),
        help="Path to the songs JSON file",
    )
    parser.add_argument(
        "-q",
        "--quality",
        default="128",
        help="Set audio quality (VBR/CBR)",
    )
    return parser.parse_args()


def main():
    config = parse_args()
    config.dir = config.dir.expanduser().resolve()

    level = logging.DEBUG if config.verbose else logging.INFO
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")
    logger = logging.getLogger(__name__)

    try:
        with (config.dir / config.songs_file).open("r", encoding="utf-8") as f:
            songs = json.load(f)
    except FileNotFoundError as e:
        logger.error(f"Songs file not found: {e}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return

    downloader = Downloader(config, logger)
    downloader.download(songs)


if __name__ == "__main__":
    main()
