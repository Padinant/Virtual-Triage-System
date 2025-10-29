#!/usr/bin/env python3
"""Test script to verify all routes work properly"""

from website import app
from flask import url_for

def test_routes():
    with app.app_context():
        print("=== TESTING ALL ROUTES ===\n")
        
        # Test basic page routes
        print("Page Routes:")
        try:
            print(f"  home: {url_for('home')} ✅")
        except Exception as e:
            print(f"  home: ERROR - {e} ❌")
            
        try:
            print(f"  faq_page: {url_for('faq_page')} ✅")
        except Exception as e:
            print(f"  faq_page: ERROR - {e} ❌")
            
        try:
            print(f"  faq_admin: {url_for('faq_admin')} ✅")
        except Exception as e:
            print(f"  faq_admin: ERROR - {e} ❌")
            
        try:
            print(f"  chat: {url_for('chat')} ✅")
        except Exception as e:
            print(f"  chat: ERROR - {e} ❌")
        
        # Test admin routes
        print("\nAdmin Routes:")
        try:
            print(f"  faq_admin_add: {url_for('faq_admin_add')} ✅")
        except Exception as e:
            print(f"  faq_admin_add: ERROR - {e} ❌")
            
        try:
            print(f"  faq_admin_edit: {url_for('faq_admin_edit', faq_id=1)} ✅")
        except Exception as e:
            print(f"  faq_admin_edit: ERROR - {e} ❌")
            
        try:
            print(f"  faq_admin_remove: {url_for('faq_admin_remove', faq_id=1)} ✅")
        except Exception as e:
            print(f"  faq_admin_remove: ERROR - {e} ❌")
        
        # Test POST routes
        print("\nPOST Routes:")
        try:
            print(f"  faq_admin_add_post: {url_for('faq_admin_add_post')} ✅")
        except Exception as e:
            print(f"  faq_admin_add_post: ERROR - {e} ❌")
            
        try:
            print(f"  faq_admin_edit_post: {url_for('faq_admin_edit_post', faq_id=1)} ✅")
        except Exception as e:
            print(f"  faq_admin_edit_post: ERROR - {e} ❌")
            
        try:
            print(f"  message: {url_for('message')} ✅")
        except Exception as e:
            print(f"  message: ERROR - {e} ❌")
        
        # Test item route
        print("\nItem Routes:")
        try:
            print(f"  faq_item_page: {url_for('faq_item_page', faq_id=1)} ✅")
        except Exception as e:
            print(f"  faq_item_page: ERROR - {e} ❌")
        
        print("\n=== ROUTE TEST COMPLETE ===")

if __name__ == "__main__":
    test_routes()