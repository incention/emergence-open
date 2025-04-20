#!/usr/bin/env python3
"""
Emergence Asset Catalog Updater

This script connects to AWS S3, scans for Emergence project assets,
and updates the YAML catalog file with current information.

Requirements:
    - boto3
    - pyyaml
    - gitpython (optional, for auto-commits)

Usage:
    python update_asset_catalog.py [--commit]
"""

import argparse
import boto3
import datetime
import os
import yaml
from pathlib import Path
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

# Configuration
AWS_PROFILE = "emergence"  # AWS profile name in ~/.aws/credentials
S3_BUCKET_NAME = "emergence-assets"
CATALOG_FILE = "emergence-assets-catalog.yaml"
REPO_ROOT = Path(__file__).parent.parent  # Assumes script is in scripts/ directory

# Category mapping based on S3 prefixes
CATEGORY_MAPPING = {
    "ue5/": "unreal_engine",
    "animations/": "animation_data",
    "models/": "assets",
    "premiere/": "premiere_pro",
    "audio/": "premiere_pro",
    "videos/": "final_movie",
}

def get_human_readable_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0 or unit == 'TB':
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0

def get_tags_from_key(key):
    """Extract potential tags from the S3 object key"""
    # Simple implementation - customize based on your naming conventions
    filename = os.path.basename(key)
    parts = filename.replace('.', '_').split('_')
    return [part for part in parts if len(part) > 2 and part not in ['v1', 'v2', 'v3']]

def determine_category(key):
    """Determine which category an asset belongs to based on its S3 key"""
    for prefix, category in CATEGORY_MAPPING.items():
        if key.startswith(prefix):
            return category
    
    # Default fallback - you may want to customize this
    if any(ext in key.lower() for ext in ['.fbx', '.obj', '.blend']):
        return "assets"
    elif any(ext in key.lower() for ext in ['.mp4', '.mov', '.avi']):
        return "final_movie"
    
    return "assets"  # Default category

def update_catalog():
    """Main function to update the asset catalog"""
    catalog_path = REPO_ROOT / CATALOG_FILE
    
    # Load existing catalog
    if catalog_path.exists():
        with open(catalog_path, 'r') as f:
            catalog = yaml.safe_load(f)
    else:
        # Create new catalog with basic structure
        catalog = {
            "project_name": "Emergence",
            "description": "Assets from the Emergence universe for Epic's Unreal Engine community",
            "updated_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "maintainer": "Emergence Team",
            "repository_url": "https://github.com/emergence-universe/assets-catalog",
            "categories": {
                "unreal_engine": {"description": "UE session with custom project settings", "assets": []},
                "animation_data": {"description": "Character and object animation data", "assets": []},
                "assets": {"description": "3D models, textures, and other game assets", "assets": []},
                "premiere_pro": {"description": "Premiere Pro sessions and assets", "assets": []},
                "final_movie": {"description": "Final rendered movie files", "assets": []},
            },
            "metadata": {
                "license": "Emergence Community License - See LICENSE.md in repository",
                "contact_email": "assets@emergence-universe.com",
                "documentation_url": "https://docs.emergence-universe.com/community-assets",
                "update_frequency": "Weekly"
            }
        }
    
    # Create asset map for faster lookups of existing assets
    asset_map = {}
    for category, category_data in catalog["categories"].items():
        for asset in category_data["assets"]:
            asset_map[asset["url"]] = (category, asset)
    
    # Connect to AWS S3
    session = boto3.Session(profile_name=AWS_PROFILE)
    s3 = session.client('s3')
    
    # Get list of all objects in the bucket
    print(f"Scanning S3 bucket: {S3_BUCKET_NAME}...")
    
    try:
        paginator = s3.get_paginator('list_objects_v2')
        assets_updated = 0
        
        for page in paginator.paginate(Bucket=S3_BUCKET_NAME):
            if 'Contents' not in page:
                continue
                
            for obj in page['Contents']:
                key = obj['Key']
                url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{key}"
                
                # Skip certain files or directories
                if key.endswith('/') or key.startswith('.') or '__MACOSX' in key:
                    continue
                
                # Determine the category for this asset
                category = determine_category(key)
                
                # Check if this asset already exists in our catalog
                if url in asset_map:
                    existing_category, existing_asset = asset_map[url]
                    
                    # Update last modified date and size if changed
                    if existing_asset["last_modified"] != obj['LastModified'].strftime("%Y-%m-%d"):
                        existing_asset["last_modified"] = obj['LastModified'].strftime("%Y-%m-%d")
                        existing_asset["size"] = get_human_readable_size(obj['Size'])
                        assets_updated += 1
                        print(f"Updated: {existing_asset['name']}")
                    
                    # If the category has changed, move the asset
                    if existing_category != category:
                        # Remove from old category
                        catalog["categories"][existing_category]["assets"].remove(existing_asset)
                        # Add to new category
                        catalog["categories"][category]["assets"].append(existing_asset)
                        print(f"Moved: {existing_asset['name']} from {existing_category} to {category}")
                        assets_updated += 1
                else:
                    # This is a new asset, create an entry for it
                    name = os.path.basename(key)
                    # Clean up the name a bit
                    name = name.replace('_', ' ').replace('-', ' ')
                    parts = name.split('.')
                    if len(parts) > 1:
                        name = '.'.join(parts[:-1])  # Remove file extension
                    
                    # Capitalize first letter of each word
                    name = ' '.join(word.capitalize() for word in name.split())
                    
                    new_asset = {
                        "name": name,
                        "description": f"Emergence {name}",  # Basic description
                        "url": url,
                        "size": get_human_readable_size(obj['Size']),
                        "last_modified": obj['LastModified'].strftime("%Y-%m-%d"),
                        "tags": get_tags_from_key(key)
                    }
                    
                    catalog["categories"][category]["assets"].append(new_asset)
                    assets_updated += 1
                    print(f"Added: {name}")
        
        # Update the catalog's updated_date
        catalog["updated_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Sort assets in each category by name
        for category_data in catalog["categories"].values():
            category_data["assets"].sort(key=lambda x: x["name"])
        
        # Write the updated catalog
        with open(catalog_path, 'w') as f:
            yaml.dump(catalog, f, sort_keys=False, default_flow_style=False)
        
        print(f"Catalog updated with {assets_updated} changes.")
        return assets_updated, catalog_path
        
    except Exception as e:
        print(f"Error updating catalog: {e}")
        return 0, catalog_path

def commit_changes(catalog_path, changes):
    """Commit changes to the git repository"""
    if not GIT_AVAILABLE:
        print("GitPython not installed. Skipping commit.")
        return False
        
    try:
        repo = git.Repo(REPO_ROOT)
        if repo.is_dirty() or repo.untracked_files:
            repo.git.add(str(catalog_path))
            commit_message = f"Update asset catalog with {changes} changes"
            repo.git.commit('-m', commit_message)
            print(f"Changes committed: {commit_message}")
            return True
        else:
            print("No changes to commit.")
            return False
    except Exception as e:
        print(f"Error committing changes: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Update the Emergence asset catalog')
    parser.add_argument('--commit', action='store_true', help='Commit changes to git repository')
    args = parser.parse_args()
    
    changes, catalog_path = update_catalog()
    
    if changes > 0 and args.commit:
        commit_changes(catalog_path, changes)

if __name__ == "__main__":
    main()