#!/usr/bin/env python3
"""
Migration Verification Script: SQLite vs Azure SQL
===================================================

This script verifies that data was successfully migrated from SQLite to Azure SQL
by comparing record counts and performing sample data checks.

Verification Steps:
    1. Compare record counts between SQLite and Azure SQL
    2. Sample data integrity checks
    3. Generate verification report

Usage:
    python migrations/verify_migration.py

Prerequisites:
    - Migration script has been run (migrate_data_to_azure.py)
    - Environment variables or manual configuration for Azure SQL credentials
    - pymssql installed (pip install pymssql)
"""

import os
import sys
import sqlite3
import pymssql
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# CONFIGURATION
# =============================================================================

# SQLite source database path
SQLITE_DB_PATH = "instance/lab_data.db"

# Azure SQL Server configuration
AZURE_SQL_SERVER = os.environ.get("AZURE_SQL_SERVER", "ezeos.database.windows.net")
AZURE_SQL_USERNAME = os.environ.get("AZURE_SQL_USERNAME", "ala")
AZURE_SQL_PASSWORD = os.environ.get("AZURE_SQL_PASSWORD", "")

# Database names
USERS_DATABASE = "users"
MAIN_DATABASE = "main"

# Number of sample records to check
SAMPLE_SIZE = 5


# =============================================================================
# TABLE DEFINITIONS
# =============================================================================

# Tables in 'users' database
USERS_DB_TABLES = {
    "users": {
        "key_column": "id",
        "check_columns": ["user_id", "email", "is_active"]
    },
    "admin_users": {
        "key_column": "id",
        "check_columns": ["user_id", "admin_level"]
    }
}

# Tables in 'main' database
MAIN_DB_TABLES = {
    "user_sessions": {
        "key_column": "id",
        "check_columns": ["session_id", "user_id", "current_page", "completed"]
    },
    "form_submissions": {
        "key_column": "id",
        "check_columns": ["session_id", "user_id", "department"]
    },
    "audit_log": {
        "key_column": "id",
        "check_columns": ["user_id", "action", "table_name"]
    }
}


# =============================================================================
# UTILITY CLASSES
# =============================================================================

class VerificationResult:
    """Represents the result of a single verification check."""
    
    def __init__(self, check_name: str, passed: bool, message: str = ""):
        self.check_name = check_name
        self.passed = passed
        self.message = message


class TableVerification:
    """Stores verification results for a single table."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.sqlite_count: Optional[int] = None
        self.azure_count: Optional[int] = None
        self.count_match: bool = False
        self.sample_checks: List[VerificationResult] = []
        self.errors: List[str] = []
    
    @property
    def passed(self) -> bool:
        """Check if all verifications passed for this table."""
        if not self.count_match:
            return False
        return all(check.passed for check in self.sample_checks)


class VerificationReport:
    """Comprehensive verification report."""
    
    def __init__(self):
        self.tables: Dict[str, TableVerification] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.connection_errors: List[str] = []
    
    def start(self):
        """Mark verification start time."""
        self.start_time = datetime.now()
    
    def end(self):
        """Mark verification end time."""
        self.end_time = datetime.now()
    
    def add_table(self, table: TableVerification):
        """Add table verification results."""
        self.tables[table.table_name] = table
    
    def add_connection_error(self, error: str):
        """Add a connection-level error."""
        self.connection_errors.append(error)
    
    @property
    def all_passed(self) -> bool:
        """Check if all verifications passed."""
        if self.connection_errors:
            return False
        return all(table.passed for table in self.tables.values())
    
    def print_report(self):
        """Print comprehensive verification report."""
        print("\n" + "=" * 80)
        print("MIGRATION VERIFICATION REPORT")
        print("=" * 80)
        
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            print(f"\nVerification Duration: {duration:.2f} seconds")
            print(f"Started:  {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Finished: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Connection errors
        if self.connection_errors:
            print("\n" + "-" * 80)
            print("CONNECTION ERRORS:")
            print("-" * 80)
            for error in self.connection_errors:
                print(f"  ❌ {error}")
        
        # Record Count Comparison
        print("\n" + "-" * 80)
        print("RECORD COUNT COMPARISON")
        print("-" * 80)
        print(f"\n{'Table':<25} {'SQLite':>12} {'Azure SQL':>12} {'Match':>10} {'Status':>10}")
        print("-" * 80)
        
        for table_name, table in self.tables.items():
            sqlite_str = str(table.sqlite_count) if table.sqlite_count is not None else "N/A"
            azure_str = str(table.azure_count) if table.azure_count is not None else "N/A"
            match_str = "Yes" if table.count_match else "No"
            status = "✅ PASS" if table.count_match else "❌ FAIL"
            
            print(f"{table_name:<25} {sqlite_str:>12} {azure_str:>12} {match_str:>10} {status:>10}")
        
        # Sample Data Checks
        print("\n" + "-" * 80)
        print("SAMPLE DATA INTEGRITY CHECKS")
        print("-" * 80)
        
        for table_name, table in self.tables.items():
            print(f"\n  📋 {table_name}:")
            
            if table.errors:
                for error in table.errors:
                    print(f"     ❌ ERROR: {error}")
            
            if not table.sample_checks:
                print(f"     ⚠️  No sample checks performed")
                continue
            
            for check in table.sample_checks:
                status = "✅" if check.passed else "❌"
                print(f"     {status} {check.check_name}: {check.message}")
        
        # Summary
        print("\n" + "=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tables = len(self.tables)
        passed_tables = sum(1 for t in self.tables.values() if t.passed)
        failed_tables = total_tables - passed_tables
        
        print(f"\n  Total Tables Verified: {total_tables}")
        print(f"  Tables Passed: {passed_tables}")
        print(f"  Tables Failed: {failed_tables}")
        
        print("\n" + "=" * 80)
        if self.all_passed:
            print("✅ VERIFICATION PASSED - Migration data is consistent")
        else:
            print("❌ VERIFICATION FAILED - Please review the issues above")
        print("=" * 80 + "\n")


# =============================================================================
# DATABASE CONNECTION FUNCTIONS
# =============================================================================

def get_sqlite_connection() -> sqlite3.Connection:
    """Create connection to SQLite database."""
    if not os.path.exists(SQLITE_DB_PATH):
        raise FileNotFoundError(f"SQLite database not found: {SQLITE_DB_PATH}")
    
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_azure_connection(database: str, timeout: int = 60) -> pymssql.Connection:
    """
    Create connection to Azure SQL database.

    Args:
        database: Database name ('users' or 'main')
        timeout: Connection timeout in seconds

    Returns:
        pymssql.Connection object
    """
    if not AZURE_SQL_PASSWORD:
        raise ValueError(
            "Azure SQL password not set. Set AZURE_SQL_PASSWORD environment variable."
        )

    return pymssql.connect(
        server=AZURE_SQL_SERVER,
        user=AZURE_SQL_USERNAME,
        password=AZURE_SQL_PASSWORD,
        database=database,
        tds_version='7.4',
        login_timeout=timeout,
    )


# =============================================================================
# VERIFICATION FUNCTIONS
# =============================================================================

def table_exists_sqlite(conn: sqlite3.Connection, table_name: str) -> bool:
    """Check if table exists in SQLite."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None


def table_exists_azure(conn: pymssql.Connection, table_name: str) -> bool:
    """Check if table exists in Azure SQL."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = %s",
        (table_name,)
    )
    result = cursor.fetchone()
    return result[0] > 0 if result else False


def get_sqlite_count(conn: sqlite3.Connection, table_name: str) -> int:
    """Get record count from SQLite table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    result = cursor.fetchone()
    return result[0] if result else 0


def get_azure_count(conn: pymssql.Connection, table_name: str) -> int:
    """Get record count from Azure SQL table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    result = cursor.fetchone()
    return result[0] if result else 0


def get_sqlite_sample(conn: sqlite3.Connection, table_name: str, 
                      key_column: str, columns: List[str], limit: int) -> List[Dict[str, Any]]:
    """Get sample records from SQLite table."""
    cursor = conn.cursor()
    
    # Get available columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    available_cols = {row[1] for row in cursor.fetchall()}
    
    # Filter to columns that exist
    select_cols = [key_column] + [c for c in columns if c in available_cols]
    cols_str = ", ".join(select_cols)
    
    cursor.execute(f"SELECT {cols_str} FROM {table_name} ORDER BY {key_column} LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    return [dict(zip(select_cols, row)) for row in rows]


def get_azure_sample(conn: pymssql.Connection, table_name: str,
                     key_column: str, columns: List[str], ids: List[Any]) -> Dict[Any, Dict[str, Any]]:
    """Get specific records from Azure SQL table by IDs."""
    if not ids:
        return {}

    cursor = conn.cursor()

    # Get available columns
    cursor.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %s",
        (table_name,)
    )
    available_cols = {row[0] for row in cursor.fetchall()}

    # Filter to columns that exist
    select_cols = [key_column] + [c for c in columns if c in available_cols]
    cols_str = ", ".join(select_cols)

    # Build IN clause
    placeholders = ", ".join(["%s" for _ in ids])
    
    cursor.execute(
        f"SELECT {cols_str} FROM {table_name} WHERE {key_column} IN ({placeholders})",
        ids
    )
    rows = cursor.fetchall()
    
    return {row[0]: dict(zip(select_cols, row)) for row in rows}


def normalize_value(value: Any) -> Any:
    """Normalize values for comparison (handle boolean/bit differences)."""
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int) and value in (0, 1):
        return value
    return value


def compare_records(sqlite_record: Dict[str, Any], azure_record: Dict[str, Any],
                    columns: List[str]) -> Tuple[bool, List[str]]:
    """
    Compare records from SQLite and Azure SQL.
    
    Returns:
        Tuple of (match, list of mismatched columns)
    """
    mismatches = []
    
    for col in columns:
        sqlite_val = normalize_value(sqlite_record.get(col))
        azure_val = normalize_value(azure_record.get(col))
        
        if sqlite_val != azure_val:
            mismatches.append(col)
    
    return len(mismatches) == 0, mismatches


def verify_table(
    sqlite_conn: sqlite3.Connection,
    azure_conn: pymssql.Connection,
    table_name: str,
    config: Dict[str, Any]
) -> TableVerification:
    """
    Verify data migration for a single table.
    
    Args:
        sqlite_conn: SQLite connection
        azure_conn: Azure SQL connection
        table_name: Name of table to verify
        config: Configuration dict with key_column and check_columns
    
    Returns:
        TableVerification object with results
    """
    result = TableVerification(table_name)
    
    key_column = config["key_column"]
    check_columns = config["check_columns"]
    
    # Check if tables exist
    if not table_exists_sqlite(sqlite_conn, table_name):
        result.errors.append(f"Table '{table_name}' not found in SQLite")
        return result
    
    if not table_exists_azure(azure_conn, table_name):
        result.errors.append(f"Table '{table_name}' not found in Azure SQL")
        return result
    
    # Get counts
    try:
        result.sqlite_count = get_sqlite_count(sqlite_conn, table_name)
    except Exception as e:
        result.errors.append(f"Failed to count SQLite records: {e}")
    
    try:
        result.azure_count = get_azure_count(azure_conn, table_name)
    except Exception as e:
        result.errors.append(f"Failed to count Azure SQL records: {e}")
    
    # Check count match
    if result.sqlite_count is not None and result.azure_count is not None:
        result.count_match = result.sqlite_count == result.azure_count
    
    # Sample data checks
    if result.sqlite_count == 0:
        result.sample_checks.append(VerificationResult(
            "Empty table check",
            result.azure_count == 0,
            "Source table is empty" if result.azure_count == 0 else "Source empty but Azure has data"
        ))
        return result
    
    try:
        # Get sample records from SQLite
        sqlite_samples = get_sqlite_sample(
            sqlite_conn, table_name, key_column, check_columns, SAMPLE_SIZE
        )
        
        if not sqlite_samples:
            result.sample_checks.append(VerificationResult(
                "Sample retrieval",
                False,
                "Could not retrieve sample records from SQLite"
            ))
            return result
        
        # Get corresponding records from Azure
        sample_ids = [r[key_column] for r in sqlite_samples]
        azure_samples = get_azure_sample(
            azure_conn, table_name, key_column, check_columns, sample_ids
        )
        
        # Compare each sample record
        records_checked = 0
        records_matched = 0
        
        for sqlite_record in sqlite_samples:
            record_id = sqlite_record[key_column]
            
            if record_id not in azure_samples:
                result.sample_checks.append(VerificationResult(
                    f"Record {record_id}",
                    False,
                    "Not found in Azure SQL"
                ))
                records_checked += 1
                continue
            
            azure_record = azure_samples[record_id]
            matched, mismatches = compare_records(
                sqlite_record, azure_record, check_columns
            )
            
            records_checked += 1
            if matched:
                records_matched += 1
        
        # Add summary check
        if records_checked > 0:
            all_matched = records_matched == records_checked
            result.sample_checks.append(VerificationResult(
                f"Sample data integrity ({records_checked} records)",
                all_matched,
                f"{records_matched}/{records_checked} records match" 
                + ("" if all_matched else " - Some records have mismatches")
            ))
        
    except Exception as e:
        result.errors.append(f"Sample check failed: {e}")
    
    return result


def verify_database_tables(
    sqlite_conn: sqlite3.Connection,
    azure_conn: pymssql.Connection,
    tables: Dict[str, Dict[str, Any]],
    database_name: str,
    report: VerificationReport
):
    """
    Verify all tables for a specific database.
    
    Args:
        sqlite_conn: SQLite connection
        azure_conn: Azure SQL connection
        tables: Dictionary of table configurations
        database_name: Name of database being verified
        report: VerificationReport object to add results to
    """
    print(f"\n  Verifying '{database_name}' database tables...")
    
    for table_name, config in tables.items():
        print(f"    Checking {table_name}...", end=" ", flush=True)
        
        try:
            result = verify_table(sqlite_conn, azure_conn, table_name, config)
            report.add_table(result)
            
            if result.passed:
                print("✅")
            else:
                print("❌")
        except Exception as e:
            result = TableVerification(table_name)
            result.errors.append(str(e))
            report.add_table(result)
            print(f"❌ Error: {e}")


# =============================================================================
# MAIN VERIFICATION FUNCTION
# =============================================================================

def run_verification():
    """
    Execute the complete verification of data migration.
    """
    print("\n" + "=" * 70)
    print("MIGRATION VERIFICATION: SQLite vs Azure SQL")
    print("=" * 70)
    print(f"\nSource: {SQLITE_DB_PATH}")
    print(f"Target Server: {AZURE_SQL_SERVER}")
    print(f"Target Databases: {USERS_DATABASE}, {EZEOS_DATABASE}")
    print(f"Sample Size: {SAMPLE_SIZE} records per table")
    
    report = VerificationReport()
    report.start()
    
    # Validate Azure SQL password is set
    if not AZURE_SQL_PASSWORD:
        print("\n❌ ERROR: Azure SQL password not configured.")
        print("   Set the AZURE_SQL_PASSWORD environment variable:")
        print("   export AZURE_SQL_PASSWORD='your-password-here'")
        sys.exit(1)
    
    # Connect to SQLite
    print("\n" + "-" * 50)
    print("Connecting to databases...")
    print("-" * 50)
    
    try:
        sqlite_conn = get_sqlite_connection()
        print(f"  ✓ Connected to SQLite: {SQLITE_DB_PATH}")
    except FileNotFoundError as e:
        report.add_connection_error(str(e))
        print(f"  ❌ ERROR: {e}")
        report.end()
        report.print_report()
        sys.exit(1)
    except Exception as e:
        report.add_connection_error(f"SQLite connection failed: {e}")
        print(f"  ❌ ERROR connecting to SQLite: {e}")
        report.end()
        report.print_report()
        sys.exit(1)
    
    # Verify 'users' database
    print("\n" + "-" * 50)
    print("Verifying 'users' database...")
    print("-" * 50)
    
    try:
        users_conn = get_azure_connection(USERS_DATABASE)
        print(f"  ✓ Connected to Azure SQL ({USERS_DATABASE})")
        verify_database_tables(sqlite_conn, users_conn, USERS_DB_TABLES, USERS_DATABASE, report)
        users_conn.close()
    except Exception as e:
        report.add_connection_error(f"Failed to connect to '{USERS_DATABASE}' database: {e}")
        print(f"  ❌ ERROR: {e}")
    
    # Verify 'main' database
    print("\n" + "-" * 50)
    print("Verifying 'main' database...")
    print("-" * 50)

    try:
        main_conn = get_azure_connection(MAIN_DATABASE)
        print(f"  ✓ Connected to Azure SQL ({MAIN_DATABASE})")
        verify_database_tables(sqlite_conn, main_conn, MAIN_DB_TABLES, MAIN_DATABASE, report)
        main_conn.close()
    except Exception as e:
        report.add_connection_error(f"Failed to connect to '{MAIN_DATABASE}' database: {e}")
        print(f"  ❌ ERROR: {e}")
    
    # Close SQLite connection
    sqlite_conn.close()
    
    # Complete verification
    report.end()
    report.print_report()
    
    # Return exit code based on results
    if not report.all_passed:
        sys.exit(1)
    sys.exit(0)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    run_verification()
