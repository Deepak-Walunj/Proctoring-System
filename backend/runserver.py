import os
import sys
from django.core.management import execute_from_command_line
import shutil

if __name__ == "__main__":
    root_dir = "."  # Set the root directory (current directory)
    for root, dirs, files in os.walk(root_dir):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(pycache_path)
                    print(f"Removed: {pycache_path}")
                except Exception as e:
                    print(f"Failed to remove {pycache_path}: {e}")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
      # Replace with your project's settings
    
    execute_from_command_line(["manage.py", "runserver","0.0.0.0:8000"])
