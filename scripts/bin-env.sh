#!/usr/bin/env bash
# Print a line you can add to your shell rc to include the project's scripts/ in PATH
if [ "$1" = "--install" ]; then
  LINE="export PATH=\"$(pwd)/scripts:\$PATH\""
  echo "$LINE" >> ~/.bashrc
  echo "Added to ~/.bashrc"
else
  echo "Run this to add scripts/ to your PATH:"
  echo "export PATH=\"$(pwd)/scripts:\$PATH\""
fi
