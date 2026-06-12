# Music Carousel Hours

A robust school bell system for automated music playback.

## Installation

### Quick Install (3 Simple Steps - No Git Required)

**Step 1: Download the complete repository content with curl**
```bash
curl -sSL https://github.com/blak0p/Musica_Pureza_grao/archive/refs/heads/main.zip -o musica-pureza.zip && unzip -q musica-pureza.zip && cd Musica_Pureza_grao-main
```

**Step 2: Make the installer executable**
```bash
chmod +x install.sh
```

**Step 3: Run the installer**
```bash
./install.sh
```

That's it! The script will:
- ✅ Download and extract the complete code repository
- ✅ Set executable permissions on all scripts
- ✅ Install all system dependencies (mpv, Python, Flask)
- ✅ Configure everything automatically

---

## Description

This system is designed for a school environment, running on a dedicated **always-on mini PC**. It replaces a legacy bash script with a modern Python application featuring a smart music carousel, [...]

All code comments and internal logic are in Spanish (matching the school's language), while this documentation is in English for global accessibility.

## Features

*   **Smart Carousel (`SmartCarousel`)**: Guarantees no song repeats until all tracks in a folder have been played. It detects new songs automatically.
*   **Configurable Schedule**: Bell times are defined in `src/cron_helper.py` (`BELL_TIMES`) and can be easily adjusted to match the school's morning and afternoon shifts.
*   **Robust CLI**: Simple command-line interface to play music by type (`entrada`, `cambio`, `recreo`, `salida`).
*   **Crontab Integration**: One-command setup (`--setup-cron`) generates 11 cron entries with proper environment variables for audio playback.
*   **Persistent State**: Remembers the last played song and queue status in JSON, surviving reboots.
*   **Graceful Handling**: Skips playback on weekends and handles empty/missing folders without crashing.
*   **Logging**: Detailed logs to `/var/log/colegio-bell.log` (with fallback to project directory).

## Tech Stack

*   **Language**: Python 3.12.3
*   **Audio Player**: `mpv` (via subprocess)
*   **Scheduler**: System `crontab`
*   **Testing**: Strict TDD with `unittest` (73 passing tests)

## Usage

```bash
# Play a specific music type (entrada, cambio, recreo, salida)
python3 bell.py cambio

# Setup crontab entries for the school schedule
python3 bell.py --setup-cron

# Remove crontab entries
python3 bell.py --remove-cron

# Check last played and next in queue
python3 bell.py --status
```

## Uninstallation

To remove the application and crontab entries:

```bash
/opt/musica-pureza-grao/uninstall.sh
```

## Testing

The project follows **Strict TDD**. To run the 73 unit tests:

```bash
cd /opt/musica-pureza-grao
python3 -m unittest discover -s tests
```

## Project Structure

```
.
├── bell.py               # Main CLI entry point
├── app.py                # Flask web interface
├── src/
│   ├── library.py       # MusicLibrary (scans folders)
│   ├── state.py         # StateManager (JSON persistence)
│   ├── carousel.py      # SmartCarousel (no-repeat logic)
│   ├── player.py        # MusicPlayer (orchestrates playback)
│   └── cron_helper.py  # CronHelper (schedule generation)
├── templates/           # Web interface templates
├── static/              # Static assets (CSS, JS)
└── tests/              # Unit tests (73 tests)
```

## Upcoming Features

*   **Web/Mobile Interface**: A user-friendly interface for school staff to modify bell schedules and manage songs without touching the terminal.
*   **Dynamic Schedule Changes**: Interface-driven schedule adjustments (no manual code edits).
*   **Remote PC Control**: SSH/TeamViewer integration for remote management.

---

*Made with ❤️ for schools that need reliable bell systems.*
