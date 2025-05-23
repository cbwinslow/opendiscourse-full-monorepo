# Development Setup

## Connecting GitHub to Jira and Bitbucket

### 1. Connect GitHub to Jira

1. Go to Jira → Settings (gear icon) → Applications → Development → GitHub
2. Click "Connect GitHub"
3. Select your GitHub account
4. Grant Jira access to your repositories
5. In Jira, select your project and click "Add repository"
6. Choose your GitHub repository (opendiscourse)
7. Enable "Smart Commits" to link commits to Jira issues

### 2. Connect GitHub to Bitbucket

1. Go to Bitbucket → Repository → Settings → Repository → Repository links
2. Click "Add repository link"
3. Select "GitHub"
4. Enter your GitHub repository URL: `https://github.com/cbwinslow/opendiscourse`
5. Click "Link repository"

### 3. Configure GitHub Integration

1. Go to GitHub → Repository → Settings → Webhooks
2. Add a new webhook for Jira:
   - Payload URL: `https://your-jira-instance.atlassian.net/rest/webhook/1.0/webhook`
   - Content type: application/json
   - Which events would you like to trigger this webhook?: "Just the push event"

3. Add a new webhook for Bitbucket:
   - Payload URL: `https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/hooks`
   - Content type: application/json
   - Which events would you like to trigger this webhook?: "Just the push event"

### 4. Configure Git Commit Messages

Use the following format in your commit messages to link to Jira issues:
```
JIRA-123: Your commit message here
```

Where JIRA-123 is your Jira issue key.

## Development Workflow

1. Create a Jira issue for your work
2. Create a feature branch with the Jira issue key:
   ```bash
   git checkout -b feature/JIRA-123-your-feature-name
   ```
3. Make your changes
4. Commit with the Jira issue key:
   ```bash
   git commit -m "JIRA-123: Your commit message"
   ```
5. Push to GitHub
6. Create a pull request in GitHub
7. Link the PR to Jira issue
8. Merge through GitHub
9. The changes will be automatically reflected in both Jira and Bitbucket
