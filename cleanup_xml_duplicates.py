#!/usr/bin/env python3
"""
SPZ XML Cleanup Script
Fixes duplicate files issue - keeps only one file per source
"""

import os
import re
import glob
from pathlib import Path

def cleanup_duplicate_xmls(directory="."):
    """
    Keeps only the latest XML file for each source.
    Renames latest to: {source}.xml (without timestamp)
    Removes older timestamped versions
    """
    os.chdir(directory)
    
    # Get all XML files
    xml_files = glob.glob("*.xml")
    
    # Group files by source name (ignoring timestamp)
    source_groups = {}
    
    for file in xml_files:
        # Pattern: source_name_YYYYMMDD_HHMM.xml or source_name_YYYYMMDD.xml
        match = re.match(r'(.+)_(\d{8})(?:_(\d{4}))?\.xml$', file)
        
        if match:
            source_name = match.group(1)
            date_str = match.group(2)
            time_str = match.group(3) if match.group(3) else "0000"
            
            if source_name not in source_groups:
                source_groups[source_name] = []
            
            source_groups[source_name].append({
                'file': file,
                'date': date_str,
                'time': time_str,
                'datetime': f"{date_str}{time_str}"
            })
    
    files_to_delete = []
    files_to_rename = []
    
    for source_name, files in source_groups.items():
        if len(files) > 1:
            # Sort by datetime (latest first)
            files.sort(key=lambda x: x['datetime'], reverse=True)
            
            # Keep the latest, delete the rest
            latest = files[0]
            latest_file = latest['file']
            
            # Rename latest to source_name.xml
            new_name = f"{source_name}.xml"
            files_to_rename.append((latest_file, new_name))
            
            # Delete older files
            for old_file in files[1:]:
                files_to_delete.append(old_file['file'])
    
    return files_to_rename, files_to_delete

def execute_cleanup(directory=".", dry_run=True):
    """
    Execute the cleanup (or just preview if dry_run=True)
    """
    files_to_rename, files_to_delete = cleanup_duplicate_xmls(directory)
    
    print("=" * 60)
    print("SPZ XML Cleanup Report")
    print("=" * 60)
    
    print(f"\nFiles to rename (keep as latest):")
    for old, new in files_to_rename:
        print(f"  {old} -> {new}")
    
    print(f"\nFiles to delete (older duplicates):")
    for f in files_to_delete:
        print(f"  {f}")
    
    print(f"\nTotal files to rename: {len(files_to_rename)}")
    print(f"Total files to delete: {len(files_to_delete)}")
    
    if not dry_run:
        print("\nExecuting...")
        
        # Delete old files
        for f in files_to_delete:
            try:
                os.remove(f)
                print(f"Deleted: {f}")
            except Exception as e:
                print(f"Error deleting {f}: {e}")
        
        # Rename latest files
        for old, new in files_to_rename:
            try:
                # If target exists, remove it first
                if os.path.exists(new):
                    os.remove(new)
                    print(f"Removed existing: {new}")
                os.rename(old, new)
                print(f"Renamed: {old} -> {new}")
            except Exception as e:
                print(f"Error renaming {old}: {e}")
        
        print("\nCleanup complete!")
    else:
        print("\n(Dry run - no changes made)")
        print("Run with dry_run=False to execute")

if __name__ == "__main__":
    import sys
    
    directory = "."
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    
    dry_run = True
    if len(sys.argv) > 2 and sys.argv[2] == "--execute":
        dry_run = False
    
    execute_cleanup(directory, dry_run)
