"""
Seed script to create initial users and admin users for the Lab Workflow Webapp
Run this script after initializing the database with init_db.py
"""

import sqlite3
import os
from models.user import User

def seed_users():
    """Create initial users and admin users"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'lab_data.db')
    
    if not os.path.exists(db_path):
        print("Error: Database not found. Please run init_db.py first.")
        return
    
    print("Seeding users...")
    
    # Define initial users (user_id, email, passcode)
    initial_users = [
        ('user1', 'user1@ypmg.com', '1111'),
        ('user2', 'user2@ypmg.com', '2222'),
        ('histology_tech', 'histology_tech@ypmg.com', '3333'),
        ('cytotech', 'cytotech@ypmg.com', '4444'),
        ('labmanager', 'labmanager@ypmg.com', '5555'),
    ]
    
    # Create users
    created_users = {}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for user_id, email, passcode in initial_users:
        user = User.create(db_path, user_id, email, passcode)
        if user:
            # Auto-confirm seeded users (bypass email verification)
            cursor.execute('''
                UPDATE users SET is_confirmed = 1, confirmed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user.id,))
            conn.commit()
            created_users[user_id] = user.id
            print(f"✓ Created user: {user_id} (ID: {user.id}) [AUTO-CONFIRMED]")
        else:
            print(f"✗ User {user_id} already exists")
            # Get existing user ID
            existing_user = User.get_by_user_id(db_path, user_id)
            if existing_user:
                created_users[user_id] = existing_user.id
    
    conn.close()
    
    # Create admin users
    print("\nCreating admin users...")
    
    admin_assignments = [
        ('ala', 3),        # Full admin access
        ('labmanager', 2), # Export and submissions access
    ]
    
    # Create admin users
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for user_id, admin_level in admin_assignments:
        if user_id in created_users:
            db_user_id = created_users[user_id]
            
            # Check if admin entry already exists
            cursor.execute('SELECT id FROM admin_users WHERE user_id = ?', (db_user_id,))
            if cursor.fetchone():
                print(f"✗ Admin entry for {user_id} already exists")
            else:
                cursor.execute('''
                    INSERT INTO admin_users (user_id, admin_level)
                    VALUES (?, ?)
                ''', (db_user_id, admin_level))
                print(f"✓ Created admin user: {user_id} (Level {admin_level})")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("Seed complete!")
    print("="*60)
    print("\nCreated Users:")
    print("-" * 60)
    for user_id, email, passcode in initial_users:
        print(f"  User ID: {user_id:20} Email: {email:30} Passcode: {passcode}")
    
    print("\nAdmin Users:")
    print("-" * 60)
    print("  ala          - Level 3 (Full Access: Dashboard, Users, Exports, Reports)")
    print("  labmanager   - Level 2 (Export & Browse Submissions)")
    
    print("\nAdmin Access Levels:")
    print("-" * 60)
    print("  Level 1: View dashboard and reports")
    print("  Level 2: Level 1 + Export data and browse submissions")
    print("  Level 3: Level 2 + User management")
    
    print("\n" + "="*60)
    print("You can now run the application with: python app.py")
    print("="*60)

if __name__ == '__main__':
    seed_users()
