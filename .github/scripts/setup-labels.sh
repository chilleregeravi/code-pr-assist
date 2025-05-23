#!/bin/bash

# Setup GitHub labels for Dependabot auto-merge workflow
# Run this script once to create the required labels in your repository

set -e

echo "🏷️  Setting up GitHub labels for Dependabot auto-merge workflow..."

# Colors for labels (using GitHub's standard color palette)
AUTO_MERGE_COLOR="0E8A16"      # Green
MANUAL_REVIEW_COLOR="D93F0B"   # Red
PATCH_COLOR="FBCA04"           # Yellow
MINOR_COLOR="0052CC"           # Blue
MAJOR_COLOR="B60205"           # Dark Red
DEPENDENCIES_COLOR="0366D6"    # GitHub Blue

# Create or update labels
echo "Creating labels..."

# Auto-merge label
gh label create "auto-merge" \
    --description "PRs that can be automatically merged" \
    --color "$AUTO_MERGE_COLOR" \
    --force

# Manual review label
gh label create "manual-review" \
    --description "PRs that require manual review before merging" \
    --color "$MANUAL_REVIEW_COLOR" \
    --force

# Update type labels
gh label create "patch-update" \
    --description "Patch version update (backwards compatible bug fixes)" \
    --color "$PATCH_COLOR" \
    --force

gh label create "minor-update" \
    --description "Minor version update (backwards compatible new features)" \
    --color "$MINOR_COLOR" \
    --force

gh label create "major-update" \
    --description "Major version update (may contain breaking changes)" \
    --color "$MAJOR_COLOR" \
    --force

# Update existing dependencies label if it exists
gh label create "dependencies" \
    --description "Pull requests that update a dependency file" \
    --color "$DEPENDENCIES_COLOR" \
    --force

echo "✅ Labels created successfully!"
echo ""
echo "📋 Created labels:"
echo "   🟢 auto-merge       - For automatic merging"
echo "   🔴 manual-review    - For manual review required"
echo "   🟡 patch-update     - For patch version updates"
echo "   🔵 minor-update     - For minor version updates"
echo "   🔴 major-update     - For major version updates"
echo "   🔵 dependencies     - For dependency updates"
echo ""
echo "🚀 Auto-merge workflow is now ready to use!"
