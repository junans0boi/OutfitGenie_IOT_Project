from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import aiomysql

# FastAPI 앱 초기화
app = FastAPI()

# CORS 설정
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 설정
DATABASE = {
    'user': 'root',
    'password': '1234',
    'db': 'hollywood',
    'host': 'hollywood.kro.kr',
    'port': 3306,
}

# 데이터베이스 연결
async def get_db():
    conn = await aiomysql.connect(
        user=DATABASE['user'],
        password=DATABASE['password'],
        db=DATABASE['db'],
        host=DATABASE['host'],
        port=DATABASE['port'],
    )
    try:
        yield conn
    finally:
        conn.close()

# 모델 정의
class User(BaseModel):
    UserID: int = Field(None, alias="UserID")
    Username: str = Field(..., alias="Username")
    Password: str = Field(..., alias="Password")
    Nickname: str = Field(None, alias="Nickname")
    Location: str = Field(None, alias="Location")

class UserLogin(BaseModel):
    Username: str
    Password: str

class Clothes(BaseModel):
    ClothesID: int
    UserID: int
    Username: str
    ImagePath: str = None
    Category: str = None
    Color: str = None

# 루트 URL (/)에서 index.html 파일 제공
@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = Path("templates") / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return HTMLResponse(content="index.html not found", status_code=404)

# 사용자 정보 가져오기
@app.get("/users/", response_model=List[User])
async def read_users(db = Depends(get_db)):
    async with db.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM OutfitGenie_Users")
        result = await cursor.fetchall()
        return [User(**row) for row in result]

# 특정 사용자 정보 가져오기
@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, db = Depends(get_db)):
    async with db.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM OutfitGenie_Users WHERE UserID = %s", (user_id,))
        result = await cursor.fetchone()
        if result:
            return User(**result)
        raise HTTPException(status_code=404, detail="User not found")

# 사용자 추가하기 (회원가입)
@app.post("/users/", response_model=User)
async def create_user(user: User, db = Depends(get_db)):
    try:
        print(user)  # 요청된 데이터 출력
        async with db.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO OutfitGenie_Users (Username, Password, Nickname, Location) VALUES (%s, %s, %s, %s)",
                (user.Username, user.Password, user.Nickname, user.Location)
            )
            await db.commit()
            user_id = cursor.lastrowid
            user.UserID = user_id
            return user
    except aiomysql.MySQLError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 로그인 기능 구현
@app.post("/login/")
async def login(user: UserLogin, db = Depends(get_db)):
    async with db.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            "SELECT * FROM OutfitGenie_Users WHERE Username = %s AND Password = %s",
            (user.Username, user.Password)
        )
        result = await cursor.fetchone()
        if result:
            return User(**result)
        raise HTTPException(status_code=401, detail="Invalid username or password")

# 메인 실행문
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
