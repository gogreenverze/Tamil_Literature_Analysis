#!/bin/bash

# Create a working directory
WORK_DIR="$HOME/github_projects"
BACKUP_DIR="$HOME/github_backup_$(date +%Y%m%d_%H%M%S)"

# Create directories
mkdir -p "$WORK_DIR"
mkdir -p "$BACKUP_DIR"

# List of all your repositories
REPOS=(
    "https://github.com/gogreenverze/virtual-try-on.git"
    # Add all other repository URLs here
)

# Function to process each repository
process_repo() {
    local repo_url="$1"
    local repo_name=$(basename "$repo_url" .git)
    echo "Processing $repo_name..."

    # If repository exists locally
    if [ -d "$WORK_DIR/$repo_name" ]; then
        echo "Backing up existing repository..."
        cp -r "$WORK_DIR/$repo_name" "$BACKUP_DIR/$repo_name"
        cd "$WORK_DIR/$repo_name"
        echo "Updating existing repository..."
    else
        echo "Cloning repository..."
        cd "$WORK_DIR"
        git clone "$repo_url"
        cd "$repo_name"
    fi

    # Update author information
    git filter-branch --env-filter '
    if [ "$GIT_COMMITTER_EMAIL" = "arkprabha@MacBook-Air.local" ]
    then
        export GIT_COMMITTER_EMAIL="gogreenverze@gmail.com"
    fi
    if [ "$GIT_AUTHOR_EMAIL" = "arkprabha@MacBook-Air.local" ]
    then
        export GIT_AUTHOR_EMAIL="gogreenverze@gmail.com"
    fi
    ' --tag-name-filter cat -- --branches --tags

    # Push changes
    git push --force --all
    echo "Completed processing $repo_name"
    echo "----------------------------------------"
}

# Process each repository
for repo in "${REPOS[@]}"; do
    process_repo "$repo"
done

echo "All repositories have been processed!"
echo "Backups are stored in: $BACKUP_DIR"