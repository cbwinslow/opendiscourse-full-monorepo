# Jira Integration Setup

## 1. Required Secrets
- `JIRA_BASE_URL`: Your Jira site URL (e.g., https://your-domain.atlassian.net)
- `JIRA_USER_EMAIL`: Your Jira user email
- `JIRA_API_TOKEN`: Your Jira API token (create at https://id.atlassian.com/manage-profile/security/api-tokens)

## 2. Usage
- The workflow `.github/workflows/jira-issue.yml` will run on every push to `TASKS.md` and create Jira issues for new TODOs.
- The script `.github/scripts/jira_sync.py` parses `TASKS.md` and creates issues in your Jira project.

## 3. Customization
- Edit `PROJECT_KEY` in `jira_sync.py` to match your Jira project.
- Adjust the script to support other issue types or sync directions as needed.

## 4. Reuse
- Copy these files to other projects and update secrets as needed for universal Jira automation.
