from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from cassandra.cluster import Cluster
import uuid
import os
import socket
import time

app = FastAPI()

# Mount thư mục frontend để serve static files nếu cần
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="../btl"), name="static")


from fastapi.responses import FileResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/")
async def homepage():
    path = os.path.join(BASE_DIR, "..", "btl", "homepage.html")
    print("Serving file from:", os.path.abspath(path))
    return FileResponse(path)
# CORS cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # trong dev, production thì sửa lại
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Kết nối ScyllaDB, đổi scylla_host tùy môi trường
scylla_host = os.getenv("SCYLLA_HOST", "127.0.0.1")
wait_for_port(scylla_host, 9042)

cluster = Cluster([scylla_host])
session = cluster.connect()

print("Connected to ScyllaDB")

# Tạo keyspace và bảng cho giày nếu chưa có
try:
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS shop 
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
    """)
except Exception as e:
    print("Error creating keyspace:", e)

session.set_keyspace('shop')

try:
    session.execute("""
        CREATE TABLE IF NOT EXISTS shoes (
            id UUID PRIMARY KEY,
            name text,
            brand text,
            model text,
            price double,
            description text,
            images list<text>,
            detail_url text
        )
    """)
except Exception as e:
    print("Error creating table:", e)

# API trả danh sách giày
@app.get("/shoes")
async def get_shoes():
    try:
        rows = session.execute("SELECT * FROM shoes LIMIT 100")
        shoes = []
        for row in rows:
            shoes.append({
                "id": str(row.id),
                "name": row.name,
                "brand": row.brand,
                "model": row.model,
                "price": row.price,
                "description": row.description,
                "images": row.images,
                "detail_url": row.detail_url
            })
        return JSONResponse(content=shoes)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API trả chi tiết 1 đôi giày theo id
@app.get("/shoes/{shoe_id}")
async def get_shoe_detail(shoe_id: str):
    try:
        shoe_uuid = uuid.UUID(shoe_id)
        row = session.execute("SELECT * FROM shoes WHERE id = %s", (shoe_uuid,)).one()
        if not row:
            raise HTTPException(status_code=404, detail="Shoe not found")
        shoe = {
            "id": str(row.id),
            "name": row.name,
            "brand": row.brand,
            "model": row.model,
            "price": row.price,
            "description": row.description,
            "images": row.images,
            "detail_url": row.detail_url
        }
        return JSONResponse(content=shoe)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API thêm giày mới (POST) - tùy chọn, nếu bạn muốn
@app.post("/shoes")
async def add_shoe(request: Request):
    data = await request.json()
    try:
        shoe_id = uuid.uuid4()
        name = data["name"]
        brand = data.get("brand", "")
        model = data.get("model", "")
        price = float(data.get("price", 0))
        description = data.get("description", "")
        images = data.get("images", [])
        detail_url = data.get("detail_url", "")

        session.execute("""
            INSERT INTO shoes (id, name, brand, model, price, description, images, detail_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (shoe_id, name, brand, model, price, description, images, detail_url))

        return {"status": "success", "id": str(shoe_id)}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
