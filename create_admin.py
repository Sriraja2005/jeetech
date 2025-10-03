#!/usr/bin/env python
"""
Simple script to create an admin user or make an existing user an admin.
Run this script to set up admin access for the JEETECH admin panel.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin_user():
    """Create or update admin user"""
    
    print("=== JEETECH Admin User Setup ===\n")
    
    # Check if any superuser exists
    existing_superusers = User.objects.filter(is_superuser=True)
    if existing_superusers.exists():
        print("Existing superusers found:")
        for user in existing_superusers:
            print(f"  - {user.username} ({user.email})")
        print()
    
    # Check if any staff users exist
    existing_staff = User.objects.filter(is_staff=True)
    if existing_staff.exists():
        print("Existing staff users found:")
        for user in existing_staff:
            print(f"  - {user.username} ({user.email}) - Staff: {user.is_staff}, Superuser: {user.is_superuser}")
        print()
    
    print("Choose an option:")
    print("1. Create new admin user")
    print("2. Make existing user admin")
    print("3. List all users")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        create_new_admin()
    elif choice == "2":
        make_user_admin()
    elif choice == "3":
        list_all_users()
    elif choice == "4":
        print("Exiting...")
        return
    else:
        print("Invalid choice. Please try again.")
        create_admin_user()

def create_new_admin():
    """Create a new admin user"""
    print("\n=== Create New Admin User ===")
    
    username = input("Enter username: ").strip()
    if not username:
        print("Username cannot be empty!")
        return
    
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists!")
        return
    
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()
    
    if not password:
        print("Password cannot be empty!")
        return
    
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        print(f"\n✅ Admin user '{username}' created successfully!")
        print(f"   Email: {email}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Superuser: {user.is_superuser}")
        print("\nYou can now login and access the admin panel.")
        
    except Exception as e:
        print(f"\n❌ Error creating user: {e}")

def make_user_admin():
    """Make an existing user admin"""
    print("\n=== Make Existing User Admin ===")
    
    username = input("Enter username to make admin: ").strip()
    if not username:
        print("Username cannot be empty!")
        return
    
    try:
        user = User.objects.get(username=username)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        print(f"\n✅ User '{username}' is now an admin!")
        print(f"   Email: {user.email}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Superuser: {user.is_superuser}")
        print("\nThey can now access the admin panel.")
        
    except User.DoesNotExist:
        print(f"\n❌ User '{username}' does not exist!")
    except Exception as e:
        print(f"\n❌ Error updating user: {e}")

def list_all_users():
    """List all users in the system"""
    print("\n=== All Users ===")
    
    users = User.objects.all()
    if not users.exists():
        print("No users found in the system.")
        return
    
    print(f"{'Username':<20} {'Email':<30} {'Staff':<8} {'Superuser':<10} {'Active':<8}")
    print("-" * 80)
    
    for user in users:
        print(f"{user.username:<20} {user.email:<30} {user.is_staff:<8} {user.is_superuser:<10} {user.is_active:<8}")
    
    print(f"\nTotal users: {users.count()}")

if __name__ == "__main__":
    try:
        create_admin_user()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
