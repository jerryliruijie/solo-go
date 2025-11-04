import importlib
import sys

import pytest

# We import the module under test lazily inside tests so that we can monkeypatch
# sys.platform and sys.modules before it is imported.
MODULE_PATH = "goai.sound"


def _reload_sound_module():
    if MODULE_PATH in sys.modules:
        importlib.reload(sys.modules[MODULE_PATH])
    else:
        importlib.import_module(MODULE_PATH)
    return sys.modules[MODULE_PATH]


def test_play_move_sound_windows(monkeypatch):
    """
    On Windows the implementation should import winsound and call winsound.Beep
    with (800, 120). We simulate Windows by setting sys.platform and injecting
    a fake winsound module into sys.modules.
    """
    # Create a fake winsound module with a Beep that records calls
    class FakeWinSound:
        def __init__(self):
            self.calls = []

        def Beep(self, freq, duration):
            self.calls.append((freq, duration))

    fake = FakeWinSound()

    # Ensure sound module is reloaded with platform='win32' and our fake winsound
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setitem(sys.modules, "winsound", fake)

    sound = _reload_sound_module()
    # Call the function; it should call our fake.Beep
    sound.play_move_sound(master=None)

    assert getattr(fake, "calls", []) == [(800, 120)]


def test_play_move_sound_non_windows_with_master(monkeypatch):
    """
    On non-Windows platforms, if a Tk master is provided, play_move_sound should
    call master.bell(). We simulate a master object that records whether bell()
    was called.
    """
    monkeypatch.setattr(sys, "platform", "linux")

    class DummyMaster:
        def __init__(self):
            self.bell_called = False

        def bell(self):
            self.bell_called = True

    master = DummyMaster()

    sound = _reload_sound_module()
    sound.play_move_sound(master=master)

    assert master.bell_called is True


def test_play_move_sound_non_windows_no_master(monkeypatch):
    """
    On non-Windows platforms, if no master is provided, function should be a no-op
    (i.e. not raise). This ensures sound playing never breaks program flow.
    """
    monkeypatch.setattr(sys, "platform", "linux")
    sound = _reload_sound_module()

    # Should not raise
    sound.play_move_sound(master=None)