from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from cassandra.cluster import Cluster
import uuid
import datetime
import time
import os

app = FastAPI()

# Cấu hình CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép mọi nguồn, dev thì ok
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép mọi method, bao gồm OPTIONS
    allow_headers=["*"],
)

# Đợi ScyllaDB khởi động
time.sleep(5)

# Kết nối đến ScyllaDB
scylla_host = os.getenv("SCYLLA_HOST", "scylla-node1")
cluster = Cluster([scylla_host])
session = cluster.connect()

print("Connected to ScyllaDB")

# Tạo keyspace và bảng như cũ
try:
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS iot 
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
    """)
except:
    pass

session.set_keyspace('iot')

try:
    session.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            sensor_id UUID,
            timestamp timestamp,
            temperature double,
            humidity double,
            PRIMARY KEY (sensor_id, timestamp)
        )
    """)
except:
    pass

@app.post("/data")
async def receive_data(request: Request):
    data = await request.json()
    sensor_id = uuid.UUID(data["sensor_id"])
    temperature = float(data["temperature"])
    humidity = float(data["humidity"])
    timestamp = datetime.datetime.utcnow()

    session.execute("""
        INSERT INTO sensor_data (sensor_id, timestamp, temperature, humidity)
        VALUES (%s, %s, %s, %s)
    """, (sensor_id, timestamp, temperature, humidity))

    return {"status": "success"}
