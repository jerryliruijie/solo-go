import importlib
import os
import sys
from pathlib import Path
import types
import pytest

MODULE_PATH = "goai.sound_dev"

def _reload_sound_module():
    if MODULE_PATH in sys.modules:
        importlib.reload(sys.modules[MODULE_PATH])
    else:
        importlib.import_module(MODULE_PATH)
    return sys.modules[MODULE_PATH]

class FakePygameOK:
    """pygame 正常可用：记录是否播放过"""
    def __init__(self):
        # mixer 对象，模拟 init / get_init / pre_init
        self.mixer = types.SimpleNamespace(
            _inited=False,
            init=self._init,
            get_init=lambda: self.mixer._inited,
            pre_init=lambda *a, **k: None,
        )
        self._played = False

        class _Sound:
            def __init__(_, path):
                self.last_sound_path = path
            def play(_):
                self._played = True
                return types.SimpleNamespace(get_busy=lambda: False)
            def set_volume(_, v):
                pass

        # 关键：真实 pygame 是 pygame.mixer.Sound
        self.Sound = _Sound
        self.mixer.Sound = _Sound

    def _init(self, *a, **k):
        self.mixer._inited = True

class FakePygameFailInit:
    """pygame 存在但初始化失败，引导走 fallback"""
    def __init__(self):
        def _init(*a, **k):
            raise RuntimeError("mixer init failed")
        self.mixer = types.SimpleNamespace(
            _inited=False,
            init=_init,
            get_init=lambda: False,
            pre_init=lambda *a, **k: None,
        )
        class _Sound:
            def __init__(_, path): pass
            def play(_): pass
            def set_volume(_, v): pass
        self.Sound = _Sound

class FakeWinSound:
    def __init__(self):
        self.beep_calls = []
        self.playsound_calls = []
    def Beep(self, f, d):
        self.beep_calls.append((f, d))
    def PlaySound(self, filename, flags):
        self.playsound_calls.append((filename, flags))

class PathExistsSwitcher:
    """
    monkeypatch Path.exists(): 对特定文件名返回 True，其他按原逻辑。
    """
    def __init__(self, monkeypatch, want_name):
        self.real_exists = Path.exists
        self.want_name = want_name
        def fake_exists(p: Path):
            try:
                if p.name == self.want_name:
                    return True
            except Exception:
                pass
            return self.real_exists(p)
        monkeypatch.setattr(Path, "exists", fake_exists, raising=False)

def test_pygame_primary_plays_when_available(monkeypatch):
    """
    有 pygame 且目标文件存在时，应该通过 pygame 播放。
    """
    # 环境准备：跨平台测试，不依赖真实文件
    os.environ["GO_SOUND_FILE"] = "assets/gostonesounds-sologo.ogg"
    PathExistsSwitcher(monkeypatch, want_name="gostonesounds-sologo.ogg")

    # 注入可用的 pygame
    fake_pg = FakePygameOK()
    monkeypatch.setitem(sys.modules, "pygame", fake_pg)

    # 确保 winsound 不影响该用例
    if "winsound" in sys.modules:
        del sys.modules["winsound"]

    # 平台设为非 Windows（无所谓，pygame 优先生效）
    monkeypatch.setattr(sys, "platform", "linux")

    sound = _reload_sound_module()
    sound.play_move_sound(master=None)

    assert fake_pg.mixer.get_init() is True
    # 断言通过 pygame 播放了
    assert fake_pg.__dict__.get("_played", False) is True

def test_windows_fallback_beep_when_pygame_fails_and_wav(monkeypatch):
    """
    pygame 失败 + Windows + 目标是 .wav 时，当前实现应退回 winsound.Beep。
    （若将来实现 winsound.PlaySound，可改为断言 PlaySound）
    """
    os.environ["GO_SOUND_FILE"] = "assets/gostonesounds-sologo.wav"
    PathExistsSwitcher(monkeypatch, want_name="gostonesounds-sologo.wav")

    # pygame 存在但初始化失败
    monkeypatch.setitem(sys.modules, "pygame", FakePygameFailInit())

    # 注入 winsound
    fw = FakeWinSound()
    monkeypatch.setitem(sys.modules, "winsound", fw)

    # Windows 平台
    monkeypatch.setattr(sys, "platform", "win32")

    sound = _reload_sound_module()
    sound.play_move_sound(master=None)

    # 断言 Beep（当前实现）
    assert fw.beep_calls == [(800, 120)]
    assert fw.playsound_calls == []

def test_windows_fallback_beep_when_not_wav(monkeypatch):
    """
    pygame 失败 + Windows + 目标不是 .wav（例如 .ogg）时，winsound.PlaySound 不可用，
    应退回 winsound.Beep。
    """
    os.environ["GO_SOUND_FILE"] = "assets/gostonesounds-sologo.ogg"
    PathExistsSwitcher(monkeypatch, want_name="gostonesounds-sologo.ogg")

    # pygame 失败
    monkeypatch.setitem(sys.modules, "pygame", FakePygameFailInit())

    fw = FakeWinSound()
    monkeypatch.setitem(sys.modules, "winsound", fw)

    monkeypatch.setattr(sys, "platform", "win32")

    sound = _reload_sound_module()
    sound.play_move_sound(master=None)

    assert fw.playsound_calls == []
    assert fw.beep_calls == [(800, 120)]

def test_non_windows_fallback_tk_bell(monkeypatch):
    """
    非 Windows + pygame 失败 → 若提供 master，调用 master.bell()
    """
    os.environ["GO_SOUND_FILE"] = "assets/gostonesounds-sologo.wav"
    PathExistsSwitcher(monkeypatch, want_name="gostonesounds-sologo.wav")

    # pygame 失败
    monkeypatch.setitem(sys.modules, "pygame", FakePygameFailInit())

    # 非 Windows
    monkeypatch.setattr(sys, "platform", "linux")

    # 不加载 winsound
    if "winsound" in sys.modules:
        del sys.modules["winsound"]

    class DummyMaster:
        def __init__(self):
            self.bell_called = False
        def bell(self):
            self.bell_called = True

    master = DummyMaster()

    sound = _reload_sound_module()
    sound.play_move_sound(master=master)

    assert master.bell_called is True

def test_non_windows_no_master_no_raise(monkeypatch):
    """
    非 Windows + pygame 失败 + 没有 master 时，应该静默无异常（no-op）。
    """
    os.environ["GO_SOUND_FILE"] = "assets/gostonesounds-sologo.wav"
    PathExistsSwitcher(monkeypatch, want_name="gostonesounds-sologo.wav")

    monkeypatch.setitem(sys.modules, "pygame", FakePygameFailInit())
    monkeypatch.setattr(sys, "platform", "linux")
    if "winsound" in sys.modules:
        del sys.modules["winsound"]

    sound = _reload_sound_module()
    # 不应抛异常
    sound.play_move_sound(master=None)
