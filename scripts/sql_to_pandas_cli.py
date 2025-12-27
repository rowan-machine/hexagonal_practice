#!/usr/bin/env python3
"""
Command-line interface for SQL to Pandas converter.

Usage:
    python scripts/sql_to_pandas_cli.py <sql_file> [--output <output_file>] [--table <table_name>]
    python scripts/sql_to_pandas_cli.py --sql "SELECT * FROM table" [--table <table_name>]
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.utils.sql_to_pandas import SQLToPandasConverter
except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease install required dependencies:")
    print("  pip install sqlglot pandas")
    sys.exit(1)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Convert SQL queries to pandas code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert SQL file
  python scripts/sql_to_pandas_cli.py queries/claims_gold.sql --table claims_silver
  
  # Convert SQL string
  python scripts/sql_to_pandas_cli.py --sql "SELECT * FROM claims_silver LIMIT 10" --table claims_silver
  
  # Save output to file
  python scripts/sql_to_pandas_cli.py queries/claims_gold.sql --output output.py --table claims_silver
        """
    )
    
    parser.add_argument(
        'sql_file',
        nargs='?',
        help='Path to SQL file'
    )
    
    parser.add_argument(
        '--sql',
        help='SQL query string (alternative to sql_file)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path for generated Python code'
    )
    
    parser.add_argument(
        '--table', '-t',
        help='Source table name (required if not in SQL)'
    )
    
    parser.add_argument(
        '--df-name',
        default='df',
        help='Name of the pandas DataFrame variable (default: df)'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.sql_file and not args.sql:
        parser.error("Either sql_file or --sql is required")
    
    if args.sql_file and args.sql:
        parser.error("Cannot specify both sql_file and --sql")
    
    # Get SQL content
    if args.sql_file:
        sql_path = Path(args.sql_file)
        if not sql_path.exists():
            print(f"Error: SQL file not found: {args.sql_file}")
            sys.exit(1)
        sql = sql_path.read_text()
    else:
        sql = args.sql
    
    # Create converter
    try:
        converter = SQLToPandasConverter(source_table=args.table)
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Convert
    try:
        if args.sql_file and args.output:
            # Use convert_file for file operations
            output_path = Path(args.output)
            code = converter.convert_file(
                args.sql_file,
                output_file=str(output_path),
                source_table=args.table
            )
            print(f"✓ Converted SQL to pandas code")
            print(f"✓ Saved to: {output_path}")
        else:
            # Convert and print
            code = converter.convert(
                sql,
                source_table=args.table,
                df_name=args.df_name
            )
            
            if args.output:
                output_path = Path(args.output)
                output_path.write_text(code)
                print(f"✓ Converted SQL to pandas code")
                print(f"✓ Saved to: {output_path}")
            else:
                print("\n" + "=" * 80)
                print("Generated Pandas Code:")
                print("=" * 80)
                print(code)
                print("=" * 80)
    
    except ValueError as e:
        print(f"Error converting SQL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

