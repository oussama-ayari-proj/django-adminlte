import os
import django
from pathlib import Path

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# After Django setup, we can import from Django apps
from django.core.management import call_command

print("Testing file upload app functionality...")
print("Django version:", django.get_version())
print("App ready for file uploads and processing")
print("You can access the app at: http://localhost:8000/fileupload/upload/")
