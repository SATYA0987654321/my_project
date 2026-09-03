import sys
import os

# Set up python sys.path for Vercel Serverless environment
curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curr_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from main import app
