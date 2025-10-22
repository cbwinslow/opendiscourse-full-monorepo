#!/bin/bash
# cleanup_directory.sh - Script to help clean up the OpenDiscourse directory structure

echo "=================================================="
echo "OpenDiscourse Directory Cleanup Assistant"
echo "=================================================="
echo ""
echo "This script will help you clean up the directory structure"
echo "by identifying potential cleanup targets."
echo ""
echo "⚠️  WARNING: This script identifies candidates for cleanup"
echo "   but does not delete anything automatically."
echo "   Always review the identified items before deleting."
echo ""

# Check if we're in the right directory
if [ ! -f "AGENT_SETUP_GUIDE.md" ]; then
    echo "❌ Error: This script should be run from the OpenDiscourse root directory"
    echo "Current directory contents:"
    ls -la
    exit 1
fi

echo "✅ OpenDiscourse directory confirmed"
echo ""

# 1. Identify large files
echo "🔍 1. Large files (>1MB):"
find . -type f -size +1M ! -path "./.git/*" -exec ls -lh {} \; | awk '{print $8 ": " $5}'
echo ""

# 2. Identify duplicate files
echo "🔍 2. Files that may be duplicates (same name, different locations):"
for file in $(find . -type f -exec basename {} \; | sort | uniq -d); do
    echo "Duplicated file: $file"
    find . -name "$file" -not -path "./.git/*" -exec ls -la {} \;
    echo ""
done
echo ""

# 3. Identify temporary files
echo "🔍 3. Temporary files:"
find . -type f -name "*.tmp" -o -name "*.temp" -o -name "*.bak" -o -name "*.backup" -not -path "./.git/*"
echo ""

# 4. Identify potentially unnecessary files
echo "🔍 4. Potentially unnecessary directories:"
echo "   - local_work_backup/: Contains original work (review before removal)"
ls -la local_work_backup/ 2>/dev/null || echo "   (directory not found)"
echo "   - local_backup/: Contains original files (review before removal)"
ls -la local_backup/ 2>/dev/null || echo "   (directory not found)"
echo ""

# 5. Identify documentation that might need consolidation
echo "🔍 5. Documentation in misc directory (may need consolidation):"
ls -la packages/docs/misc/ 2>/dev/null || echo "   (directory not found)"
echo ""

# 6. Identify Python cache files
echo "🔍 6. Python cache files:"
find . -type d -name "__pycache__" -not -path "./.git/*" | head -10
find . -type f -name "*.pyc" -not -path "./.git/*" | head -10
echo ""

# 7. Show the recommended cleanup based on TODO.md
echo "📋 7. Recommended cleanup actions from TODO.md:"
echo "   - Review local_work_backup/ and local_backup/"
echo "   - Consolidate files in packages/docs/misc/"
echo "   - Organize scripts in tools/scripts/main/"
echo "   - Audit requirements files for unused dependencies"
echo "   - Standardize naming conventions"
echo ""

# 8. Show the current project structure
echo "📊 8. Current project structure:"
tree -d -L 2 2>/dev/null || echo "tree command not available, showing with ls:"
ls -la

echo ""
echo "=================================================="
echo "Cleanup Recommendations:"
echo "=================================================="
echo "1. Review local_work_backup/ and local_backup/ - remove if content is preserved elsewhere"
echo "2. Move files from packages/docs/misc/ to more specific documentation directories"  
echo "3. Organize tools/scripts/main/ into more specific subdirectories"
echo "4. Remove Python cache files ( __pycache__, *.pyc)"
echo "5. Check for and remove any temporary files"
echo ""
echo "⚠️  Remember: Always backup important data before running actual deletions!"
echo "=================================================="