.PHONY: export-conversations show-scripts-path

# Export conversations for a user (by id). Usage:
#   make export-conversations USERID=42 OUT=user_42.csv
export-conversations:
	@if [ -z "$(USERID)" ]; then \
		echo "Usage: make export-conversations USERID=<id> OUT=<file>"; exit 1; \
	fi
	@OUT=${OUT:-user_$(USERID).csv}; \
	python3 scripts/export_conversations.py --db users.db --userid $(USERID) --out $$OUT; \
	echo "Wrote $$OUT"

# Print a line you can add to your shell rc to include the project's scripts/ in PATH
show-scripts-path:
	@echo "Add the following line to your ~/.bashrc or ~/.profile to include the project's scripts in PATH:";
	@echo "export PATH=\"$$(pwd)/scripts:$$PATH\""
