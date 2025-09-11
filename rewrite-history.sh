#!/bin/bash

# Script to rewrite git history and translate Russian commit messages to English

echo "Starting git history rewrite..."

# Use git filter-branch to rewrite commit messages
git filter-branch --force --msg-filter '
if echo "$GIT_COMMIT" | grep -q "78c0875"; then
    echo "Release v1.0.4: Repository cleanup and documentation improvements"
elif echo "$GIT_COMMIT" | grep -q "Очистка репозитория"; then
    echo "Release v1.0.4: Repository cleanup and documentation improvements"
else
    cat
fi
' --tag-name-filter cat -- --all

echo "Git history rewrite completed."