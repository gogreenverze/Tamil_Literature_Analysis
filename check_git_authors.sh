#!/bin/bash

# Directory containing all your repositories
BASE_DIR="$HOME/your/repos/directory"

echo "Checking Git authors across all repositories..."
echo "---------------------------------------------"

for repo in $(find "$BASE_DIR" -name ".git" -type d -prune); do
    repo_path=$(dirname "$repo")
    echo "Repository: $repo_path"
    echo "Authors:"
    cd "$repo_path"
    git log --pretty=format:"%an <%ae>" | sort -u
    echo "---------------------------------------------"
done