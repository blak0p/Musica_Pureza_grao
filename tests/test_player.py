"""Tests for MusicPlayer — RED phase (tests written first, implementation doesn't exist yet)"""
import unittest
import os
import tempfile
import shutil
import subprocess
from unittest.mock import patch, MagicMock

# This import will FAIL until src/player.py is created — that's the RED phase
from src.player import MusicPlayer


class TestMusicPlayerInit(unittest.TestCase):
    """Test MusicPlayer initialization."""

    def test_init_sets_music_base_default(self):
        """MusicPlayer uses default music base from config when not specified."""
        from src import config
        player = MusicPlayer()
        self.assertEqual(player.music_base, str(config.MUSIC_DIR))

    def test_init_accepts_custom_music_base(self):
        """MusicPlayer accepts custom music base path."""
        player = MusicPlayer(music_base="/custom/path")
        self.assertEqual(player.music_base, "/custom/path")

    def test_init_creates_library_state_and_carousels(self):
        """MusicPlayer initializes MusicLibrary, StateManager, and carousels dict."""
        player = MusicPlayer(music_base="/tmp/test")

        # Should have library and state instances
        self.assertIsNotNone(player.library)
        self.assertIsNotNone(player.state)
        self.assertIsNotNone(player.carousels)
        self.assertEqual(player.carousels, {})


class TestMusicPlayerGetCarousel(unittest.TestCase):
    """Test MusicPlayer._get_carousel() method."""

    def setUp(self):
        """Create temp directory for music."""
        self.temp_dir = tempfile.mkdtemp()
        self.music_base = os.path.join(self.temp_dir, "musica")
        os.makedirs(self.music_base)

        self.player = MusicPlayer(music_base=self.music_base)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_get_carousel_creates_new_for_unknown_type(self):
        """_get_carousel() creates SmartCarousel for new music type."""
        # Create a folder for the music type
        os.makedirs(os.path.join(self.music_base, "cambio"))

        carousel = self.player._get_carousel("cambio")

        # Should return a SmartCarousel instance
        self.assertIsNotNone(carousel)
        self.assertIn("cambio", self.player.carousels)

    def test_get_carousel_returns_cached_for_known_type(self):
        """_get_carousel() returns cached carousel for known music type."""
        os.makedirs(os.path.join(self.music_base, "entrada"))

        carousel1 = self.player._get_carousel("entrada")
        carousel2 = self.player._get_carousel("entrada")

        # Should be the same instance (cached)
        self.assertIs(carousel1, carousel2)


class TestMusicPlayerRunMpv(unittest.TestCase):
    """Test MusicPlayer._run_mpv() method per spec scenarios."""

    def setUp(self):
        self.player = MusicPlayer(music_base="/tmp/test")

    @patch('src.player.subprocess.run')
    def test_run_mpv_calls_subprocess_with_correct_args(self, mock_run):
        """Verify mpv is called with --ao=alsa, --audio-device=..., --no-terminal, --really-quiet."""
        mock_run.return_value = MagicMock(returncode=0)
        self.player.state.get_alsa_device = MagicMock(return_value="sysdefault:CARD=PCH")

        self.player._run_mpv("/path/to/song.mp3", duration=35)

        # Check subprocess.run was called
        mock_run.assert_called_once()
        args = mock_run.call_args

        # First arg should be the command list
        cmd = args[0][0]
        self.assertEqual(cmd[0], "/usr/bin/mpv")
        self.assertIn("--ao=alsa", cmd)
        self.assertIn("--audio-device=alsa/sysdefault:CARD=PCH", cmd)
        self.assertIn("--no-terminal", cmd)
        self.assertIn("--really-quiet", cmd)
        self.assertIn("--length=35", cmd)
        self.assertEqual(cmd[-1], "/path/to/song.mp3")

    @patch('src.player.subprocess.run')
    def test_run_mpv_returns_exit_code_zero_on_success(self, mock_run):
        """Spec scenario: Successful playback returns exit code 0."""
        mock_run.return_value = MagicMock(returncode=0)

        result = self.player._run_mpv("/path/to/song.mp3")

        self.assertEqual(result, 0)

    @patch('src.player.subprocess.run')
    def test_run_mpv_handles_failure_gracefully(self, mock_run):
        """Spec scenario: mpv failure doesn't crash system."""
        mock_run.side_effect = FileNotFoundError("mpv not found")

        # Should not raise an exception
        result = self.player._run_mpv("/path/to/song.mp3")

        # Should return non-zero on failure
        self.assertEqual(result, 1)

    @patch('src.player.subprocess.run')
    def test_run_mpv_handles_timeout_gracefully(self, mock_run):
        """Spec scenario: mpv timeout or failure doesn't crash."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="mpv", timeout=40)

        # Should not raise
        result = self.player._run_mpv("/path/to/song.mp3")

        # Should return 1 on timeout
        self.assertEqual(result, 1)


class TestMusicPlayerPlay(unittest.TestCase):
    """Test MusicPlayer.play() method."""

    def setUp(self):
        """Create temp directory with music."""
        self.temp_dir = tempfile.mkdtemp()
        self.music_base = os.path.join(self.temp_dir, "musica")
        self.music_type = "cambio"
        self.music_folder = os.path.join(self.music_base, self.music_type)
        os.makedirs(self.music_folder)

        # Create a test song
        self.test_song = "test_song.mp3"
        with open(os.path.join(self.music_folder, self.test_song), "w") as f:
            f.write("")

        self.player = MusicPlayer(music_base=self.music_base)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('src.player.MusicPlayer._run_mpv')
    def test_play_calls_next_song_and_runs_mpv(self, mock_run_mpv):
        """play() gets next song from carousel and runs mpv."""
        mock_run_mpv.return_value = 0

        self.player.play(self.music_type)

        # mpv should have been called
        mock_run_mpv.assert_called_once()
        # The argument should be a path containing our test song
        called_path = mock_run_mpv.call_args[0][0]
        self.assertIn(self.test_song, called_path)

    @patch('src.player.MusicPlayer._run_mpv')
    def test_play_handles_missing_folder_gracefully(self, mock_run_mpv):
        """play() handles missing music folder without crashing."""
        # Try to play a type that doesn't exist
        self.player.play("nonexistent")

        # Should not call mpv
        mock_run_mpv.assert_not_called()

    @patch('src.player.MusicPlayer._run_mpv')
    @patch('src.player.logger')
    def test_play_logs_playback_event(self, mock_logger, mock_run_mpv):
        """play() logs the playback event."""
        mock_run_mpv.return_value = 0

        self.player.play(self.music_type)

        # Should have logged something
        mock_logger.info.assert_called()


class TestMusicPlayerDuration(unittest.TestCase):
    """Test MusicPlayer duration integration — _run_mpv with duration, play() consults state."""

    def setUp(self):
        self.player = MusicPlayer(music_base="/tmp/test")

    # ── Task 2.2: _run_mpv with duration=None (no -t flag, 600s timeout) ──

    @patch('src.player.subprocess.run')
    def test_run_mpv_no_duration_uses_600s_timeout(self, mock_run):
        """_run_mpv with duration=None does NOT add --length flag, uses 600s timeout (full song)."""
        mock_run.return_value = MagicMock(returncode=0)

        self.player._run_mpv("/path/to/song.mp3", duration=None)

        self.assertEqual(mock_run.return_value.returncode, 0)
        # Should NOT have --length or -t flag
        cmd = mock_run.call_args[0][0]
        self.assertNotIn("-t", cmd)
        self.assertNotIn("--length", cmd)
        # Should have 600s timeout for full song
        self.assertEqual(mock_run.call_args[1]['timeout'], 600)

    # ── Task 2.2: _run_mpv with duration=30 (has -t 30, timeout=65) ──

    @patch('src.player.subprocess.run')
    def test_run_mpv_with_duration_adds_length_flag_and_dynamic_timeout(self, mock_run):
        """_run_mpv with duration=30 adds --length=30 and timeout=65 (30*2+5)."""
        mock_run.return_value = MagicMock(returncode=0)

        self.player._run_mpv("/path/to/song.mp3", duration=30)

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        self.assertIn("--length=30", cmd)
        self.assertEqual(mock_run.call_args[1]['timeout'], 65)

    # ── Task 2.3: timeout clamped to minimum 40s ──

    @patch('src.player.subprocess.run')
    def test_run_mpv_with_short_duration_clamps_timeout_to_minimum(self, mock_run):
        """_run_mpv with duration=5 still has --length=5 but timeout clamped to 40 (min)."""
        mock_run.return_value = MagicMock(returncode=0)

        self.player._run_mpv("/path/to/song.mp3", duration=5)

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        self.assertIn("--length=5", cmd)
        self.assertEqual(mock_run.call_args[1]['timeout'], 40)

    # ── Task 2.3: timeout capped at maximum 600s ──

    @patch('src.player.subprocess.run')
    def test_run_mpv_with_long_duration_caps_timeout_to_maximum(self, mock_run):
        """_run_mpv with duration=350 caps timeout at 600 (max)."""
        mock_run.return_value = MagicMock(returncode=0)

        self.player._run_mpv("/path/to/song.mp3", duration=350)

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        self.assertIn("--length=350", cmd)
        self.assertEqual(mock_run.call_args[1]['timeout'], 600)

    # ── Task 2.1: play() consults state.get_duration() and passes to _run_mpv ──

    @patch('src.player.MusicPlayer._run_mpv')
    def test_play_consults_state_duration_and_passes_to_run_mpv(self, mock_run_mpv):
        """play() calls state.get_duration() and passes result to _run_mpv."""
        self.player.state.get_duration = MagicMock(return_value=45)

        mock_carousel = MagicMock()
        mock_carousel.next_song.return_value = "/path/to/song.mp3"
        self.player._get_carousel = MagicMock(return_value=mock_carousel)
        self.player.library.validate_folder = MagicMock(return_value=True)

        self.player.play("entrada")

        self.player.state.get_duration.assert_called_once_with("entrada")
        mock_run_mpv.assert_called_once_with("/path/to/song.mp3", 45)

    @patch('src.player.MusicPlayer._run_mpv')
    def test_play_passes_none_duration_when_state_returns_none(self, mock_run_mpv):
        """play() passes duration=None to _run_mpv when state returns None (full song)."""
        self.player.state.get_duration = MagicMock(return_value=None)

        mock_carousel = MagicMock()
        mock_carousel.next_song.return_value = "/path/to/song.mp3"
        self.player._get_carousel = MagicMock(return_value=mock_carousel)
        self.player.library.validate_folder = MagicMock(return_value=True)

        self.player.play("salida")

        self.player.state.get_duration.assert_called_once_with("salida")
        mock_run_mpv.assert_called_once_with("/path/to/song.mp3", None)


class TestMusicPlayerMuteGuard(unittest.TestCase):
    """Test MusicPlayer.play() mute guard — defense in depth."""

    def setUp(self):
        """Create temp directory with music."""
        self.temp_dir = tempfile.mkdtemp()
        self.music_base = os.path.join(self.temp_dir, "musica")
        self.music_type = "cambio"
        self.music_folder = os.path.join(self.music_base, self.music_type)
        os.makedirs(self.music_folder)

        # Create a test song
        self.test_song = "test_song.mp3"
        with open(os.path.join(self.music_folder, self.test_song), "w") as f:
            f.write("")

        self.player = MusicPlayer(music_base=self.music_base)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('src.player.MusicPlayer._run_mpv')
    def test_play_returns_early_when_muted(self, mock_run_mpv):
        """GIVEN state.get_muted() returns True
        WHEN play() called
        THEN returns without calling _run_mpv"""
        self.player.state.get_muted = MagicMock(return_value=True)
        mock_run_mpv.return_value = 0

        self.player.play(self.music_type)

        mock_run_mpv.assert_not_called()

    @patch('src.player.logger')
    @patch('src.player.MusicPlayer._run_mpv')
    def test_play_logs_muted_message(self, mock_run_mpv, mock_logger):
        """GIVEN system is muted
        WHEN play() called
        THEN logs 'System muted' message"""
        self.player.state.get_muted = MagicMock(return_value=True)
        mock_run_mpv.return_value = 0

        self.player.play(self.music_type)

        # Should log a message containing "skipping" or "muted"
        found = any("skipping" in str(call) or "muted" in str(call).lower()
                    for call in mock_logger.info.call_args_list)
        self.assertTrue(found, "Expected logger to record muted/skipping message")

    @patch('src.player.MusicPlayer._run_mpv')
    def test_play_mute_check_before_folder_validation(self, mock_run_mpv):
        """GIVEN system is muted
        WHEN play() called
        THEN validate_folder is NOT called (mute guard fires first)"""
        self.player.state.get_muted = MagicMock(return_value=True)
        self.player.library.validate_folder = MagicMock(return_value=True)
        mock_run_mpv.return_value = 0

        self.player.play(self.music_type)

        self.player.library.validate_folder.assert_not_called()

    @patch('src.player.MusicPlayer._run_mpv')
    def test_play_normal_flow_when_not_muted(self, mock_run_mpv):
        """GIVEN state.get_muted() returns False
        WHEN play() called
        THEN proceeds to call _run_mpv (normal flow)"""
        self.player.state.get_muted = MagicMock(return_value=False)
        mock_run_mpv.return_value = 0

        self.player.play(self.music_type)

        mock_run_mpv.assert_called_once()


if __name__ == "__main__":
    unittest.main()
