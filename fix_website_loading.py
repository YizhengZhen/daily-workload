#!/usr/bin/env python3
"""
Fix website loading issue by ensuring proper data files exist.
"""

import os
import json
import sys
from datetime import datetime, timezone

def check_website_structure():
    """Check website directory structure and data files."""
    website_dir = "website"
    data_dir = os.path.join(website_dir, "data")
    
    print(f"Checking website structure...")
    print(f"Website directory: {website_dir}")
    print(f"Data directory: {data_dir}")
    
    # Check if directories exist
    if not os.path.exists(website_dir):
        print(f"ERROR: Website directory not found: {website_dir}")
        return False
    
    if not os.path.exists(data_dir):
        print(f"ERROR: Data directory not found: {data_dir}")
        os.makedirs(data_dir, exist_ok=True)
        print(f"Created data directory: {data_dir}")
    
    # Check index.json
    index_file = os.path.join(data_dir, "index.json")
    if not os.path.exists(index_file):
        print(f"WARNING: index.json not found, creating default...")
        create_default_index(index_file)
    else:
        print(f"Found index.json: {index_file}")
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        print(f"  Dates in index: {len(index.get('dates', []))}")
        print(f"  Latest date: {index.get('latest', 'N/A')}")
        print(f"  Updated: {index.get('updated', 'N/A')}")
    
    # Check data files
    data_files = []
    for file in os.listdir(data_dir):
        if file.endswith('.json') and file != 'index.json':
            data_files.append(file)
    
    print(f"\nData files found: {len(data_files)}")
    for file in sorted(data_files)[:10]:  # Show first 10
        file_path = os.path.join(data_dir, file)
        size = os.path.getsize(file_path)
        print(f"  {file} ({size} bytes)")
    
    if len(data_files) > 10:
        print(f"  ... and {len(data_files) - 10} more")
    
    return True

def create_default_index(index_file):
    """Create a default index.json with today's date."""
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    index = {
        "dates": [today, "2024-01-01"],  # Include test date
        "latest": today,
        "updated": datetime.now(timezone.utc).isoformat()
    }
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"Created default index.json with date: {today}")
    return index

def check_js_files():
    """Check JavaScript files for data loading issues."""
    website_dir = "website"
    js_dir = os.path.join(website_dir, "js")
    
    print(f"\nChecking JavaScript files...")
    
    # Check data-loader.js
    loader_file = os.path.join(js_dir, "data-loader.js")
    if os.path.exists(loader_file):
        with open(loader_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for potential issues
        issues = []
        
        # Check baseUrl construction
        if "window.location.origin + window.location.pathname" not in content:
            issues.append("baseUrl construction may be incorrect")
        
        # Check fetch paths
        if "data/index.json" not in content:
            issues.append("index.json path may be incorrect")
        
        if issues:
            print(f"  data-loader.js: POTENTIAL ISSUES FOUND")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  data-loader.js: Looks good")
    else:
        print(f"  WARNING: data-loader.js not found: {loader_file}")
    
    # Check app.js
    app_file = os.path.join(js_dir, "app.js")
    if os.path.exists(app_file):
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for error handling
        if "console.error" in content and "catch" in content:
            print(f"  app.js: Has error handling")
        else:
            print(f"  app.js: May lack proper error handling")
    else:
        print(f"  WARNING: app.js not found: {app_file}")
    
    return True

def test_data_loading():
    """Simulate data loading to test paths."""
    print(f"\nTesting data loading simulation...")
    
    # Simulate the paths used by the website
    test_paths = [
        "data/index.json",
        "website/data/index.json",
        "data/2024-01-01.json",
        "website/data/2024-01-01.json"
    ]
    
    for path in test_paths:
        exists = os.path.exists(path)
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"  {path}: {status}")
        
        if exists and path.endswith('.json'):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    print(f"    Contains {len(data)} items")
                elif isinstance(data, dict):
                    print(f"    Dictionary with keys: {list(data.keys())}")
            except Exception as e:
                print(f"    Error reading: {e}")

def create_test_data():
    """Create test data if needed."""
    data_dir = "website/data"
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    today_file = os.path.join(data_dir, f"{today}.json")
    
    if not os.path.exists(today_file):
        print(f"\nCreating test data for {today}...")
        
        test_data = [
            {
                "id": f"test:{today}-001",
                "title": "Test Paper 1 - AI Research Progress",
                "summary": "This is a test paper showing AI enhancement is working.",
                "link": "https://example.com/test1",
                "source": "Test",
                "category": "test.AI",
                "score": 8.5,
                "recommendation": True,
                "published": f"{today}T00:00:00Z",
                "authors": ["Test Author 1", "Test Author 2"],
                "score_int": 9,
                "year": today[:4]
            },
            {
                "id": f"test:{today}-002",
                "title": "Test Paper 2 - Quantum Computing Advances",
                "summary": "Another test paper to verify data loading.",
                "link": "https://example.com/test2",
                "source": "Test",
                "category": "test.Quantum",
                "score": 6.0,
                "recommendation": False,
                "published": f"{today}T00:00:00Z",
                "authors": ["Test Author 3"],
                "score_int": 6,
                "year": today[:4]
            }
        ]
        
        with open(today_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"Created test data: {today_file} with {len(test_data)} items")
        
        # Update index.json
        index_file = os.path.join(data_dir, "index.json")
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {"dates": [], "latest": ""}
        
        if today not in index["dates"]:
            index["dates"].append(today)
            index["dates"].sort(reverse=True)
        
        index["latest"] = today
        index["updated"] = datetime.now(timezone.utc).isoformat()
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        print(f"Updated index.json with date: {today}")
    
    return today_file

def main():
    """Main function."""
    print("=" * 60)
    print("Website Loading Issue Diagnostic")
    print("=" * 60)
    
    # Check website structure
    if not check_website_structure():
        print("\nWebsite structure has issues.")
        return 1
    
    # Check JavaScript files
    check_js_files()
    
    # Test data loading
    test_data_loading()
    
    # Create test data if needed
    test_file = create_test_data()
    
    print(f"\n" + "=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)
    print("\nRecommendations:")
    print("1. Check if GitHub Actions workflow is generating new data files")
    print("2. Verify data files are copied to correct location for GitHub Pages")
    print("3. Check browser console for JavaScript errors")
    print("4. Test with the newly created test data")
    print(f"\nTest data created: {test_file}")
    print("Open website/index.html in browser to test.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())