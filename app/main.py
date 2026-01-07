import pathway as pw
import time
import os
from datetime import datetime
import random

# Define the schema
class MetricsSchema(pw.Schema):
    metric: str
    value: int
    timestamp: str

# Custom connector for business metrics
class BusinessMetricsConnector(pw.io.python.ConnectorSubject):
    def run(self):
        counter = 0
        while True:
            timestamp = datetime.now().isoformat()
            
            # Add randomness to ensure values always change
            random_offset = random.randint(0, 10)
            
            # Simulate real business metrics with variation
            self.next(
                metric="Sales",
                value=100 + (counter % 50) + random_offset,
                timestamp=timestamp
            )
            self.next(
                metric="Profit",
                value=25 + (counter % 20) + random_offset,
                timestamp=timestamp
            )
            self.next(
                metric="New_Users",
                value=5 + (counter % 10) + random_offset,
                timestamp=timestamp
            )
            
            counter += 1
            time.sleep(2)

# Read from connector
metrics_table = pw.io.python.read(
    BusinessMetricsConnector(),
    schema=MetricsSchema,
    mode="streaming"
)

# Write all metrics directly (no groupby)
pw.io.jsonlines.write(metrics_table, "/app/web/metrics.jsonl")
pw.io.csv.write(metrics_table, "/app/output/live_data.csv")
pw.io.csv.write(metrics_table, "/dev/stdout")

# Run the engine
pw.run()