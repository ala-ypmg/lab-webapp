#!/usr/bin/env python3
"""
Test script to verify Vercel database auto-initialization
Simulates a Vercel cold start scenario
"""
import os
import sys
import sqlite3

# Set VERCEL environment variable to trigger Vercel-specific logic
os.environ['VERCEL'] = '1'

# Remove existing /tmp database to simulate cold start
db_path = '/tmp/lab_data.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✓ Removed existing database at {db_path}")

print("\n" + "="*60)
print("SIMULATING VERCEL COLD START")
print("="*60 + "\n")

# Import the app (this should trigger auto-initialization)
print("Importing app module...")
try:
    from app import app
    print("✓ App imported successfully\n")
except Exception as e:
    print(f"✗ Failed to import app: {e}")
    sys.exit(1)

# Verify database was created
print("="*60)
print("VERIFICATION TESTS")
print("="*60 + "\n")

if os.path.exists(db_path):
    print(f"✓ Database file created at {db_path}")
else:
    print(f"✗ Database file NOT found at {db_path}")
    sys.exit(1)

# Connect and verify tables
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check tables
expected_tables = ['users', 'user_sessions', 'form_submissions', 'admin_users', 'audit_log']
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']

print(f"\nExpected tables: {len(expected_tables)}")
print(f"Found tables:    {len(tables)}")
for table in tables:
    if table in expected_tables:
        print(f"  ✓ {table}")
    else:
        print(f"  ? {table} (unexpected)")

missing = set(expected_tables) - set(tables)
if missing:
    print(f"\n✗ Missing tables: {missing}")
    sys.exit(1)
else:
    print("\n✓ All expected tables exist")

# Check users were seeded
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
print(f"\n✓ Users seeded: {user_count} users found")

if user_count > 0:
    cursor.execute("SELECT user_id, email FROM users")
    print("\nCreated users:")
    for user_id, email in cursor.fetchall():
        print(f"  - {user_id:20} {email}")
else:
    print("✗ No users found in database")
    sys.exit(1)

# Check admin users
cursor.execute("SELECT COUNT(*) FROM admin_users")
admin_count = cursor.fetchone()[0]
print(f"\n✓ Admin users: {admin_count} admin entries")

if admin_count > 0:
    cursor.execute("""
        SELECT u.user_id, a.admin_level 
        FROM admin_users a 
        JOIN users u ON a.user_id = u.id
    """)
    print("\nAdmin users:")
    for user_id, level in cursor.fetchall():
        print(f"  - {user_id:20} Level {level}")

# Test user authentication
print("\n" + "="*60)
print("AUTHENTICATION TEST")
print("="*60 + "\n")

cursor.execute("SELECT id, user_id, email, passcode_hash FROM users WHERE user_id = 'ala'")
result = cursor.fetchone()

if result:
    print("✓ Admin user 'ala' found in database")
    print(f"  ID:    {result[0]}")
    print(f"  User:  {result[1]}")
    print(f"  Email: {result[2]}")
    print(f"  Hash:  {result[3][:50]}...")
    
    # Test password verification
    import bcrypt
    test_passcode = '6925'
    if bcrypt.checkpw(test_passcode.encode('utf-8'), result[3].encode('utf-8')):
        print(f"\n✓ Password verification successful for passcode '{test_passcode}'")
    else:
        print(f"\n✗ Password verification FAILED for passcode '{test_passcode}'")
        sys.exit(1)
else:
    print("✗ Admin user 'ala' NOT found")
    sys.exit(1)

conn.close()

print("\n" + "="*60)
print("ALL TESTS PASSED ✓")
print("="*60)
print("\nThe Vercel auto-initialization is working correctly!")
print("Database will be created automatically on cold starts.")
print("\nYou can now login with:")
print("  User ID:  ala")
print("  Passcode: 6925")
print("="*60 + "\n")
