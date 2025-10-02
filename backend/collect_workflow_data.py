# Import dependencies
from .functions.orchestation import WorkflowScrapper

# List of repos to monitor
REPOS = ["golf-ui-streamlit", "play-cricket", "strava-ui-streamlit"]

WorkflowScrapper(REPOS=REPOS).run()
