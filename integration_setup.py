import yaml
import requests
from typing import Dict, Any
import os
import logging
from github import Github
from bitbucket.client import Client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open('integration_config.yaml', 'r') as f:
        return yaml.safe_load(f)

def setup_jira_webhook(config: Dict[str, Any]) -> None:
    """Set up Jira webhook for GitHub repository."""
    try:
        headers = {
            'Authorization': f'Basic {config["jira"]["api_token"]}',
            'Content-Type': 'application/json'
        }
        
        webhook_data = {
            'name': 'GitHub Webhook',
            'url': config['webhooks']['jira_webhook_url'],
            'events': ['push']
        }
        
        response = requests.post(
            f"{config['jira']['base_url']}/rest/webhook/1.0/webhook",
            headers=headers,
            json=webhook_data
        )
        
        response.raise_for_status()
        logging.info("Successfully set up Jira webhook")
    except Exception as e:
        logging.error(f"Failed to set up Jira webhook: {str(e)}")
        raise

def setup_bitbucket_webhook(config: Dict[str, Any]) -> None:
    """Set up Bitbucket webhook for GitHub repository."""
    try:
        client = Client(
            username=config['bitbucket']['username'],
            password=config['bitbucket']['app_password']
        )
        
        webhook_data = {
            'description': 'GitHub Webhook',
            'url': config['webhooks']['bitbucket_webhook_url'],
            'active': True,
            'events': ['repo:push']
        }
        
        response = client.post(
            f"/repositories/{config['bitbucket']['workspace']}/opendiscourse/hooks",
            json=webhook_data
        )
        
        if response.status_code == 201:
            logging.info("Successfully set up Bitbucket webhook")
        else:
            logging.error(f"Failed to set up Bitbucket webhook: {response.text}")
            raise Exception("Failed to set up Bitbucket webhook")
    except Exception as e:
        logging.error(f"Failed to set up Bitbucket webhook: {str(e)}")
        raise

def setup_github_webhooks(config: Dict[str, Any]) -> None:
    """Set up GitHub webhooks for Jira and Bitbucket."""
    try:
        g = Github(config['github']['token'])
        repo = g.get_repo(config['github']['repository'])
        
        # Set up Jira webhook
        jira_webhook = repo.create_hook(
            name='web',
            config={
                'url': config['webhooks']['jira_webhook_url'],
                'content_type': 'json'
            },
            events=['push'],
            active=True
        )
        logging.info("Successfully set up GitHub webhook for Jira")
        
        # Set up Bitbucket webhook
        bitbucket_webhook = repo.create_hook(
            name='web',
            config={
                'url': config['webhooks']['bitbucket_webhook_url'].format(
                    workspace=config['bitbucket']['workspace'],
                    repo_slug='opendiscourse'
                ),
                'content_type': 'json'
            },
            events=['push'],
            active=True
        )
        logging.info("Successfully set up GitHub webhook for Bitbucket")
    except Exception as e:
        logging.error(f"Failed to set up GitHub webhooks: {str(e)}")
        raise

def setup_repository_links(config: Dict[str, Any]) -> None:
    """Set up repository links between GitHub and Bitbucket."""
    try:
        client = Client(
            username=config['bitbucket']['username'],
            password=config['bitbucket']['app_password']
        )
        
        response = client.post(
            f"/repositories/{config['bitbucket']['workspace']}/opendiscourse/links",
            json={
                'repository': {
                    'url': f"https://github.com/{config['github']['repository']}"
                }
            }
        )
        
        if response.status_code == 201:
            logging.info("Successfully linked GitHub repository to Bitbucket")
        else:
            logging.error(f"Failed to link repositories: {response.text}")
            raise Exception("Failed to link repositories")
    except Exception as e:
        logging.error(f"Failed to set up repository links: {str(e)}")
        raise

def main():
    config = load_config()
    
    try:
        logging.info("Starting integration setup...")
        
        # Setup webhooks
        setup_jira_webhook(config)
        setup_bitbucket_webhook(config)
        setup_github_webhooks(config)
        
        # Setup repository links
        setup_repository_links(config)
        
        logging.info("Integration setup completed successfully!")
        
    except Exception as e:
        logging.error(f"Integration setup failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
