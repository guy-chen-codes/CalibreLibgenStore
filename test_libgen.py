#!/usr/bin/env python3
"""
Test script for the updated libgen_client.py
"""

from libgen_client import LibgenClient

def test_search():
    client = LibgenClient()
    
    print("Testing search functionality...")
    
    # Test a simple search
    try:
        results = client.search("test", criteria="title")
        print(f"Search returned {results.total} results")
        
        if results.results:
            print(f"First result: {results.results[0].title} by {results.results[0].authors}")
            print(f"MD5: {results.results[0].md5}")
            print(f"Detail URL: {client.get_detail_url(results.results[0].md5)}")
            print(f"Download URL: {client.get_download_url(results.results[0].md5)}")
        
    except Exception as e:
        print(f"Search test failed: {e}")

if __name__ == "__main__":
    test_search() 