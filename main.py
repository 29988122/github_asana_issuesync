import requests

# Replace with your personal access tokens
GITHUB_TOKEN = "token"
ASANA_TOKEN = "token"

# Replace with your repo and Asana project details
GITHUB_ORG_NAME = "scroll-tech"
ASANA_PROJECT_ID = "project_id"

# Fetch all repositories in the organization
github_headers = {"Authorization": f"token {GITHUB_TOKEN}"}
github_repos_url = f"https://api.github.com/orgs/{GITHUB_ORG_NAME}/repos?type=public"
response = requests.get(github_repos_url, headers=github_headers)

if response.status_code == 200:
    github_repos = response.json()

    # Add GitHub issues to Asana
    asana_headers = {"Authorization": f"Bearer {ASANA_TOKEN}", "Content-Type": "application/json"}

    for repo in github_repos:
        if not repo["private"]:  # Check if the repository is public
            page = 1

            while True:
                # Fetch GitHub issues for the current repository and page
                github_issues_url = f"https://api.github.com/repos/{GITHUB_ORG_NAME}/{repo['name']}/issues?page={page}"
                github_issues = requests.get(github_issues_url, headers=github_headers).json()

                if not github_issues:
                    break

                # Filter out pull requests
                filtered_issues = [issue for issue in github_issues if 'pull_request' not in issue]

                for issue in filtered_issues:
                    issue_url = issue["html_url"]
                    issue_author = issue["user"]["login"]
                    asana_task_data = {
                        "data": {
                            "name": f"{repo['name']} - {issue['title']}",
                            "notes": f"Author: {issue_author}\n{issue_url}\n\n{issue['body']}",  # Add the GitHub issue author and URL to the beginning of the description
                            "projects": [ASANA_PROJECT_ID],
                        }
                    }

                    asana_task_url = "https://app.asana.com/api/1.0/tasks"
                    response = requests.post(asana_task_url, json=asana_task_data, headers=asana_headers)

                    if response.status_code == 201:
                        print(f"Added issue {issue['number']} from repo {repo['name']} as task: {response.json()['data']['gid']}")
                    else:
                        print(f"Error creating task for issue {issue['number']} from repo {repo['name']}: {response.json()}")

                # Increment the page number for the next iteration
                page += 1

            # Prompt for user input after iterating through all issues in the current repository
            input(f"All issues from repo {repo['name']} have been processed. Press Enter to continue to the next repository...")

else:
    print(f"Error fetching repositories: {response.json()}")