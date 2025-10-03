# Import dependencies
from ..logging import configure_logging
from ..data import GitHubClient, Variables
import requests
import json

class WorkflowScrapper:
    """
    """
    def __init__(self, REPOS: list) -> None:
        """
        """
        self.logger = configure_logging()
        self.REPOS = REPOS
        self.vars = Variables()

    def run(self) -> None:
        """
        """
        # Iterate through each repo and collect workflow data
        self.logger.critical("Running Workflow Scrapping flow \n")
        for repo_i, repo in enumerate(iterable=self.REPOS, start=1):

            try:
                # Log progress message
                self.logger.critical(f"{repo_i}/{len(self.REPOS)} - Collecting workflow data for repo: {repo}... \n")

                # Define GithubClient class
                client = GitHubClient(GITHUB_TOKEN=self.vars.GITHUB_TOKEN)
                workflows = client.list_repository_workflows(repo=repo)

                # Log status of collected data
                self.logger.info(f"{len(workflows)} workflows identified within {repo}: "
                                 f"{[wf['name'] for wf in workflows]} \n")

                # Iterate through each workflow and log status message
                for wf_i, wf in enumerate(iterable=workflows, start=1):
                    self.logger.info(f"{wf_i}/{len(workflows)} - Collecting workflow run data for {wf['name']}...")

                    try:
                        wf_runs = client.collect_workflow_metadata(repo=repo, workflow=wf)
                        self.logger.info(f"{len(wf_runs)} workflow runs recorded for {wf['name']}. Last run recorded "
                                         f"at {wf_runs[0]['run_started_at']} | Status: {wf_runs[0]['conclusion']} \n")

                        wf_runs = client.aggregate_workflow_data(repo=repo, wf_name=wf["name"], workflow_runs=wf_runs)

                        # Save results to JSON for dashboard
                        with open(f"data/workflows_{repo}_{wf['name']}.json", "w") as f:
                            json.dump(wf_runs, f, indent=2)

                    except requests.exceptions.RequestException as e:
                        self.logger.error(f"Error fetching data for {wf['name']}: {e}")
                        break

                    except Exception as e:
                        self.logger.error(f"Failed to aggregate workflow run data - {e}")
                        break

                self.logger.info(f"Updated workflow data for {repo} \n")

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching data for {repo}: {e} \n")
