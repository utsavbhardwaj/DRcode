#!/usr/bin/env python3
"""
Setup script to download all external resources for offline use
Run this once with internet connection before deploying offline
"""

import os
import urllib.request
import sys

def download_file(url, filepath):
    """Download a file from URL to filepath"""
    try:
        print(f"Downloading: {url}")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        urllib.request.urlretrieve(url, filepath)
        print(f"✓ Saved to: {filepath}")
        return True
    except Exception as e:
        print(f"✗ Error downloading {url}: {e}")
        return False

def main():
    print("=" * 70)
    print("DRcode Offline Setup - Downloading External Resources")
    print("=" * 70)
    
    # Create directories
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Bootstrap CSS and JS
    resources = [
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
            'path': 'static/css/bootstrap.min.css'
        },
        {
            'url': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
            'path': 'static/js/bootstrap.bundle.min.js'
        }
    ]
    
    success_count = 0
    for resource in resources:
        if download_file(resource['url'], resource['path']):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"Download Complete: {success_count}/{len(resources)} files downloaded")
    print("=" * 70)
    
    if success_count == len(resources):
        print("\n✓ All resources downloaded successfully!")
        print("\nNext steps:")
        print("1. Update your templates to use local resources")
        print("2. Install Python dependencies: pip install -r requirements.txt")
        print("3. Run the application: python app.py")
    else:
        print("\n⚠ Some downloads failed. Please check your internet connection.")
        sys.exit(1)

if __name__ == '__main__':
    main()