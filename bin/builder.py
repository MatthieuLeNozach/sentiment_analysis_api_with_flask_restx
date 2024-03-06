import os
import sys
import subprocess

# Get the directory of this script
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to the Python path
sys.path.append(project_root)

# Change the working directory to the script directory
print(project_root)
os.chdir(project_root)

# Run the scripts as separate processes
subprocess.run(['python', 'bin/initialize_db.py'])
subprocess.run(['python', 'bin/confidential/add_creator.py'])
subprocess.run(['python', 'bin/add_customer_base.py'])