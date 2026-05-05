#!/usr/bin/env python3
"""
Azure SQL Connection Diagnostic Script
Helps identify why connection to Azure SQL is failing
"""

import os
import sys
import socket

def print_header(msg):
    print(f"\n{'='*60}")
    print(f" {msg}")
    print('='*60)

def check_env_vars():
    """Check if environment variables are set"""
    print_header("STEP 1: Checking Environment Variables")
    
    required_vars = [
        ('AZURE_SQL_SERVER', 'ezeos.database.windows.net'),
        ('AZURE_SQL_DATABASE_USERS', 'users'),
        ('AZURE_SQL_DATABASE_MAIN', 'main'),
        ('AZURE_SQL_USERNAME', 'ala'),
        ('AZURE_SQL_PASSWORD', '(must be set)'),
        ('USE_AZURE_SQL', 'true'),
    ]
    
    all_set = True
    for var, default in required_vars:
        value = os.environ.get(var)
        if value:
            masked = '***' if 'PASSWORD' in var else value
            print(f"  ✓ {var} = {masked}")
        else:
            print(f"  ✗ {var} NOT SET (default: {default})")
            if var == 'AZURE_SQL_PASSWORD':
                all_set = False
    
    if not os.environ.get('AZURE_SQL_PASSWORD'):
        print("\n  ⚠️  WARNING: AZURE_SQL_PASSWORD is NOT SET!")
        print("     Run: export AZURE_SQL_PASSWORD='your-password-here'")
        all_set = False
    
    return all_set

def check_dns_resolution():
    """Check if server DNS resolves"""
    print_header("STEP 2: DNS Resolution Check")
    
    server = os.environ.get('AZURE_SQL_SERVER', 'ezeos.database.windows.net')
    
    try:
        ip = socket.gethostbyname(server)
        print(f"  ✓ {server} resolves to {ip}")
        return True
    except socket.gaierror as e:
        print(f"  ✗ DNS resolution failed: {e}")
        print("     This indicates network/DNS issues")
        return False

def check_port_connectivity():
    """Check if port 1433 is reachable"""
    print_header("STEP 3: Port 1433 Connectivity Check")
    
    server = os.environ.get('AZURE_SQL_SERVER', 'ezeos.database.windows.net')
    port = 1433
    
    print(f"  Attempting TCP connection to {server}:{port}...")
    print("  (This may take up to 10 seconds)")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        result = sock.connect_ex((server, port))
        if result == 0:
            print(f"  ✓ Port 1433 is REACHABLE")
            return True
        else:
            print(f"  ✗ Port 1433 is NOT reachable (error code: {result})")
            print("\n  ⚠️  LIKELY CAUSE: Azure SQL firewall is blocking your IP")
            print("     OR Public Network Access is DISABLED")
            return False
    except socket.timeout:
        print(f"  ✗ Connection TIMED OUT")
        print("\n  ⚠️  LIKELY CAUSE: Azure SQL firewall or network config")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    finally:
        sock.close()

def check_pymssql():
    """Check if pymssql is installed"""
    print_header("STEP 4: pymssql Module Check")

    try:
        import pymssql  # noqa: F401
        print("  ✓ pymssql is installed")
        return True
    except ImportError:
        print("  ✗ pymssql module not installed")
        print("     Run: pip install pymssql")
        return False

def test_connection():
    """Attempt actual Azure SQL connection"""
    print_header("STEP 5: Azure SQL Connection Test")

    # Check prerequisites
    if not os.environ.get('AZURE_SQL_PASSWORD'):
        print("  ✗ Skipping - AZURE_SQL_PASSWORD not set")
        return False

    try:
        import pymssql

        server = os.environ.get('AZURE_SQL_SERVER', 'ezeos.database.windows.net')
        database = os.environ.get('AZURE_SQL_DATABASE_USERS', 'users')
        username = os.environ.get('AZURE_SQL_USERNAME', 'ala')
        password = os.environ.get('AZURE_SQL_PASSWORD', '')

        print(f"  Connecting to {server}/{database} as {username}...")
        print("  (Timeout: 60 seconds - DB may need to wake from pause)")

        conn = pymssql.connect(
            server=server,
            user=username,
            password=password,
            database=database,
            tds_version='7.4',
            login_timeout=60,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")

        print("  ✓ CONNECTION SUCCESSFUL!")

        # Get database info
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        if row:
            version = row[0]
            print(f"\n  SQL Server Version: {version[:80]}...")

        conn.close()
        return True

    except pymssql.OperationalError as e:
        error_msg = str(e)

        print(f"  ✗ Connection FAILED")
        print(f"     Error: {error_msg[:200]}")

        if 'Login timeout expired' in error_msg or 'timed out' in error_msg.lower():
            print("\n  ⚠️  DIAGNOSIS: Login timeout - Cannot reach the server")
            print("     MOST LIKELY CAUSES:")
            print("     1. Public Network Access is DISABLED on Azure SQL Server")
            print("     2. Your IP is not in the firewall allow list")
            print("     3. Database is paused and needs longer timeout")
        elif 'Login failed' in error_msg:
            print("\n  ⚠️  DIAGNOSIS: Authentication failed")
            print("     Check your username and password")
        elif 'Cannot open database' in error_msg:
            print("\n  ⚠️  DIAGNOSIS: Database does not exist")
            print("     Check database name is correct")

        return False

    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        return False

def get_public_ip():
    """Try to get the current public IP"""
    print_header("STEP 6: Your Public IP Address")
    
    try:
        import urllib.request
        external_ip = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode('utf8')
        print(f"  Your public IP: {external_ip}")
        print("\n  ➜ Add this IP to Azure SQL firewall rules:")
        print("    Azure Portal → SQL servers → ezeos → Networking")
        print(f"    → Add client IP: {external_ip}")
        return external_ip
    except Exception as e:
        print(f"  Could not determine public IP: {e}")
        return None

def main():
    print("\n" + "="*60)
    print(" AZURE SQL CONNECTION DIAGNOSTIC TOOL")
    print("="*60)
    
    results = {
        'env_vars': check_env_vars(),
        'dns': check_dns_resolution(),
        'port': check_port_connectivity(),
        'pymssql': check_pymssql(),
        'connection': test_connection(),
    }
    
    get_public_ip()
    
    print_header("SUMMARY")
    
    if not results['pymssql']:
        print("""
  ❌ pymssql IS NOT INSTALLED

  Run: pip install pymssql
""")
    elif not results['port']:
        print("""
  ❌ PORT 1433 IS NOT REACHABLE
  
  This confirms the issue is with Azure network configuration.
  
  SOLUTION - Do these steps in Azure Portal:
  
  1. Go to: Azure Portal → SQL servers → ezeos → Networking
  
  2. Under "Public network access":
     ✓ Change from "Disabled" to "Selected networks"
  
  3. Under "Firewall rules":
     ✓ Click "Add your client IPv4 address" 
     OR manually add your IP address shown above
  
  4. Under "Exceptions":
     ✓ Check "Allow Azure services and resources to access this server"
     (Required for GitHub Codespaces)
  
  5. Click "Save" at the top
  
  6. Wait 2-3 minutes for changes to propagate
  
  7. Run this diagnostic again
""")
    elif not results['connection'] and results['port']:
        print("""
  ⚠️  PORT IS REACHABLE BUT CONNECTION FAILED
  
  This suggests an authentication or database issue.
  Check:
  - Password is correct
  - Username is correct (ala)
  - Database exists (users)
""")
    elif results['connection']:
        print("""
  ✅ ALL CHECKS PASSED - CONNECTION SUCCESSFUL!
  
  You can now run:
  - python migrations/azure_sql_schema.sql (via SQL client)
  - python migrations/migrate_data_to_azure.py
""")
    else:
        print("""
  ⚠️  Some checks failed. Review the output above.
""")

if __name__ == '__main__':
    main()
