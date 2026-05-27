import os
import sys

# Ensure the root directory is in the python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the frontend app
import frontend.app
