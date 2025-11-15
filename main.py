from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import asyncpg
import os
import asyncio
import urllib.parse

app = FastAPI(title="Login Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

# Database connection
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{urllib.parse.quote(os.getenv('POSTGRES_PASSWORD'))}@{os.getenv('POSTGRES_SRV_HOSTNAME')}:5432/{os.getenv('DATABASE')}"

pool = None

async def connect_database():
    global pool
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
        print("✅ Login Service: Connected to PostgreSQL")
        return True
    except Exception as e:
        print(f"❌ Login Service: PostgreSQL connection failed: {str(e)}")
        return False

async def get_db_connection():
    if not pool:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
    return pool

@app.on_event("startup")
async def startup_event():
    await connect_database()

@app.get("/")
async def get_login_info():
    db_status = "Connected to PostgreSQL" if pool else "Database disconnected"
    return {
        "service": "Login Service",
        "message": "Login API is ready",
        "dbStatus": db_status,
        "info": "You are in Login API - User authentication endpoint",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/")
async def login(credentials: LoginRequest):
    try:
        db_pool = await get_db_connection()
        
        async with db_pool.acquire() as connection:
            # Simulate user lookup in database
            user = await connection.fetchrow(
                "SELECT id, username FROM users WHERE username = $1 AND password = $2",
                credentials.username, credentials.password
            )
            
            if user:
                return {
                    "service": "Login Service",
                    "message": "Login successful",
                    "user": credentials.username,
                    "userId": user['id'],
                    "token": "sample-jwt-token-12345",
                    "dbStatus": "User authenticated from PostgreSQL",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Database error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
