BIN     := bin/macpilot
SRC     := core/macpilot.c
CFLAGS  := -O2 -Wall
FRAMEWORKS := -framework ApplicationServices -framework Carbon

.PHONY: all clean install check
all: $(BIN)

$(BIN): $(SRC)
	@mkdir -p bin
	clang $(CFLAGS) -o $@ $(SRC) $(FRAMEWORKS)
	@echo "built $@"

check: $(BIN)
	@./$(BIN) screen
	@./$(BIN) pos

install: $(BIN)
	@mkdir -p $(HOME)/.local/bin
	cp $(BIN) $(HOME)/.local/bin/macpilot
	@echo "installed to ~/.local/bin/macpilot"

clean:
	rm -rf bin
