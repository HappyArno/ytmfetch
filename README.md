# ytmfetch

Download songs from YouTube Music using a JSON song list.

## Requirements

- Python 3.10+
- `ffmpeg` available on your PATH (needed for audio conversion, metadata, and thumbnails)

## Installation

```bash
pip install git+https://github.com/HappyArno/ytmfetch
```

## Usage

### Prepare a Songs JSON File

The songs file format:

- Keys become directory names or MP3 filenames; values are YouTube Music URLs. Nested objects create subfolders.
- Default songs file is `songs.json` in the target directory. A ready-to-run example lives at [`./songs.json`](./songs.json).
- Use filesystem-safe names for keys; invalid names are skipped.

```json
{
  "Song Title": "https://music.youtube.com/watch?v=video_id",
  "Folder Name": {
    "Song In Folder": "https://music.youtube.com/watch?v=another_id",
    "Nested Folder": {
      "Deep Song": "https://music.youtube.com/watch?v=yet_another_id"
    }
  }
}
```

### Run the Downloader

```bash
ytmfetch
# or with options
ytmfetch -d ~/Music -s songs.json -q 192
```

### Enjoy Music!

Find your MP3s (with metadata and cover art) in the target directory.

## Options

```
options:
  -h, --help            show this help message and exit
  -v, --verbose, --no-verbose
                        Enable verbose logging
  -w, --overwrite, --no-overwrite
                        Overwrite existing files
  -d, --dir DIR         Change base directory
  -s, --songs-file SONGS_FILE
                        Path to the songs JSON file
  -q, --quality QUALITY
                        Set audio quality (VBR/CBR)
```

## License

Copyright (C) 2026 HappyArno

This program is released under the [MIT](./LICENSE) license.
