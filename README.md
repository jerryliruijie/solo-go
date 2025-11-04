# Solo-Go

一个用 Python 实现的迷你围棋项目（教学/练手用），包含终端与图形界面（tkinter）、基本规则判断与简单 AI。目标是做一个易于扩展的本地围棋练习工具。

## 目录
- goai/         — 核心模块（board, ai, game_manager, gui）
- tests/        — pytest 测试用例
- run_tests.py  — 统一测试入口
- README.md     — 项目说明（你现在看到的）
  
## 已实现（功能）
- 棋盘与规则核心
  - Board 类：棋盘表示、落子、提子（捕获）、气与联通块的判定、自杀判定（自杀着法被拒绝）。
  - 落子接口 `place(r, c, color)` 与合法性查询 `is_legal(r, c, color)`。
- 对局控制
  - GameManager：回合控制、落子流程、当某方无合法着法时按“认输”结束对局（项目当前不允许 pass）。
- AI
  - SimpleAI：基础随机（或简单启发）AI，返回合法着法或 None（无合法着法）。
- 图形界面
  - tkinter GUI（19x19 默认）：棋盘绘制、星位、鼠标点击落子、禁止 Pass 按钮、Reset 重开局、与 AI 人机对弈。
- 测试与 CI 支持（本地）
  - pytest 测试套件覆盖 Board、AI、GameManager；tests/test_sound.py 覆盖音效逻辑（mock）。
  - `run_tests.py`：统一运行所有 pytest 测试的入口脚本。
- 声音（部分实现）
  - 设计了跨平台音效接口 `goai/sound.py`（Windows 用 winsound.Beep，非 Windows 使用 Tk bell；此文件已加入但请确认具体音频文件/效果是否满足需求）。

## 尚未实现（用户列出的重点改进项）
下面列出你提到的 6 项及额外实现建议，按优先级给出说明与建议实现方式。

1) 一个能正常对弈的 AI（部署在程序里面）
- 状态：未完成 / 当前为基础 SimpleAI（随机合法着法）。
- 优先级：高
- 建议：
  - 先实现基于启发式的规则（优先吃子、避免自杀、连接己子等）作为短期提升。
  - 中期：实现蒙特卡洛树搜索（MCTS）或基于 UCT 的搜索；借助现有库或自行实现轻量版。
  - 提供可选开关：level=0/1/2，对应随机/启发式/MCTS。

2) 更好的落子音效（“去找一个”）
- 状态：目前实现了简单 cross-platform 接口和 Windows/Tk 的退化方案，但未加入具体 WAV 音效文件或更好音源。
- 优先级：中
- 建议：
  - 找一个合适的短音效（例如 click.wav 或 stone.wav，CC0 或合适授权），放在项目 `assets/sounds/` 下。
  - 使用 `simpleaudio` 或 `pygame` 播放 WAV（跨平台、低延迟），在 `goai/sound.py` 中实现并保持 play_move_sound(master=None) 接口向后兼容。
  - 补充 tests/test_sound.py 用 mock 覆盖库调用。

3) “退出棋局”按钮（而不是只依赖窗口关闭）
- 状态：未实现（当前只有 Reset）
- 优先级：中低（可视需求）
- 建议：
  - 在 GUI 添加 `Quit Game` 按钮，明确触发确认对话框（是否保存/退出）。
  - 在 GUI 中实现回调：若你后续实现了对局保存/SGF 导出，可把 “Quit” 与保存步骤关联。

4) 更精美的棋子（UI 美化）
- 状态：未实现
- 优先级：低（UI 改进）
- 建议：
  - 将 Canvas 的石子替换为图片（PNG）或使用带阴影的绘制（双重圆环、渐变）。
  - 把棋盘背景替换为木纹图、添加坐标标签、边栏信息（剩余时间、吃子数）。
  - 考虑引入前端（Web）界面（例如使用 Flask + JS/Canvas），但那是较大改动。

5) 实时计算胜率（对局中）
- 状态：未实现
- 优先级：中高（如果你想做 AI 助手）
- 建议：
  - 若使用 MCTS，可在 AI 空闲时运行 rollouts 并将 win-rate 作为胜率估计显示（例如在状态栏以百分比显示当前玩家胜率）。
  - 也可使用网络化现成模型（如神经网络评估器）来估计局面价值（复杂度高，需额外依赖和模型文件）。
  - 在 GUI 增加一个显示胜率的区域，并异步计算以避免阻塞 UI。

6) 使用中国规则结算胜负（计分）
- 状态：未实现
- 优先级：中
- 建议：
  - 实现两种计分方法（中国/日本）或先实现中国规则（中国规则：地力 + 提子）。
  - 需要实现：区域判定（空点归属）、死子确认或复盘阶段让双方确认死子、计算贴目（komi）。
  - 在 GameManager 中添加终局计分接口并在 GUI 里提供“结束对局并计分”按钮。

## 其它建议与注意事项
- KO 与对局历史：当前未记录历史（因此不处理劫争/重复局面），强烈建议在实现完整对局后增加历史记录与 KO 判定（可以先只实现简单单劫）。
- 单元测试：新增或修改核心逻辑时请先补充对应的 pytest 测试并通过 `python run_tests.py`。
- 分支与提交策略：
  - feature/gui-and-tests-before-sound：当前主开发分支（GUI + tests）。
  - feature/add-sound：音效改动在独立分支（便于回退与审查）。
  - feature/ai-mcts：实现更强 AI 的独立分支。
- 许可与贡献：在 README 顶部注明开源协议（MIT / Apache / GPL），并说明如何贡献（Fork -> branch -> PR）。

## 如何运行（快速说明）
- 依赖：Python 3.8+；Linux 需安装 `python3-tk`。
- 运行 GUI：
  - 在项目根（含 goai/）执行：
    ```bash
    python -m goai.gui
    ```
- 运行测试：
  - 安装 pytest： `pip install pytest`
  - 运行全部测试： `python run_tests.py` 或 `python -m pytest -q`

