# Optional backends

macpilot needs nothing here. These are alternatives worth knowing about.

## cliclick
Mature Objective-C CLI with the same CGEvent approach. More complete key handling than
macpilot; no `peek` and no Retina scale reporting.

```bash
brew install cliclick                       # if you have Homebrew
# no Homebrew? build from source - needs only Command Line Tools:
git clone --depth 1 https://github.com/BlueM/cliclick.git
cd cliclick && make && cp cliclick ~/.local/bin/
```
MIT licensed. Not vendored here on purpose: prebuilt binaries are arch-specific and
carry no provenance. Build it yourself.

## computer-use MCP servers (macOS 13+ only)
See ../docs/compatibility.md - verified NOT to run on macOS 12.
