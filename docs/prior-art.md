# macOS UI automation - what already exists (researched Sep 2026)

## CLI tools (same approach as macpilot)
- **cliclick** — https://github.com/BlueM/cliclick
  Objective-C, CGEvent-based, `brew install cliclick`, macOS 10.15+. Mature and more
  complete than macpilot (has wait/rich key handling). Syntax: `cliclick c:123,456`.
  **If you want a maintained dependency, use this.** macpilot's additions are `peek`
  (accessibility introspection under a point) and explicit Retina scale reporting.
- **Hammerspoon** — Lua scripting for macOS; best for persistent hotkeys and daemons.
- **AppleScript / System Events** — built in, but **cannot click Chromium/CEF apps**.
- **Sikuli** — image-recognition-driven clicking; heavier, JVM.

## Agent-native MCP servers (best option for repeated agent use)
- **computer-use-mcp** — https://github.com/minghinmatthewlam/computer-use-mcp
  Agent-agnostic. Accessibility-first with automatic pixel fallback (z-order hit-testing)
  for apps with poor/absent AX trees — exactly the CapCut problem. Notably its input
  ladder can deliver actions **without moving the real cursor or stealing focus**, so the
  user keeps working while the agent works. macpilot cannot do that.
- **macOS-MCP** — https://github.com/CursorTouch/MacOS-MCP  Lightweight, AX-native.
- **Open Computer Use (QwenLM)** — https://github.com/QwenLM/open-computer-use
  Cross-platform (macOS/Linux/Windows), npm-installable.
- **mcp-server-macos-use** — https://github.com/mediar-ai/mcp-server-macos-use  Swift, MacosUseSDK.

## Trade-off
| | macpilot | cliclick | MCP server |
|---|---|---|---|
| Dependencies | none (one .c file) | Homebrew | node/swift + config |
| Agent tool access | shell out | shell out | native tools |
| Accessibility-aware | `peek` only | no | yes, with fallback |
| Works without stealing focus | no | no | some |
| Maintained by someone else | no | yes | yes |

Use **macpilot** for zero-dependency, works-right-now control.
Use an **MCP server** if this becomes a regular workflow.
