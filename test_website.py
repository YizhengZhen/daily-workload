#!/usr/bin/env python3
"""
Simple website testing script.
Verifies that website files exist and contain correct data.
"""

import os
import json
import sys

def test_website_structure():
    """Test website directory structure."""
    print("Testing website structure...")
    
    required_files = [
        "website/index.html",
        "website/data/index.json",
        "website/data/2026-04-03.json",
        "website/js/app.js",
        "website/js/data-loader.js",
        "website/css/styles.css"
    ]
    
    all_exist = True
    for file in required_files:
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_data_files():
    """Test data files content."""
    print("\nTesting data files...")
    
    # Test index.json
    try:
        with open("website/data/index.json", "r", encoding="utf-8") as f:
            index = json.load(f)
        
        print(f"  ✓ index.json loaded successfully")
        print(f"    Dates: {index.get('dates', [])}")
        print(f"    Latest: {index.get('latest', 'N/A')}")
        
        # Verify latest date exists
        latest = index.get("latest")
        if latest:
            latest_file = f"website/data/{latest}.json"
            if os.path.exists(latest_file):
                with open(latest_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"  ✓ Latest data file contains {len(data)} papers")
            else:
                print(f"  ✗ Latest data file not found: {latest_file}")
                return False
    except Exception as e:
        print(f"  ✗ Error loading index.json: {e}")
        return False
    
    return True

def test_js_loading():
    """Test JavaScript files for loading issues."""
    print("\nTesting JavaScript files...")
    
    try:
        # Test data-loader.js
        with open("website/js/data-loader.js", "r", encoding="utf-8") as f:
            loader_content = f.read()
        
        # Check for required functions
        required_patterns = [
            "loadDateIndex",
            "loadDateData",
            "loadLatestData",
            "window.dataLoader"
        ]
        
        for pattern in required_patterns:
            if pattern in loader_content:
                print(f"  ✓ Found {pattern} in data-loader.js")
            else:
                print(f"  ✗ Missing {pattern} in data-loader.js")
                return False
        
        # Test app.js
        with open("website/js/app.js", "r", encoding="utf-8") as f:
            app_content = f.read()
        
        required_app_patterns = [
            "ResearchTrackerApp",
            "loadLatestData",
            "applyFilters"
        ]
        
        for pattern in required_app_patterns:
            if pattern in app_content:
                print(f"  ✓ Found {pattern} in app.js")
            else:
                print(f"  ✗ Missing {pattern} in app.js")
                return False
    
    except Exception as e:
        print(f"  ✗ Error testing JavaScript files: {e}")
        return False
    
    return True

def test_html_structure():
    """Test HTML file structure."""
    print("\nTesting HTML file...")
    
    try:
        with open("website/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        required_elements = [
            "<title>Daily Research Tracker</title>",
            "papers-container",
            "date-select",
            "search-box",
            "data-loader.js",
            "app.js"
        ]
        
        for element in required_elements:
            if element in html_content:
                print(f"  ✓ Found {element}")
            else:
                print(f"  ✗ Missing {element}")
                return False
        
        # Check for loading indicator
        if "loading" in html_content or "Loading" in html_content:
            print(f"  ✓ Found loading indicator")
        else:
            print(f"  ⚠️ No loading indicator found")
    
    except Exception as e:
        print(f"  ✗ Error testing HTML: {e}")
        return False
    
    return True

def test_obsidian_output():
    """Test Obsidian output generation."""
    print("\nTesting Obsidian output capability...")
    
    # Check if to_md.py exists
    if os.path.exists("to_md.py"):
        print(f"  ✓ to_md.py exists")
    else:
        print(f"  ✗ to_md.py not found")
        return False
    
    # Check config.yaml for obsidian settings
    try:
        import yaml
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        obsidian_enabled = config.get("obsidian", {}).get("enabled", True)
        if obsidian_enabled:
            print(f"  ✓ Obsidian enabled in config.yaml")
        else:
            print(f"  ⚠️ Obsidian disabled in config.yaml")
        
        # Check generate_output.py
        with open("generate_output.py", "r", encoding="utf-8") as f:
            gen_content = f.read()
        
        if "generate_markdown" in gen_content and "obsidian_dir" in gen_content:
            print(f"  ✓ generate_output.py includes Obsidian generation")
        else:
            print(f"  ✗ generate_output.py missing Obsidian generation")
            return False
    
    except Exception as e:
        print(f"  ⚠️ Could not fully test Obsidian: {e}")
    
    return True

def main():
    """Main test function."""
    print("=" * 60)
    print("Daily Research Tracker - Website Test")
    print("=" * 60)
    
    tests = [
        ("Website Structure", test_website_structure),
        ("Data Files", test_data_files),
        ("JavaScript Loading", test_js_loading),
        ("HTML Structure", test_html_structure),
        ("Obsidian Output", test_obsidian_output)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  ✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    total_passed = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    for test_name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n✅ All tests passed! Website should work correctly.")
        print("\nTo test in browser:")
        print("1. Open 'website/index.html' in your browser")
        print("2. You should see 3 test papers from 2026-04-03")
        print("3. Try filtering, searching, and viewing paper details")
    else:
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed.")
        print("\nRecommended actions:")
        print("1. Run 'fix_website_loading.py' to diagnose issues")
        print("2. Check browser console for JavaScript errors")
        print("3. Verify all required files exist")
    
    return 0 if total_passed == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())