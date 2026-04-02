#!/usr/bin/env python3
"""Test that seeded users are auto-confirmed"""
import os
import sqlite3

# Test both local and Vercel databases
test_cases = [
    ("Local DB", "instance/lab_data.db"),
    ("Vercel DB", "/tmp/lab_data.db")
]

for name, db_path in test_cases:
    print(f"\n{'='*60}")
    print(f"Testing: {name} ({db_path})")
    print('='*60)
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        continue
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, email, is_confirmed, confirmed_at 
        FROM users 
        ORDER BY id
    ''')
    
    users = cursor.fetchall()
    
    if not users:
        print("❌ No users found in database")
        conn.close()
        continue
    
    print(f"\nFound {len(users)} users:\n")
    all_confirmed = True
    
    for user_id, email, is_confirmed, confirmed_at in users:
        status = "✅ CONFIRMED" if is_confirmed else "❌ NOT CONFIRMED"
        print(f"  {user_id:20} {email:30} {status}")
        if confirmed_at and is_confirmed:
            print(f"  {'':20} Confirmed at: {confirmed_at}")
        if not is_confirmed:
            all_confirmed = False
    
    conn.close()
    
    if all_confirmed:
        print(f"\n✅ All users in {name} are confirmed!")
    else:
        print(f"\n❌ Some users in {name} are NOT confirmed!")

print("\n" + "="*60)
print("Email Confirmation Test Complete")
print("="*60 + "\n")
