#!/usr/bin/env python3
"""
Convert OnlineRetail.csv to SQLite database
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime

def convert_csv_to_sqlite():
    """Convert OnlineRetail.csv to OnlineRetail.db SQLite database"""
    
    # File paths
    csv_file = 'data/OnlineRetail.csv'
    db_file = 'data/OnlineRetail.db'
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return
    
    print(f"Reading CSV file: {csv_file}")
    
    # Read CSV file
    try:
        df = pd.read_csv(csv_file)
        print(f"Successfully loaded {len(df)} rows from CSV")
        
        # Display basic info about the dataset
        print("\nDataset Info:")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # Show data types
        print("\nData types:")
        print(df.dtypes)
        
        # Check for missing values
        print("\nMissing values:")
        print(df.isnull().sum())
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Data preprocessing
    print("\nPreprocessing data...")
    
    # Convert InvoiceDate to datetime
    try:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%m/%d/%Y %H:%M')
        print("✓ InvoiceDate converted to datetime")
    except Exception as e:
        print(f"Warning: Could not convert InvoiceDate: {e}")
    
    # Handle missing CustomerID (convert to string to allow NULL values)
    df['CustomerID'] = df['CustomerID'].astype('Int64')  # Use nullable integer type
    
    # Clean up data types
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
    
    print("✓ Data types cleaned")
    
    # Create SQLite database
    print(f"\nCreating SQLite database: {db_file}")
    
    try:
        # Remove existing database if it exists
        if os.path.exists(db_file):
            os.remove(db_file)
            print("✓ Existing database removed")
        
        # Create connection
        conn = sqlite3.connect(db_file)
        
        # Write dataframe to SQLite
        df.to_sql('online_retail', conn, index=False, if_exists='replace')
        
        # Create indexes for better performance
        cursor = conn.cursor()
        
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_no ON online_retail(InvoiceNo)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_code ON online_retail(StockCode)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_id ON online_retail(CustomerID)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_country ON online_retail(Country)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_date ON online_retail(InvoiceDate)")
        
        print("✓ Indexes created")
        
        # Get table info
        cursor.execute("SELECT COUNT(*) FROM online_retail")
        row_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA table_info(online_retail)")
        columns = cursor.fetchall()
        
        print(f"\n✓ Database created successfully!")
        print(f"✓ Table 'online_retail' created with {row_count} rows")
        print(f"✓ Columns: {[col[1] for col in columns]}")
        
        # Show some sample queries
        print("\nSample data from database:")
        cursor.execute("SELECT * FROM online_retail LIMIT 5")
        sample_data = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        for row in sample_data:
            print(dict(zip(column_names, row)))
        
        # Show database statistics
        print("\nDatabase Statistics:")
        cursor.execute("SELECT COUNT(DISTINCT InvoiceNo) as unique_invoices FROM online_retail")
        unique_invoices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT CustomerID) as unique_customers FROM online_retail WHERE CustomerID IS NOT NULL")
        unique_customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT StockCode) as unique_products FROM online_retail")
        unique_products = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT Country) as unique_countries FROM online_retail")
        unique_countries = cursor.fetchone()[0]
        
        print(f"✓ Unique invoices: {unique_invoices}")
        print(f"✓ Unique customers: {unique_customers}")
        print(f"✓ Unique products: {unique_products}")
        print(f"✓ Unique countries: {unique_countries}")
        
        conn.close()
        
        # Show file size
        db_size = os.path.getsize(db_file) / 1024 / 1024
        print(f"✓ Database file size: {db_size:.2f} MB")
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return
    
    print(f"\n🎉 Conversion completed successfully!")
    print(f"SQLite database saved as: {db_file}")
    print(f"You can now use this database in your applications.")

if __name__ == "__main__":
    convert_csv_to_sqlite()
