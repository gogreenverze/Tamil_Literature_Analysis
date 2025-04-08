#!/bin/bash

# Create a working directory
WORK_DIR="$HOME/github_projects"

# Create directory if it doesn't exist
mkdir -p "$WORK_DIR"

# List of all your repositories
REPOS=(
    "https://github.com/gogreenverze/virtual-try-on.git"
    "https://github.com/gogreenverze/housegenie.git"
    "https://github.com/gogreenverze/smart-attendai-cctv.git"
    "https://github.com/gogreenverze/tamil-sundari-sollu-aai.git"
    "https://github.com/gogreenverze/pedalverse-rewards-nft.git"
    "https://github.com/gogreenverze/email-ai-nexus.git"
    "https://github.com/gogreenverze/HomeMaker.git"
    "https://github.com/gogreenverze/greenlight-control.git"
    "https://github.com/gogreenverze/ip-nft-exchange.git"
    "https://github.com/gogreenverze/eco-sentinel-mrv.git"
    "https://github.com/gogreenverze/traveliscope.git"
    "https://github.com/gogreenverze/digital-mrv-clone.git"
    "https://github.com/gogreenverze/housegenius-procure-3d.git"
    "https://github.com/gogreenverze/smartdesign-automator-ff89331f.git"
    "https://github.com/gogreenverze/SmartExchange.git"
    "https://github.com/gogreenverze/ExpenseTracker.git"
    "https://github.com/gogreenverze/shopwhiz-integration.git"
    "https://github.com/gogreenverze/smartdesign-automator.git"
    "https://github.com/gogreenverze/browse-nest-360.git"
    "https://github.com/gogreenverze/talkverse-app.git"
    "https://github.com/gogreenverze/GoGreenTec_WebApp.git"
    "https://github.com/gogreenverze/hrmgo.git"
    "https://github.com/gogreenverze/3d-farm-orchard.git"
    "https://github.com/gogreenverze/GoGreenVerz_WebSite.git"
    "https://github.com/gogreenverze/ProducerBazaar_GGV.git"
    "https://github.com/gogreenverze/MetaVerse_MarketPlace_NextJs.git"
    "https://github.com/gogreenverze/MetaVerse_GG_Javascript.git"
    "https://github.com/gogreenverze/AdminPanel_ProducerBazaar_GG.git"
    "https://github.com/gogreenverze/GPI_Dashboard.git"
    "https://github.com/gogreenverze/Dockal_NFT_Creation_Redirection_Site.git"
)

# Function to check commit history
check_history() {
    local repo_url="$1"
    local repo_name=$(basename "$repo_url" .git)
    echo "======================================================"
    echo "Checking history for: $repo_name"
    echo "======================================================"

    # If repository exists locally
    if [ -d "$WORK_DIR/$repo_name" ]; then
        cd "$WORK_DIR/$repo_name"
        git pull
    else
        cd "$WORK_DIR"
        git clone "$repo_url"
        cd "$repo_name"
    fi

    # Show all unique authors and their email addresses
    echo "Unique authors and their email addresses:"
    git log --pretty=format:"%an <%ae>" | sort | uniq
    echo -e "\n"

    # Show detailed commit history
    echo "Last 10 commits:"
    git log -n 10 --pretty=format:"%h - %an <%ae> - %s" --date=short
    echo -e "\n\n"
}

# Process each repository
for repo in "${REPOS[@]}"; do
    check_history "$repo"
done

echo "All repositories have been checked!"