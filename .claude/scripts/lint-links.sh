#!/usr/bin/env bash
# Link linting script for knowledge garden
# Checks for broken links and suggests improvements

set -euo pipefail

GARDEN_DIR=".claude"
ERRORS=0
WARNINGS=0

echo "🔍 Linting knowledge garden links..."
echo ""

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check for broken markdown links
echo "📋 Checking for broken links..."
while IFS= read -r file; do
    # Extract markdown links: [text](path)
    while IFS= read -r link; do
        # Extract the path from [text](path)
        path=$(echo "$link" | sed -n 's/.*(\(.*\)).*/\1/p')

        # Skip external links (http/https)
        if [[ "$path" =~ ^https?:// ]]; then
            continue
        fi

        # Skip anchors
        if [[ "$path" =~ ^# ]]; then
            continue
        fi

        # Resolve relative path
        dir=$(dirname "$file")
        target="$dir/$path"

        # Normalize path (remove ../ and ./)
        target=$(cd "$dir" && realpath -m "$path" 2>/dev/null || echo "$target")

        # Check if file exists
        if [[ ! -f "$target" ]]; then
            echo -e "${RED}✗${NC} Broken link in $file:"
            echo "  Link: $link"
            echo "  Target: $target"
            echo ""
            ((ERRORS++))
        fi
    done < <(grep -o '\[.*\](.*\.md)' "$file" 2>/dev/null || true)
done < <(find "$GARDEN_DIR" -name "*.md" -type f)

# Check for plain text references that should be links
echo "📝 Checking for plain text references..."
while IFS= read -r file; do
    # Look for patterns like "See file.md" or "See path/file.md"
    while IFS= read -r line_num; do
        line=$(sed -n "${line_num}p" "$file")

        # Skip if already a markdown link
        if [[ "$line" =~ \[.*\]\(.*\) ]]; then
            continue
        fi

        # Check for plain references
        if [[ "$line" =~ (See|see|Check|check|Refer to|refer to)[[:space:]]+\`?([a-zA-Z0-9_/-]+\.md)\`? ]]; then
            echo -e "${YELLOW}⚠${NC}  Plain text reference in $file:$line_num"
            echo "  Line: $line"
            echo "  Suggestion: Convert to [@filename](path/to/file.md)"
            echo ""
            ((WARNINGS++))
        fi
    done < <(grep -n "\.md" "$file" | cut -d: -f1)
done < <(find "$GARDEN_DIR" -name "*.md" -type f)

# Check for files without Related sections
echo "🔗 Checking for files without Related sections..."
while IFS= read -r file; do
    if ! grep -q "^## Related" "$file"; then
        echo -e "${YELLOW}⚠${NC}  No Related section: $file"
        ((WARNINGS++))
    fi
done < <(find "$GARDEN_DIR" -name "*.md" -type f ! -name "README.md" ! -name "INDEX.md")

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
    echo -e "${GREEN}✓${NC} All checks passed!"
elif [[ $ERRORS -eq 0 ]]; then
    echo -e "${YELLOW}⚠${NC}  $WARNINGS warnings found"
    echo "  Consider addressing warnings to improve knowledge graph"
else
    echo -e "${RED}✗${NC} $ERRORS errors, $WARNINGS warnings"
    echo "  Fix errors before committing"
    exit 1
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
