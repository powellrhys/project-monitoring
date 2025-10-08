# Import dependencies
from ..data import GitHubClient
from ..logging import configure_logging
from shared import BlobClient, Variables
import requests
import json

class WorkflowScrapper(BlobClient):
    """
    A utility class for collecting and storing GitHub Actions workflow data
    across multiple repositories. Uses the GitHubClient to fetch workflow
    details, run metadata, and durations, and saves the results to JSON files.
    """
    def __init__(self, REPOS: list) -> None:
        """
        Initialize the WorkflowScrapper with a list of repositories to process.

        Args: REPOS (list): A list of repository names to collect workflow data from.
        """
        self.logger = configure_logging()
        self.REPOS = REPOS
        self.vars = Variables()

    def run(self) -> None:
        """
        Execute the workflow data collection process for all configured repositories.

        Iterates through each repository, fetches workflow and run data using the
        GitHubClient, and writes the aggregated results to JSON files. Handles API
        and data processing errors gracefully, logging progress and issues.
        """
        # Iterate through each repo and collect workflow data
        self.logger.info("Running Workflow Scrapping flow \n")
        for repo_i, repo in enumerate(iterable=self.REPOS, start=1):

            try:
                # Log progress message
                self.logger.info(f"{repo_i}/{len(self.REPOS)} - Collecting workflow data for repo: {repo}... \n")

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

                        # Export data to blob storage
                        self.export_dict_to_blob(data=wf_runs, container="project-monitoring",
                                                 output_filename=f"workflows/{repo}_{wf['name']}.json")

                    except requests.exceptions.RequestException as e:
                        self.logger.exception(f"Error fetching data for {wf['name']}: {e}")
                        break

                    except json.JSONDecodeError as e:
                        self.logger.exception(f"Failed to parse workflow run data - {e}")
                        break

                self.logger.info(f"Updated workflow data for {repo} \n")

            except requests.exceptions.RequestException as e:
                self.logger.exception(f"Error fetching data for {repo}: {e} \n")
