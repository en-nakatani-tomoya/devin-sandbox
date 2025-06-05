#!/usr/bin/env python3

import subprocess
import time
import json
import mysql.connector
import psycopg2
import sys
from datetime import datetime

def get_docker_stats(container_names):
    """Get memory usage statistics from Docker containers"""
    try:
        cmd = ["docker", "stats", "--no-stream", "--format", "json"] + container_names
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        stats = {}
        for line in result.stdout.strip().split('\n'):
            if line:
                data = json.loads(line)
                container_name = data['Name']
                memory_usage = data['MemUsage']
                memory_percent = data['MemPerc']
                stats[container_name] = {
                    'memory_usage': memory_usage,
                    'memory_percent': memory_percent
                }
        
        return stats
    except subprocess.CalledProcessError as e:
        print(f"Error getting Docker stats: {e}")
        return {}

def get_mysql_memory_info(host='localhost', port=3306, user='testuser', password='testpass', database='memory_test'):
    """Get MySQL memory usage information"""
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        cursor.execute("SHOW ENGINE INNODB STATUS")
        innodb_status = cursor.fetchone()[2]
        
        buffer_pool_info = {}
        for line in innodb_status.split('\n'):
            if 'Buffer pool size' in line:
                buffer_pool_info['buffer_pool_size'] = line.strip()
            elif 'Free buffers' in line:
                buffer_pool_info['free_buffers'] = line.strip()
            elif 'Database pages' in line:
                buffer_pool_info['database_pages'] = line.strip()
        
        cursor.execute("""
            SELECT 
                table_name,
                ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'test_data'
        """, (database,))
        
        table_info = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return {
            'buffer_pool_info': buffer_pool_info,
            'table_size_mb': table_info[1] if table_info else 0
        }
        
    except mysql.connector.Error as e:
        print(f"MySQL monitoring error: {e}")
        return {}

def get_postgres_memory_info(host='localhost', port=5432, user='testuser', password='testpass', database='memory_test'):
    """Get PostgreSQL memory usage information"""
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        cursor.execute("SELECT pg_size_pretty(pg_database_size(%s))", (database,))
        db_size = cursor.fetchone()[0]
        
        cursor.execute("SELECT pg_size_pretty(pg_total_relation_size('test_data'))")
        table_size = cursor.fetchone()[0]
        
        cursor.execute("SHOW shared_buffers")
        shared_buffers = cursor.fetchone()[0]
        
        cursor.execute("SHOW work_mem")
        work_mem = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return {
            'database_size': db_size,
            'table_size': table_size,
            'shared_buffers': shared_buffers,
            'work_mem': work_mem
        }
        
    except psycopg2.Error as e:
        print(f"PostgreSQL monitoring error: {e}")
        return {}

def monitor_memory(duration_seconds=60, interval_seconds=10, memory_limit="512mb"):
    """Monitor memory usage for specified duration"""
    print(f"=== Memory Monitoring ({memory_limit} limit) ===")
    print(f"Monitoring for {duration_seconds} seconds with {interval_seconds}s intervals")
    
    if memory_limit == "1gb":
        mysql_container = "mysql-memory-test-1gb"
        postgres_container = "postgres-memory-test-1gb"
        mysql_port = 3307
        postgres_port = 5433
    elif memory_limit == "2gb":
        mysql_container = "mysql-memory-test-2gb"
        postgres_container = "postgres-memory-test-2gb"
        mysql_port = 3308
        postgres_port = 5434
    elif memory_limit == "16gb":
        mysql_container = "mysql-memory-test-16gb"
        postgres_container = "postgres-memory-test-16gb"
        mysql_port = 3309
        postgres_port = 5435
    else:  # 512mb
        mysql_container = "mysql-memory-test"
        postgres_container = "postgres-memory-test"
        mysql_port = 3306
        postgres_port = 5432
    
    container_names = [mysql_container, postgres_container]
    
    start_time = time.time()
    measurements = []
    
    while time.time() - start_time < duration_seconds:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n--- {timestamp} ---")
        
        docker_stats = get_docker_stats(container_names)
        
        mysql_info = get_mysql_memory_info(port=mysql_port)
        
        postgres_info = get_postgres_memory_info(port=postgres_port)
        
        print("Docker Container Memory Usage:")
        for container, stats in docker_stats.items():
            print(f"  {container}: {stats['memory_usage']} ({stats['memory_percent']})")
        
        if mysql_info:
            print(f"MySQL Table Size: {mysql_info.get('table_size_mb', 'N/A')} MB")
            
        if postgres_info:
            print(f"PostgreSQL Database Size: {postgres_info.get('database_size', 'N/A')}")
            print(f"PostgreSQL Table Size: {postgres_info.get('table_size', 'N/A')}")
        
        measurement = {
            'timestamp': timestamp,
            'docker_stats': docker_stats,
            'mysql_info': mysql_info,
            'postgres_info': postgres_info
        }
        measurements.append(measurement)
        
        time.sleep(interval_seconds)
    
    return measurements

def main():
    """Main monitoring function"""
    memory_limit = "512mb"
    if len(sys.argv) > 1:
        memory_limit = sys.argv[1]
    
    print(f"Starting memory monitoring for {memory_limit} containers...")
    
    measurements = monitor_memory(duration_seconds=60, interval_seconds=10, memory_limit=memory_limit)
    
    results_file = f"memory_results_{memory_limit}.json"
    with open(results_file, 'w') as f:
        json.dump(measurements, f, indent=2, default=str)
    
    print(f"\nResults saved to {results_file}")
    
    if measurements:
        print("\n=== Summary ===")
        final_measurement = measurements[-1]
        
        print("Final Memory Usage:")
        for container, stats in final_measurement['docker_stats'].items():
            print(f"  {container}: {stats['memory_usage']} ({stats['memory_percent']})")
        
        mysql_info = final_measurement['mysql_info']
        postgres_info = final_measurement['postgres_info']
        
        if mysql_info:
            print(f"MySQL Table Size: {mysql_info.get('table_size_mb', 'N/A')} MB")
        
        if postgres_info:
            print(f"PostgreSQL Table Size: {postgres_info.get('table_size', 'N/A')}")

if __name__ == "__main__":
    main()
