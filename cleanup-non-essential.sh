#!/bin/bash
# cleanup-non-essential.sh
# Script to identify and optionally remove non-essential files from the OpenDiscourse monorepo

echo "🔍 OpenDiscourse Cleanup Assistant"
echo "This script helps identify potentially non-essential files for cleanup"
echo ""

echo "📁 Essential directories (will NOT be removed):"
echo "  - packages/api/opendiscourse-core/"
echo "  - packages/data-collector/sources/"
echo "  - packages/data-collector/processing/"
echo "  - apps/web-client/"
echo "  - requirements/"
echo "  - packages/docs/research/"
echo "  - packages/docs/guides/"
echo ""

echo "🗑️  Potential non-essential files/directories to review:"
find . -name "*test*" -type d | grep -v ".git" | head -10
echo ""
find . -name "*example*" -type d | grep -v ".git" | head -10
echo ""
find . -name "*backup*" -type d | grep -v ".git" | head -10
echo ""
find . -name "*temp*" -type d | grep -v ".git" | head -10
echo ""

echo "📝 To remove non-essential files, you can run commands like:"
echo "  rm -rf path/to/non/essential/directory"
echo ""
echo "💡 Tip: Always backup important work before running cleanup operations"
echo ""
echo "📋 Recommended safe cleanup operations:"
echo "  1. Remove local_work_backup/ if you've reviewed its contents"
echo "  2. Review and selectively remove experimental/unused packages"
echo "  3. Remove temporary files and duplicates"
echo ""