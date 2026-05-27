"""MusicPlayer — orchestrates playback for school bell system."""

import subprocess
import logging

from src import config
from src.library import MusicLibrary, MusicFolderError
from src.carousel import SmartCarousel
from src.state import StateManager

# Configure logger
logger = logging.getLogger(__name__)


class MusicPlayer:
    """Orchestrates music playback for school bell system."""

    def __init__(self, music_base: str | None = None):
        self.music_base = music_base if music_base is not None else str(config.MUSIC_DIR)
        self.library = MusicLibrary(music_base)
        self.state = StateManager()
        self.carousels: dict[str, SmartCarousel] = {}

    def play(self, music_type: str) -> None:
        """Play next song for given music type."""
        try:
            # ── MUTE GUARD (defense in depth) ──
            if self.state.get_muted():
                logger.info(f"System muted — skipping {music_type}")
                return

            # Validate folder first
            if not self.library.validate_folder(music_type):
                logger.warning(f"Folder missing or empty: {music_type}")
                return

            # Get carousel for this type (lazy-load)
            carousel = self._get_carousel(music_type)

            # Get next song
            song_path = carousel.next_song()

            # Get duration for this music type
            duration = self.state.get_duration(music_type)

            # Play with mpv
            self._run_mpv(song_path, duration)

            logger.info(f"Played {music_type}/{song_path.split('/')[-1]}")

        except MusicFolderError as e:
            logger.warning(f"Music folder error for {music_type}: {e}")
        except Exception as e:
            logger.error(f"Error playing {music_type}: {e}")

    def _get_carousel(self, music_type: str) -> SmartCarousel:
        """Lazy-load or return cached carousel for music type."""
        if music_type not in self.carousels:
            self.carousels[music_type] = SmartCarousel(
                music_type, self.state, self.music_base
            )
        return self.carousels[music_type]

    def _run_mpv(self, file_path: str, duration: int | None = None) -> int:
        """Execute mpv subprocess with proper args.

        Uses ALSA directly (no PulseAudio/PipeWire dependency).
        ALSA device is read from StateManager (default: sysdefault:CARD=PCH).

        When duration is set (>0), adds --length=N flag and adjusts timeout.
        When duration is None or 0 (full song), plays with 600s timeout.

        Returns exit code from mpv.
        """
        try:
            alsa_device = self.state.get_alsa_device()
            cmd = [
                "/usr/bin/mpv",
                "--ao=alsa",
                f"--audio-device=alsa/{alsa_device}",
                "--no-terminal",
                "--really-quiet",
            ]
            if duration is not None and duration > 0:
                cmd.append(f"--length={duration}")
                timeout = max(40, min(600, duration * 2 + 5))
            else:
                timeout = 600  # Canción completa — timeout generoso
            cmd.append(file_path)

            result = subprocess.run(
                cmd,
                check=False,
                timeout=timeout,
            )
            return result.returncode
        except FileNotFoundError:
            logger.error("mpv not found at /usr/bin/mpv")
            return 1
        except subprocess.TimeoutExpired:
            logger.error(f"mpv timeout for {file_path}")
            return 1
        except Exception as e:
            logger.error(f"mpv failed: {e}")
            return 1
