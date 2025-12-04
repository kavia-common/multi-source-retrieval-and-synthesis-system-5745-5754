#!/bin/bash
cd /home/kavia/workspace/code-generation/multi-source-retrieval-and-synthesis-system-5745-5754/backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

