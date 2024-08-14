from fastapi import FastAPI, HTTPException
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from uuid import uuid4
from datetime import datetime
from database import create_keyspace_and_table
from pydantic import BaseModel


create_keyspace_and_table()

app = FastAPI()
cluster = Cluster(['cassandra'])
session = cluster.connect('user_keyspace')

class UserCreateRequest(BaseModel):
    username: str
    email: str

@app.post("/create_user/")
async def create_user(user: UserCreateRequest):
    try:
        # Generate a new UUID for the user
        user_id = uuid4()
        created_at = datetime.utcnow()

        # Insert the new user into the user_info table
        query = SimpleStatement("""
            INSERT INTO user_info (user_id, username, email, created_at)
            VALUES (%s, %s, %s, %s)
        """)
        session.execute(query, (user_id, user.username, user.email, created_at))

        return {"user_id": user_id, "username": user.username, "email": user.email, "created_at": created_at}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)