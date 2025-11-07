# create test_gdal.py in your project root
import os
import django
from django.conf import settings

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

try:
    from django.contrib.gis.gdal import GDAL_VERSION
    print(f"✅ GDAL working with Django! Version: {GDAL_VERSION}")
    
    # Test if we can import GIS models
    from django.contrib.gis.db import models
    print("✅ GIS models can be imported!")
    
except Exception as e:
    print(f"❌ Error: {e}")