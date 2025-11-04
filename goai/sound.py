"""
Sound helper for solo-go.

Provides a simple play_move_sound(master=None) function which plays a short sound
when a stone is placed. Implementation is minimal and dependency-free:

- On Windows: uses winsound.Beep for a short beep.
- On other platforms: uses the provided Tk master.bell() if master is given,
  otherwise falls back to a no-op.

This file is intentionally small so you can replace its internals later to play
WAV files or use libraries like simpleaudio/pygame without touching GUI code.
"""
import sys

def play_move_sound(master=None):
    """
    Play a short sound to indicate a move was made.
    - master: optional Tk root or widget; if provided on non-Windows,
      master.bell() will be used to ring the system bell.
    """
    try:
        if sys.platform.startswith("win"):
            # winsound is Windows-only and part of stdlib
            import winsound
            # Short beep: frequency 800Hz, duration 120ms
            winsound.Beep(800, 120)
        else:
            # On other platforms use Tk bell if available
            if master is not None:
                try:
                    master.bell()
                except Exception:
                    # If bell fails, silently ignore
                    pass
            else:
                # No master provided; nothing we can reliably play without extra deps
                pass
    except Exception:
        # Never raise from sound playing; it's non-critical
        pass