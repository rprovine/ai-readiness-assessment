#!/usr/bin/env python3
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Change to backend directory to run the app
os.chdir(os.path.join(project_root, 'backend'))

# Run the backend app directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)