# OpenDiscourse Project - Task List and Cleanup Guide

## 🎯 Current Task List

### High Priority Tasks
- [ ] Implement core data collection API endpoints in `packages/api/opendiscourse-core/`
- [ ] Create unified data schema for all government data sources
- [ ] Set up database migrations in `packages/infrastructure/database-migrations/`
- [ ] Implement basic data validation in `packages/data-collector/processing/`

### Medium Priority Tasks
- [ ] Enhance RAG engine with better document chunking in `packages/rag-engine/`
- [ ] Create comprehensive API documentation in `packages/docs/api/`
- [ ] Set up CI/CD pipeline for automated testing
- [ ] Add comprehensive unit tests to `packages/shared/testing/`

### Low Priority Tasks
- [ ] Design improved UI components in `packages/web/`
- [ ] Implement advanced analytics dashboards
- [ ] Create user management system
- [ ] Add more government data sources

---

## 🧹 Directory Cleanup Tasks

### Tasks to Complete
- [ ] Review and remove `local_work_backup/` after confirming content is preserved elsewhere
- [ ] Archive or remove `local_backup/` if content is no longer needed
- [ ] Consolidate duplicate documentation files across packages
- [ ] Move temporary/intermediate files to appropriate directories or remove
- [ ] Review and potentially remove experimental packages not in use
- [ ] Audit and clean up requirements files to remove unused dependencies
- [ ] Standardize naming conventions across all directories and files
- [ ] Remove large binary files or move to git LFS if needed

### Files to Review
- [ ] `packages/docs/misc/` - Review for files that can be moved to more specific locations
- [ ] `tools/scripts/main/` - Organize scripts into more specific subdirectories
- [ ] `external-sources/` - Verify all repositories are actively needed
- [ ] `packages/infrastructure/` - Consolidate configuration files where possible

### Organization Tasks
- [ ] Ensure all Python modules have appropriate `__init__.py` files
- [ ] Verify all packages have README.md files explaining their purpose
- [ ] Check that all important functions and classes have docstrings
- [ ] Standardize configuration file formats across the project
- [ ] Ensure consistent import styles across Python files

---

## 📋 Cleanup Guidelines

### Before Removing Any Files
1. **Backup**: Always create a backup before removing files
2. **Verify**: Check if files are referenced elsewhere in the codebase
3. **Test**: Verify that removing the files doesn't break functionality
4. **Document**: Record why files were removed in the CHANGELOG.md

### Safe to Remove
- Temporary files with extensions like `.tmp`, `.temp`, `.bak`
- Local configuration files that might contain secrets
- Large binary files that can be regenerated
- Duplicate files where the original is preserved

### Keep Always
- Core functionality in `packages/` directories
- Documentation files in `packages/docs/`
- Configuration files in root and `packages/shared/config/`
- External repositories in `external-sources/` that provide reference implementations
- All test files and testing utilities

---

## 🔧 Recommended Cleanup Process

1. **Backup Current State**: Create a backup of the repo before making changes
   ```bash
   tar -czf opendiscourse-backup-$(date +%Y%m%d).tar.gz --exclude='.git' .
   ```

2. **Review Local Backups**: Check if `local_work_backup/` and `local_backup/` have content that's already preserved elsewhere

3. **Consolidate Documentation**: Move files from `packages/docs/misc/` to more appropriate locations

4. **Audit Dependencies**: Review and update the requirements files

5. **Standardize Structure**: Ensure all packages follow similar internal structure

6. **Update Documentation**: Update README files after cleanup is complete

---

## 🚨 Cleanup Warnings

⚠️ **DO NOT DELETE**:
- Any files in `packages/api/opendiscourse-core/` - core functionality
- Any files in `packages/data-collector/` - essential data collection
- Any external repositories in `external-sources/` - reference implementations
- Any research documents in `packages/docs/research/` - important for context
- Any configuration files in `packages/shared/config/` - needed for operation

⚠️ **Review Carefully Before Deleting**:
- Files in `packages/docs/misc/` - may contain useful information
- Any experimental packages - may be needed for future development
- Large files - may be needed but could be moved to LFS
- Local configuration files - may contain important settings