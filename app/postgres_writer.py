#!/usr/bin/env python3
import time
import json
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'examdb',
    'user': 'admin',
    'password': 'admin123'
}

METRICS_FILE = '/app/web/metrics.jsonl'

def create_table_if_not_exists(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id SERIAL PRIMARY KEY,
                metric VARCHAR(50),
                value INTEGER,
                timestamp TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    print("Metrics table ready")

def read_latest_metrics():
    try:
        with open(METRICS_FILE, 'r') as f:
            lines = f.readlines()
            latest_lines = lines[-10:] if len(lines) >= 10 else lines
            metrics = []
            for line in latest_lines:
                if line.strip():
                    try:
                        metrics.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return metrics
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"rror reading file: {e}")
        return []

def insert_metrics(conn, metrics):
    if not metrics:
        return
    
    with conn.cursor() as cur:
        values = [
            (
                m['metric'],
                m['value'],
                datetime.fromisoformat(m['timestamp']) if m.get('timestamp') else datetime.now()
            )
            for m in metrics
        ]
        
        execute_values(
            cur,
            "INSERT INTO metrics (metric, value, timestamp) VALUES %s",
            values
        )
        conn.commit()
    print(f"Inserted {len(metrics)} metrics")

def main():
    print("PostgreSQL Writer started")
    
    while True:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            print(" Connected to PostgreSQL")
            break
        except psycopg2.OperationalError:
            print(" Waiting for PostgreSQL...")
            time.sleep(2)
    
    create_table_if_not_exists(conn)
    last_count = 0
    
    while True:
        try:
            metrics = read_latest_metrics()
            current_count = len(metrics)
            
            if current_count > last_count:
                new_metrics = metrics[last_count:]
                insert_metrics(conn, new_metrics)
                last_count = current_count
            
            time.sleep(5)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
