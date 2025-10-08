# Import dependencies
from ..logging import configure_logging
from datetime import datetime
import requests

class GitHubClient:
    """
    A client for interacting with GitHub repositories using the GitHub REST API.
    Provides methods to list workflows, collect workflow metadata, calculate run durations,
    and aggregate workflow data for reporting or analysis.
    """
    def __init__(self, GITHUB_TOKEN: str) -> None:
        """
        Initialize the GitHubClient with a personal access token.

        Args: GITHUB_TOKEN (str): GitHub personal access token used for authentication.
        """
        self.logge = configure_logging()
        self.base_url = "https://api.github.com/repos/powellrhys"
        self.HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

    def list_repository_workflows(self, repo: str) -> list:
        """
        Retrieve a list of workflows configured in the specified repository.

        Args: repo (str): The name of the GitHub repository.

        Returns: list: A list of workflow objects from the GitHub API response.
        """

        # Define request url
        workflows_url = f"{self.base_url}/{repo}/actions/workflows"

        # Execute request
        workflows_resp = requests.get(workflows_url, headers=self.HEADERS)
        workflows_resp.raise_for_status()

        # Collect workflow data
        return workflows_resp.json().get("workflows", [])

    def collect_workflow_metadata(self, repo: str, workflow: dict) -> dict:
        """
        Collect metadata for all runs of a given workflow in a repository.

        Args:
            repo (str): The name of the GitHub repository.
            workflow (dict): A workflow object obtained from the GitHub API.

        Returns: dict: A dictionary containing metadata for each workflow run.
        """
        # Define runs endpoint url
        runs_url = f"{self.base_url}/{repo}/actions/workflows/{workflow['id']}/runs"

        # Execute workflows runs request
        runs_resp = requests.get(runs_url, headers=self.HEADERS)
        runs_resp.raise_for_status()

        # Collect workflow runs data
        return runs_resp.json().get("workflow_runs", [])

    def workflow_duration(self, run: dict) -> int:
        """
        Calculate the duration of a workflow run in seconds.

        Args: run (dict): A workflow run object from the GitHub API.

        Returns: int: Duration of the workflow run in seconds, or None if unavailable.
        """
        start_time_str = run.get("run_started_at") or run.get("created_at")
        end_time_str = run.get("updated_at")

        try:
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
            duration_seconds = (end_time - start_time).total_seconds()

        except Exception:
            duration_seconds = None

        return duration_seconds

    def aggregate_workflow_data(self, repo: str, wf_name: str, workflow_runs: list) -> list:
        """
        Aggregate workflow run data into a simplified list of dictionaries.

        Args:
            repo (str): The name of the GitHub repository.
            wf_name (str): The name of the workflow.
            workflow_runs (list): A list of workflow run objects.

        Returns: list: A list of dictionaries containing summarized workflow run data.
        """
        # Iterate through each run and simplify output
        all_runs = []
        for run in workflow_runs:
            all_runs.append({
                "repo": repo,
                "workflow_name": wf_name,
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
                "created_at": run.get("created_at"),
                "updated_at": run.get("updated_at"),
                "run_number": run.get("run_number"),
                "html_url": run.get("html_url"),
                "duration_seconds": self.workflow_duration(run=run)
            })

        return all_runs
