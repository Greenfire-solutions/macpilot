# Compatibility

## Tested
| OS | macpilot | notes |
|---|---|---|
| macOS 12.6.8 Monterey (x86_64) | ✅ works | click/drag/type/key/scroll/peek all verified |

## The macOS 13+ problem with computer-use MCP servers

Agent-native computer-use MCP servers are architecturally better than this tool — they are
accessibility-first with pixel fallback, expose native agent tools, and some act **without
moving your cursor or stealing focus**. If you are on macOS 13+, prefer them.

They do **not** run on macOS 12. Verified failure of `@qwen-code/open-computer-use`:

```
$ open-computer-use doctor
dyld[34377]: Symbol not found:
  (_$sSo6CGRectV6AppKitE4fill5usingySo22NSCompositingOperationV_tF)
  Referenced from: .../Open Computer Use.app/Contents/MacOS/OpenComputerUse
  Expected in: /System/Library/Frameworks/AppKit.framework/Versions/C/AppKit
```

The npm package installs and its Node CLI wrapper responds to `--help`, but every command
that touches the native engine (`doctor`, `list-apps`, `version`, `mcp`) crashes. The
bundled Swift/AppKit binary is built against a newer SDK than Monterey ships.

`computer-use-mcp` is likewise a Swift binary and generally expects a modern toolchain
(Monterey ships Swift 5.7.2), so treat it as macOS 13+ unless proven otherwise.

**Conclusion:** on macOS 12, macpilot/cliclick are not a fallback — they are the option.

## Architecture note
macpilot deliberately depends only on `ApplicationServices` and `Carbon`, both stable
since 10.x. That is why it builds on Monterey with the stock Command Line Tools.
