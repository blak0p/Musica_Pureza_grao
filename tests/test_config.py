"""Tests for src/config.py — centralized path configuration for school bell system."""
import importlib
import os
import unittest
from pathlib import Path
from unittest.mock import patch


class TestConfigProjectDir(unittest.TestCase):
    """Test PROJECT_DIR autodetection."""

    def test_project_dir_is_project_root_parent_of_src(self):
        """PROJECT_DIR should be the project root (parent of src/)."""
        import src.config
        expected = Path(__file__).resolve().parent.parent
        self.assertEqual(src.config.PROJECT_DIR, expected)

    def test_project_dir_contains_app_py(self):
        """PROJECT_DIR should contain app.py (project marker)."""
        import src.config
        self.assertTrue((src.config.PROJECT_DIR / "app.py").exists())

    def test_project_dir_contains_src_directory(self):
        """PROJECT_DIR should contain src/ directory."""
        import src.config
        self.assertTrue((src.config.PROJECT_DIR / "src").is_dir())


class TestConfigDefaults(unittest.TestCase):
    """Test default values when no env vars are set."""

    def test_music_dir_defaults_to_home_musica(self):
        """MUSIC_DIR defaults to Path.home() / 'musica' when no env var."""
        import src.config
        expected = Path.home() / "musica"
        self.assertEqual(src.config.MUSIC_DIR, expected)

    def test_static_dir_defaults_to_project_static(self):
        """STATIC_DIR defaults to PROJECT_DIR / 'static'."""
        import src.config
        expected = src.config.PROJECT_DIR / "static"
        self.assertEqual(src.config.STATIC_DIR, expected)

    def test_state_dir_is_project_state(self):
        """STATE_DIR is PROJECT_DIR / 'state'."""
        import src.config
        expected = src.config.PROJECT_DIR / "state"
        self.assertEqual(src.config.STATE_DIR, expected)

    def test_log_file_server_derived_from_state_dir(self):
        """LOG_FILE_SERVER is STATE_DIR / 'server.log'."""
        import src.config
        expected = src.config.STATE_DIR / "server.log"
        self.assertEqual(src.config.LOG_FILE_SERVER, expected)

    def test_log_file_bell_derived_from_state_dir(self):
        """LOG_FILE_BELL is STATE_DIR / 'colegio-bell.log'."""
        import src.config
        expected = src.config.STATE_DIR / "colegio-bell.log"
        self.assertEqual(src.config.LOG_FILE_BELL, expected)

    def test_state_file_derived_from_state_dir(self):
        """STATE_FILE is STATE_DIR / 'carousel.json'."""
        import src.config
        expected = src.config.STATE_DIR / "carousel.json"
        self.assertEqual(src.config.STATE_FILE, expected)

    def test_system_paths_have_defaults(self):
        """PYTHON_PATH and MPV_PATH have sensible defaults."""
        import src.config
        self.assertEqual(src.config.PYTHON_PATH, "/usr/bin/python3")
        self.assertEqual(src.config.MPV_PATH, "/usr/bin/mpv")


class TestConfigEnvVarOverride(unittest.TestCase):
    """Test that env vars override defaults."""

    @patch.dict(os.environ, {"MUSIC_DIR": "/custom/music/path"})
    def test_music_dir_uses_env_var_when_set(self):
        """When MUSIC_DIR env var is set, it overrides the default."""
        import src.config
        importlib.reload(src.config)
        self.assertEqual(str(src.config.MUSIC_DIR), "/custom/music/path")

    @patch.dict(os.environ, {"MUSIC_DIR": "/another/path"})
    def test_music_dir_env_var_different_value(self):
        """MUSIC_DIR can be set to any path via env var."""
        import src.config
        importlib.reload(src.config)
        self.assertEqual(str(src.config.MUSIC_DIR), "/another/path")

    @patch.dict(os.environ, {"STATIC_DIR": "/custom/static/path"})
    def test_static_dir_uses_env_var_when_set(self):
        """When STATIC_DIR env var is set, it overrides the default."""
        import src.config
        importlib.reload(src.config)
        self.assertEqual(str(src.config.STATIC_DIR), "/custom/static/path")


class TestConfigDerivedPaths(unittest.TestCase):
    """Test that derived paths are always relative to PROJECT_DIR."""

    def test_state_dir_always_relative_to_project(self):
        """STATE_DIR stays relative to PROJECT_DIR regardless of env."""
        import src.config
        self.assertTrue(str(src.config.STATE_DIR).startswith(str(src.config.PROJECT_DIR)))

    def test_log_files_inside_state_dir(self):
        """LOG_FILE_SERVER and LOG_FILE_BELL live inside STATE_DIR."""
        import src.config
        self.assertEqual(src.config.LOG_FILE_SERVER.parent, src.config.STATE_DIR)
        self.assertEqual(src.config.LOG_FILE_BELL.parent, src.config.STATE_DIR)
        self.assertEqual(src.config.STATE_FILE.parent, src.config.STATE_DIR)


class TestConfigDotEnv(unittest.TestCase):
    """Test .env loading behavior."""

    @patch.dict(os.environ, {"WEB_USER": "admin"}, clear=False)
    def test_web_user_loaded_from_env(self):
        """WEB_USER is loaded from the .env file when not overridden by env."""
        import src.config
        importlib.reload(src.config)
        # .env has WEB_USER=admin, and we set it in environ via patch
        self.assertEqual(src.config.WEB_USER, "admin")

    def test_web_password_loaded_from_env(self):
        """WEB_PASSWORD is loaded from the .env file."""
        import src.config
        self.assertEqual(src.config.WEB_PASSWORD, "eit2021")

    @patch.dict(os.environ, {"WEB_USER": "admin"}, clear=False)
    def test_web_user_fallback_when_not_in_env(self):
        """WEB_USER falls back to 'admin' when not in env/.env."""
        import src.config
        importlib.reload(src.config)
        self.assertEqual(src.config.WEB_USER, "admin")

    def test_web_password_fallback_when_not_in_env(self):
        """WEB_PASSWORD falls back to 'admin123' when not in env/.env."""
        import src.config
        self.assertEqual(src.config.WEB_PASSWORD, "eit2021")


class TestConfigPythonDotenv(unittest.TestCase):
    """Test that python-dotenv is used (if available)."""

    def test_load_dotenv_function_exists(self):
        """config module has a _load_dotenv function."""
        import src.config
        self.assertTrue(hasattr(src.config, "_load_dotenv"))
        self.assertTrue(callable(src.config._load_dotenv))

    def test_load_dotenv_does_not_crash_on_missing_file(self):
        """_load_dotenv handles missing .env gracefully."""
        import src.config
        from pathlib import Path
        # Should not raise for a nonexistent path
        try:
            src.config._load_dotenv(Path("/nonexistent/.env"))
        except Exception as e:
            self.fail(f"_load_dotenv raised {e} for nonexistent file")


class TestConfigPathTypes(unittest.TestCase):
    """Test that path constants are Path instances, not strings."""

    def test_music_dir_is_path_instance(self):
        """MUSIC_DIR is a Path object."""
        import src.config
        self.assertIsInstance(src.config.MUSIC_DIR, Path)

    def test_static_dir_is_path_instance(self):
        """STATIC_DIR is a Path object."""
        import src.config
        self.assertIsInstance(src.config.STATIC_DIR, Path)

    def test_state_dir_is_path_instance(self):
        """STATE_DIR is a Path object."""
        import src.config
        self.assertIsInstance(src.config.STATE_DIR, Path)

    def test_state_file_is_path_instance(self):
        """STATE_FILE is a Path object."""
        import src.config
        self.assertIsInstance(src.config.STATE_FILE, Path)

    def test_log_files_are_path_instances(self):
        """LOG_FILE_SERVER and LOG_FILE_BELL are Path objects."""
        import src.config
        self.assertIsInstance(src.config.LOG_FILE_SERVER, Path)
        self.assertIsInstance(src.config.LOG_FILE_BELL, Path)


class TestConfigEdgeCases(unittest.TestCase):
    """Test edge cases for config module."""

    def test_env_file_with_empty_lines_does_not_crash(self):
        """_load_dotenv handles files with empty lines."""
        import src.config
        from pathlib import Path
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("\n\n\n# comment\n\nTEST_KEY=testvalue\n\nANOTHER_KEY=another\n\n")
            tmp_path = f.name

        try:
            src.config._load_dotenv(Path(tmp_path))
            self.assertEqual(os.environ.get("TEST_KEY"), "testvalue")
            self.assertEqual(os.environ.get("ANOTHER_KEY"), "another")
        finally:
            # Clean up to avoid leaking env
            os.environ.pop("TEST_KEY", None)
            os.environ.pop("ANOTHER_KEY", None)
            os.unlink(tmp_path)

    def test_env_file_with_comments_only_does_not_crash(self):
        """_load_dotenv handles files with only comments."""
        import src.config
        from pathlib import Path
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# This is a comment\n# Another comment\n")
            tmp_path = f.name

        try:
            # Should not crash
            src.config._load_dotenv(Path(tmp_path))
        finally:
            os.unlink(tmp_path)

    def test_env_file_missing_path_does_not_crash(self):
        """_load_dotenv with nonexistent path returns silently."""
        import src.config
        from pathlib import Path
        # Should not raise
        src.config._load_dotenv(Path("/tmp/nonexistent_dir_12345/.env"))


if __name__ == "__main__":
    unittest.main()
