"""Tests for StateManager — RED phase (tests written first, implementation doesn't exist yet)"""
import unittest
import os
import json
import tempfile
import shutil
import time

# This import will FAIL until src/state.py is created — that's the RED phase
from src.state import StateManager


class TestStateManagerLoad(unittest.TestCase):
    """Test StateManager.load() method per spec scenarios."""

    def setUp(self):
        """Create a temp directory to act as state dir."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "carousel.json")
        # Patch STATE_FILE for testing — we'll use a test-specific path
        StateManager.STATE_FILE = self.state_file
        StateManager.STATE_DIR = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_nonexistent_file_returns_empty_dict(self):
        """Load returns empty dict when state file doesn't exist."""
        self.assertFalse(os.path.exists(self.state_file))
        manager = StateManager()
        result = manager.load()
        self.assertEqual(result, {})

    def test_load_valid_json_returns_data(self):
        """Load returns valid data from JSON file."""
        test_data = {
            "cambio": {
                "queue": ["song1.mp3", "song2.mp3"],
                "last_played": "song1.mp3",
                "last_played_time": "2026-05-04T10:30:00"
            }
        }
        with open(self.state_file, "w") as f:
            json.dump(test_data, f)

        manager = StateManager()
        result = manager.load()
        self.assertEqual(result, test_data)

    def test_load_corrupt_json_backups_and_returns_empty(self):
        """Spec scenario: Corrupt JSON recovery.

        GIVEN carousel.json contains invalid JSON
        WHEN state.load() called
        THEN backs up corrupt file to carousel.json.corrupt.{timestamp}, returns empty dict
        """
        # Write invalid JSON
        with open(self.state_file, "w") as f:
            f.write("{invalid json garbage")

        manager = StateManager()
        result = manager.load()

        # Should return empty dict
        self.assertEqual(result, {})

        # Should have backed up the corrupt file
        backup_files = [f for f in os.listdir(self.temp_dir)
                        if f.startswith("carousel.json.corrupt.")]
        self.assertEqual(len(backup_files), 1)

        # Corrupt file should no longer exist as the main file
        # (it was backed up and removed, load returns {})
        # Actually, let's check: the backup should contain the corrupt content
        backup_path = os.path.join(self.temp_dir, backup_files[0])
        with open(backup_path, "r") as f:
            content = f.read()
        self.assertEqual(content, "{invalid json garbage")


class TestStateManagerSave(unittest.TestCase):
    """Test StateManager.save() method with atomic writes."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "carousel.json")
        StateManager.STATE_FILE = self.state_file
        StateManager.STATE_DIR = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_save_writes_atomic_temp_then_rename(self):
        """Spec scenario: Atomic write.

        GIVEN state dirty with new data
        WHEN state.save(data) called
        THEN writes to temp file first, then renames to carousel.json
        """
        manager = StateManager()
        test_data = {
            "cambio": {
                "queue": ["song1.mp3"],
                "last_played": "song1.mp3",
                "last_played_time": "2026-05-04T10:30:00"
            }
        }

        manager.save(test_data)

        # Main file should exist with correct content
        self.assertTrue(os.path.exists(self.state_file))
        with open(self.state_file, "r") as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, test_data)

    def test_save_creates_state_dir_if_missing(self):
        """Save creates STATE_DIR if it doesn't exist."""
        # Remove the temp_dir to simulate missing dir
        shutil.rmtree(self.temp_dir)
        self.assertFalse(os.path.exists(self.temp_dir))

        manager = StateManager()
        test_data = {"test": "data"}
        manager.save(test_data)

        self.assertTrue(os.path.exists(self.state_file))

    def test_atomic_write_no_partial_reads(self):
        """Verify atomic write: temp file should not remain after rename."""
        manager = StateManager()
        test_data = {"key": "value"}
        manager.save(test_data)

        # No temp files should remain
        temp_files = [f for f in os.listdir(self.temp_dir)
                      if f.startswith("carousel.json.tmp.")]
        self.assertEqual(len(temp_files), 0)


class TestStateManagerFolderState(unittest.TestCase):
    """Test get_folder_state and update_folder_state methods."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "carousel.json")
        StateManager.STATE_FILE = self.state_file
        StateManager.STATE_DIR = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_get_folder_state_returns_correct_data(self):
        """get_folder_state returns state for specific folder."""
        test_data = {
            "entrada": {
                "queue": ["song_a.mp3"],
                "last_played": None,
                "last_played_time": None
            }
        }
        with open(self.state_file, "w") as f:
            json.dump(test_data, f)

        manager = StateManager()
        result = manager.get_folder_state("entrada")
        self.assertEqual(result["queue"], ["song_a.mp3"])
        self.assertIsNone(result["last_played"])

    def test_get_folder_state_missing_returns_default(self):
        """get_folder_state returns default dict for unknown folder."""
        manager = StateManager()
        manager.save({})  # empty state
        result = manager.get_folder_state("nonexistent")
        self.assertEqual(result["queue"], [])
        self.assertIsNone(result["last_played"])
        self.assertIsNone(result["last_played_time"])

    def test_update_folder_state_persists_changes(self):
        """update_folder_state modifies state and saves to disk."""
        manager = StateManager()
        manager.save({})

        manager.update_folder_state(
            "cambio",
            queue=["song1.mp3", "song2.mp3"],
            last_played="song1.mp3",
            last_played_time="2026-05-04T10:30:00"
        )

        # Reload and verify
        reloaded = manager.load()
        self.assertIn("cambio", reloaded)
        self.assertEqual(reloaded["cambio"]["queue"], ["song1.mp3", "song2.mp3"])
        self.assertEqual(reloaded["cambio"]["last_played"], "song1.mp3")


class TestStateManagerDurations(unittest.TestCase):
    """Test get_durations, get_duration, and update_durations methods."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "carousel.json")
        StateManager.STATE_FILE = self.state_file
        StateManager.STATE_DIR = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # --- get_durations() ---

    def test_get_durations_no_key_returns_empty_dict(self):
        """GIVEN carousel.json has NO durations key
        WHEN get_durations() called
        THEN returns {}"""
        manager = StateManager()
        manager.save({"schedule": {"entrada": ["08:05"]}})
        result = manager.get_durations()
        self.assertEqual(result, {})

    def test_get_durations_returns_persisted_dict(self):
        """GIVEN carousel.json has durations key
        WHEN get_durations() called
        THEN returns the full durations dict"""
        state = {"durations": {"entrada": 30, "salida": 60}}
        with open(self.state_file, "w") as f:
            json.dump(state, f)
        manager = StateManager()
        result = manager.get_durations()
        self.assertEqual(result, {"entrada": 30, "salida": 60})

    # --- get_duration(tipo) ---

    def test_get_duration_returns_number_when_tipo_has_value(self):
        """GIVEN durations key exists AND tipo has a number
        WHEN get_duration(tipo) called
        THEN returns that number"""
        state = {"durations": {"entrada": 30}}
        with open(self.state_file, "w") as f:
            json.dump(state, f)
        manager = StateManager()
        result = manager.get_duration("entrada")
        self.assertEqual(result, 30)

    def test_get_duration_returns_none_when_tipo_is_null(self):
        """GIVEN durations key exists AND tipo value is null
        WHEN get_duration(tipo) called
        THEN returns None (full song)"""
        state = {"durations": {"entrada": None}}
        with open(self.state_file, "w") as f:
            json.dump(state, f)
        manager = StateManager()
        result = manager.get_duration("entrada")
        self.assertIsNone(result)

    def test_get_duration_returns_none_when_tipo_absent(self):
        """GIVEN durations key exists BUT tipo is NOT in it
        WHEN get_duration(tipo) called
        THEN returns None (full song)"""
        state = {"durations": {"entrada": 30}}
        with open(self.state_file, "w") as f:
            json.dump(state, f)
        manager = StateManager()
        result = manager.get_duration("salida")
        self.assertIsNone(result)

    def test_get_duration_returns_30_default_when_no_durations_key(self):
        """GIVEN carousel.json has NO durations key at all
        WHEN get_duration(tipo) called
        THEN returns 30"""
        manager = StateManager()
        manager.save({"schedule": {"entrada": ["08:05"]}})
        result = manager.get_duration("entrada")
        self.assertEqual(result, 30)

    # --- get_duration(tipo) with empty durations dict ---

    def test_get_duration_returns_none_when_durations_empty(self):
        """GIVEN durations is {} (empty dict)
        WHEN get_duration(tipo) called
        THEN returns None (tipo not in it, no 30 default)"""
        state = {"durations": {}}
        with open(self.state_file, "w") as f:
            json.dump(state, f)
        manager = StateManager()
        result = manager.get_duration("entrada")
        self.assertIsNone(result)

    # --- update_durations() ---

    def test_update_durations_persists_and_can_be_read_back(self):
        """GIVEN no durations set
        WHEN update_durations({"entrada": 30}) called
        THEN get_durations() returns {"entrada": 30}
        AND file on disk contains the durations"""
        manager = StateManager()
        manager.save({})
        manager.update_durations({"entrada": 30})
        self.assertEqual(manager.get_durations(), {"entrada": 30})
        # Verify on disk
        reloaded = manager.load()
        self.assertEqual(reloaded.get("durations"), {"entrada": 30})

    def test_update_durations_replaces_previous_values(self):
        """GIVEN durations {"entrada": 30} exist
        WHEN update_durations({"entrada": 60, "salida": 45}) called
        THEN get_duration("entrada") == 60
        AND get_duration("salida") == 45"""
        manager = StateManager()
        manager.save({"durations": {"entrada": 30}})
        manager.update_durations({"entrada": 60, "salida": 45})
        self.assertEqual(manager.get_duration("entrada"), 60)
        self.assertEqual(manager.get_duration("salida"), 45)

    # --- update_durations atomic write (Task 1.2) ---

    def test_update_durations_atomic_write_no_temp_file_remains(self):
        """update_durations uses save() which does atomic write.
        No .tmp. files should remain after the operation."""
        manager = StateManager()
        manager.save({})
        manager.update_durations({"entrada": 30})
        temp_files = [f for f in os.listdir(self.temp_dir)
                      if f.startswith("carousel.json.tmp.")]
        self.assertEqual(len(temp_files), 0)

    # --- Corruption handling (Task 1.2, verifying load still works) ---

    def test_load_after_corruption_returns_empty_no_crash(self):
        """GIVEN carousel.json is corrupt
        WHEN load() is called
        THEN it returns {} without crashing
        AND pututside schedule is still usable"""
        with open(self.state_file, "w") as f:
            f.write("{broken")
        manager = StateManager()
        result = manager.load()
        self.assertEqual(result, {})

    def test_durations_methods_work_after_corruption_recovery(self):
        """GIVEN carousel.json was corrupt and has been cleaned
        WHEN duration methods are called
        THEN they work normally (no durations key → 30 default)"""
        with open(self.state_file, "w") as f:
            f.write("{broken")
        manager = StateManager()
        manager.load()  # recovers
        # Should work normally now
        self.assertEqual(manager.get_durations(), {})
        self.assertEqual(manager.get_duration("entrada"), 30)
        manager.update_durations({"entrada": 45})
        self.assertEqual(manager.get_duration("entrada"), 45)


class TestStateManagerAlsaDevice(unittest.TestCase):
    """Test get_alsa_device and set_alsa_device methods."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "carousel.json")
        StateManager.STATE_FILE = self.state_file
        StateManager.STATE_DIR = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_get_alsa_device_returns_default_when_not_set(self):
        """GIVEN state has NO alsa_device key
        WHEN get_alsa_device() called
        THEN returns 'sysdefault:CARD=PCH'"""
        manager = StateManager()
        manager.save({})
        result = manager.get_alsa_device()
        self.assertEqual(result, "sysdefault:CARD=PCH")

    def test_set_and_get_alsa_device_round_trip(self):
        """GIVEN state has alsa_device set to 'hw:0,0'
        WHEN get_alsa_device() called
        THEN returns 'hw:0,0'"""
        manager = StateManager()
        manager.save({})
        manager.set_alsa_device("hw:0,0")
        result = manager.get_alsa_device()
        self.assertEqual(result, "hw:0,0")

    def test_alsa_device_persists_in_json_file(self):
        """GIVEN alsa_device set to 'hw:1,0'
        WHEN a new StateManager loads from disk
        THEN get_alsa_device() returns 'hw:1,0'"""
        manager = StateManager()
        manager.save({})
        manager.set_alsa_device("hw:1,0")
        # Reload from disk with fresh instance
        manager2 = StateManager()
        result = manager2.get_alsa_device()
        self.assertEqual(result, "hw:1,0")

    def test_get_alsa_device_returns_value_when_key_exists(self):
        """GIVEN state has alsa_device key set to 'default:CARD=HDMI'
        WHEN get_alsa_device() called
        THEN returns 'default:CARD=HDMI'"""
        state = {"alsa_device": "default:CARD=HDMI"}
        with open(StateManager.STATE_FILE, "w") as f:
            json.dump(state, f)
        manager = StateManager()
        result = manager.get_alsa_device()
        self.assertEqual(result, "default:CARD=HDMI")

    def test_set_alsa_device_updates_existing_value(self):
        """GIVEN alsa_device is 'hw:0,0'
        WHEN set_alsa_device('hw:2,0') called
        THEN get_alsa_device() returns 'hw:2,0'"""
        manager = StateManager()
        manager.save({})
        manager.set_alsa_device("hw:0,0")
        manager.set_alsa_device("hw:2,0")
        result = manager.get_alsa_device()
        self.assertEqual(result, "hw:2,0")


class TestStateManagerMute(unittest.TestCase):
    """Test get_muted, set_muted, and toggle_muted methods."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "carousel.json")
        StateManager.STATE_FILE = self.state_file
        StateManager.STATE_DIR = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # --- get_muted() ---

    def test_get_muted_default_false_when_no_file(self):
        """GIVEN state file does NOT exist
        WHEN get_muted() called
        THEN returns False"""
        manager = StateManager()
        result = manager.get_muted()
        self.assertFalse(result)

    def test_get_muted_default_false_when_no_key(self):
        """GIVEN state file exists WITHOUT muted key
        WHEN get_muted() called
        THEN returns False"""
        manager = StateManager()
        manager.save({"schedule": {"entrada": ["08:05"]}})
        result = manager.get_muted()
        self.assertFalse(result)

    def test_get_muted_returns_true_when_persisted(self):
        """GIVEN state file has muted: true
        WHEN get_muted() called
        THEN returns True"""
        state = {"muted": True}
        with open(self.state_file, "w") as f:
            json.dump(state, f)
        manager = StateManager()
        result = manager.get_muted()
        self.assertTrue(result)

    def test_get_muted_returns_false_when_persisted_false(self):
        """GIVEN state file has muted: false
        WHEN get_muted() called
        THEN returns False"""
        state = {"muted": False}
        with open(self.state_file, "w") as f:
            json.dump(state, f)
        manager = StateManager()
        result = manager.get_muted()
        self.assertFalse(result)

    # --- set_muted() ---

    def test_set_muted_true_then_get_returns_true(self):
        """GIVEN fresh state
        WHEN set_muted(True) then get_muted()
        THEN returns True"""
        manager = StateManager()
        manager.save({})
        manager.set_muted(True)
        self.assertTrue(manager.get_muted())

    def test_set_muted_false_then_get_returns_false(self):
        """GIVEN state with muted: true
        WHEN set_muted(False) then get_muted()
        THEN returns False"""
        manager = StateManager()
        manager.save({"muted": True})
        manager.set_muted(False)
        self.assertFalse(manager.get_muted())

    def test_set_muted_is_atomic_no_temp_files(self):
        """GIVEN fresh state
        WHEN set_muted(True) called
        THEN no .tmp. files remain after operation"""
        manager = StateManager()
        manager.save({})
        manager.set_muted(True)
        temp_files = [f for f in os.listdir(self.temp_dir)
                      if f.startswith("carousel.json.tmp.")]
        self.assertEqual(len(temp_files), 0)

    # --- toggle_muted() ---

    def test_toggle_muted_flips_false_to_true(self):
        """GIVEN muted is False
        WHEN toggle_muted() called
        THEN returns True"""
        manager = StateManager()
        manager.save({})
        result = manager.toggle_muted()
        self.assertTrue(result)

    def test_toggle_muted_flips_true_to_false(self):
        """GIVEN muted is True
        WHEN toggle_muted() called
        THEN returns False"""
        manager = StateManager()
        manager.save({"muted": True})
        result = manager.toggle_muted()
        self.assertFalse(result)

    def test_toggle_muted_persists_to_disk(self):
        """GIVEN state toggled
        WHEN new StateManager loads from disk
        THEN reads correct muted value"""
        manager = StateManager()
        manager.save({})
        manager.toggle_muted()  # now True
        manager2 = StateManager()
        self.assertTrue(manager2.get_muted())

    def test_toggle_muted_twice_returns_to_original(self):
        """GIVEN muted is False
        WHEN toggle_muted() twice
        THEN returns False (back to original)"""
        manager = StateManager()
        manager.save({})
        manager.toggle_muted()  # True
        result = manager.toggle_muted()  # False
        self.assertFalse(result)

    def test_get_muted_handles_corrupt_state(self):
        """GIVEN carousel.json is corrupt
        WHEN get_muted() called
        THEN returns False (backup + empty dict)"""
        with open(self.state_file, "w") as f:
            f.write("{broken")
        manager = StateManager()
        result = manager.get_muted()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
