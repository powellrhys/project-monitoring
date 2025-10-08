# Import dependencies
from .functions.orchestation import WorkflowScrapper

# List of repos to monitor
REPOS = ["golf-ui-streamlit", "fantasy-premier-league", "play-cricket", "strava-ui-streamlit"]

# Execute Workflow Scrapper Flow
WorkflowScrapper(REPOS=REPOS).run()
