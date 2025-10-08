# Import dependencies
from dotenv import load_dotenv
import os

# Load environmental variables
load_dotenv()

class Variables:
    """
    Class to collect environmental variables from .env file
    """
    def __init__(self):

        # Collect environmental variables
        self.GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
