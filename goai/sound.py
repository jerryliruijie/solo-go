"""
Sound helper for solo-go.

Plays a short sound when a stone is placed.

- Primary (cross-platform): pygame.mixer plays 'assets/gostonesounds-sologo.wav'
  (supports OGG/WAV/MP3, low latency, no compiler needed).
- Fallbacks (keep legacy behavior):
    - Windows: winsound.Beep
    - Others: Tk master.bell() if provided, else no-op
- Never raises on failure; sound is non-critical.
"""

import sys
import pygame
from pathlib import Path

# Cache pygame init state to avoid reinit every click
_PYGAME_READY = False

def _sound_file():
    # project_root = goai/.. ; asset is at project_root / assets / gostonesounds-sologo.wav
    return Path(__file__).parent.parent / "assets" / "gostonesounds-sologo.wav"

def _try_play_with_pygame(sound_path: Path) -> bool:
    """Return True if played via pygame, else False."""
    global _PYGAME_READY
    try:
        # Init mixer once
        if not _PYGAME_READY:
            # Let pygame pick a default audio driver; keep tiny buffer for low latency
            pygame.mixer.init()
            _PYGAME_READY = True

        if sound_path.exists():
            snd = pygame.mixer.Sound(str(sound_path))
            snd.play()
            return True
        return False
    except Exception:
        return False

def play_move_sound(master=None):
    """
    Play a short sound to indicate a move was made.
    Keeps backward compatibility and never raises.
    """
    sound_path = _sound_file()

    # 1) Cross-platform preferred path (pygame, supports .ogg/.wav)
    if _try_play_with_pygame(sound_path):
        return

    # 2) Fallbacks match old minimal implementation behavior
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.Beep(800, 120)
        else:
            if master is not None:
                try:
                    master.bell()
                except Exception:
                    pass
    except Exception:
        pass

# Manual quick test: `python -m goai.sound`
if __name__ == "__main__":
    play_move_sound()
