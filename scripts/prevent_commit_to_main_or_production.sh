#!/bin/bash

BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$BRANCH" = "main" ] || [[ "$BRANCH" == production* ]]; then
  echo ">> Commit blocked on branch '$BRANCH'."
  echo ">> Please create a new branch, commit there, and open a Pull Request."
  exit 1
fi
