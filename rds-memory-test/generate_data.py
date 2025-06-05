#!/usr/bin/env python3

import uuid
import random
import datetime
import mysql.connector
import psycopg2
from psycopg2.extras import execute_batch
import time
import sys

def generate_test_data_batch(start_id, batch_size=10000):
    """Generate a batch of test data"""
    data = []
    base_time = datetime.datetime(2023, 1, 1)
    
    for i in range(start_id, start_id + batch_size):
        record_id = i  # int8 sequential
        uuid_text = str(uuid.uuid4())  # 36-character UUID
        category = random.randint(1, 4)  # int4 values 1-4
        
        random_days = random.randint(0, 365)
        random_seconds = random.randint(0, 86400)
        timestamp_col = base_time + datetime.timedelta(days=random_days, seconds=random_seconds)
        
        data.append((record_id, uuid_text, category, timestamp_col))
    
    return data

def insert_mysql_data_streaming(total_rows=12000000, batch_size=10000, host='localhost', port=3306, user='testuser', password='testpass', database='memory_test'):
    """Insert data into MySQL database using streaming approach"""
    print(f"Connecting to MySQL at {host}:{port}...")
    
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM test_data")
        
        insert_query = """
        INSERT INTO test_data (record_id, uuid_text, category, timestamp_col) 
        VALUES (%s, %s, %s, %s)
        """
        
        print(f"Inserting {total_rows:,} rows into MySQL in batches of {batch_size:,}...")
        start_time = time.time()
        
        total_inserted = 0
        for start_id in range(1, total_rows + 1, batch_size):
            current_batch_size = min(batch_size, total_rows - start_id + 1)
            batch_data = generate_test_data_batch(start_id, current_batch_size)
            
            cursor.executemany(insert_query, batch_data)
            connection.commit()
            
            total_inserted += len(batch_data)
            if total_inserted % 100000 == 0:
                print(f"Inserted {total_inserted:,} rows...")
        
        end_time = time.time()
        
        print(f"MySQL insertion completed in {end_time - start_time:.2f} seconds")
        
        cursor.execute("SELECT COUNT(*) FROM test_data")
        count = cursor.fetchone()[0]
        print(f"MySQL: {count:,} rows inserted successfully")
        
        cursor.close()
        connection.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
        return False

def insert_postgres_data(data, host='localhost', port=5432, user='testuser', password='testpass', database='memory_test'):
    """Insert data into PostgreSQL database"""
    print(f"Connecting to PostgreSQL at {host}:{port}...")
    
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM test_data")
        
        insert_query = """
        INSERT INTO test_data (record_id, uuid_text, category, timestamp_col) 
        VALUES (%s, %s, %s, %s)
        """
        
        print(f"Inserting {len(data)} rows into PostgreSQL...")
        start_time = time.time()
        
        batch_size = 1000
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            execute_batch(cursor, insert_query, batch, page_size=100)
            connection.commit()
            if (i + batch_size) % 100000 == 0:
                print(f"Inserted {i + batch_size:,} rows...")
        
        end_time = time.time()
        
        print(f"PostgreSQL insertion completed in {end_time - start_time:.2f} seconds")
        
        cursor.execute("SELECT COUNT(*) FROM test_data")
        count = cursor.fetchone()[0]
        print(f"PostgreSQL: {count} rows inserted successfully")
        
        cursor.close()
        connection.close()
        return True
        
    except psycopg2.Error as e:
        print(f"PostgreSQL Error: {e}")
        return False

def main():
    """Main function to generate and insert test data"""
    print("=== RDS Memory Test Data Generation ===")
    
    mysql_port = 3306
    postgres_port = 5432
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "1gb":
            mysql_port = 3307
            postgres_port = 5433
        elif sys.argv[1] == "2gb":
            mysql_port = 3308
            postgres_port = 5434
        elif sys.argv[1] == "16gb":
            mysql_port = 3309
            postgres_port = 5435
    
    print(f"Using MySQL port: {mysql_port}, PostgreSQL port: {postgres_port}")
    
    print("Using streaming insertion approach for 12M rows...")
    
    sample_data = generate_test_data_batch(1, 3)
    print("\nSample data (first 3 rows):")
    for i, row in enumerate(sample_data):
        print(f"  Row {i+1}: record_id={row[0]}, uuid={row[1][:8]}..., category={row[2]}, timestamp={row[3]}")
    
    print("\n--- MySQL Streaming Insertion ---")
    mysql_success = insert_mysql_data_streaming(total_rows=12000000, host='localhost', port=mysql_port)
    
    postgres_success = True
    
    print("\n=== Summary ===")
    print(f"MySQL insertion: {'SUCCESS' if mysql_success else 'FAILED'}")
    print(f"PostgreSQL insertion: {'SUCCESS' if postgres_success else 'FAILED'}")
    
    if mysql_success and postgres_success:
        print("Data generation and insertion completed successfully!")
        return 0
    else:
        print("Some insertions failed. Check database connections.")
        return 1

if __name__ == "__main__":
    exit(main())
