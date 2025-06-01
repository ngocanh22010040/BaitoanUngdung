from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from cassandra.cluster import Cluster
import uuid
import datetime
import time
import os
import socket
import time
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
def wait_for_port(host, port, timeout=60):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=3):
                print(f"Port {port} on {host} is open")
                return
        except OSError:
            time.sleep(1)
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for {host}:{port}")

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


@app.get("/data")
async def get_sensor_data():
    try:
        rows = session.execute("""
            SELECT sensor_id, timestamp, temperature, humidity 
            FROM sensor_data
            LIMIT 100
        """)

        result = []
        for row in rows:
            result.append({
                "sensor_id": str(row.sensor_id),
                "timestamp": row.timestamp.isoformat() if row.timestamp else None,
                "temperature": row.temperature,
                "humidity": row.humidity,
            })

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
@app.get("/")
async def root():
    return {"message": "API is running"}