# Optional: the ready-made bin/macpilot is already in this folder (Intel + Apple Silicon).
# Rebuilding needs Apple's free Command Line Tools: xcode-select --install
BIN     := bin/macpilot
SRC     := core/macpilot.c
CFLAGS  := -O2 -Wall -arch x86_64 -arch arm64 -mmacosx-version-min=11.0
FRAMEWORKS := -framework ApplicationServices -framework Carbon

.PHONY: all clean install check test
all: $(BIN)

$(BIN): $(SRC)
	@mkdir -p bin
	clang $(CFLAGS) -o $@ $(SRC) $(FRAMEWORKS)
	codesign --force -s - $@
	@lipo -info $@
	@echo "built $@"

check: $(BIN)
	@./$(BIN) screen
	@./$(BIN) pos
	@./$(BIN) access || true

test:
	python3 tests/test_safe.py

install: $(BIN)
	@mkdir -p $(HOME)/.local/bin
	cp $(BIN) $(HOME)/.local/bin/macpilot
	@echo "installed to ~/.local/bin/macpilot"

clean:
	rm -f $(BIN)
