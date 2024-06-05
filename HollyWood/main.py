from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import aiomysql
import logging
import base64
from OutfitGenie.getWeather import get_weather # 날씨 API 코드 Import 

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
    'host': 'localhost',
    'port': 3306,
}

# 데이터베이스 연결 풀 초기화
async def get_db():
    pool = await aiomysql.create_pool(
        user=DATABASE['user'],
        password=DATABASE['password'],
        db=DATABASE['db'],
        host=DATABASE['host'],
        port=DATABASE['port'],
        maxsize=10
    )
    async with pool.acquire() as conn:
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

class UpdateLocation(BaseModel):
    UserID: int
    gridX: float
    gridY: float

class Clothes(BaseModel):
    ClothesID: int
    UserID: int
    ImageData: str = None  # bytes -> str로 변경
    Category: str = None
    Color: str = None

class Outfit(BaseModel):
    ClothesIDs: List[int]

# 루트 URL (/)에서 index.html 파일 제공
@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = Path("templates") / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return HTMLResponse(content="index.html not found", status_code=404)

# 사용자 정보 가져오기
@app.get("/users/", response_model=List[User])
async def read_users(db=Depends(get_db)):
    async with db.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM outfitgenie_users")
        result = await cursor.fetchall()
        return [User(**row) for row in result]

# 특정 사용자 정보 가져오기
@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, db=Depends(get_db)):
    async with db.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM outfitgenie_users WHERE UserID = %s", (user_id,))
        result = await cursor.fetchone()
        if result:
            return User(**result)
        raise HTTPException(status_code=404, detail="User not found")

# 사용자 추가하기 (회원가입)
@app.post("/users/", response_model=User)
async def create_user(user: User, db=Depends(get_db)):
    try:
        async with db.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO outfitgenie_users (Username, Password, Nickname, gridX, gridY) VALUES (%s, %s, %s, %s, %s)",
                (user.Username, user.Password, user.Nickname, user.gridX, user.gridY)
            )
            await db.commit()
            user_id = cursor.lastrowid
            user.UserID = user_id
            return user
    except aiomysql.MySQLError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 로그인 기능 구현
@app.post("/login/")
async def login(user: UserLogin, db=Depends(get_db)):
    async with db.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            "SELECT * FROM outfitgenie_users WHERE Username = %s AND Password = %s",
            (user.Username, user.Password)
        )
        result = await cursor.fetchone()
        if result:
            return User(**result)
        raise HTTPException(status_code=401, detail="Invalid username or password")

# 사용자 위치 정보 업데이트
@app.post("/update_location/", response_model=User)
async def update_location(update: UpdateLocation, db=Depends(get_db)):
    async with db.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            "UPDATE outfitgenie_users SET gridX = %s, gridY = %s WHERE UserID = %s",
            (update.gridX, update.gridY, update.UserID)
        )
        await db.commit()
        await cursor.execute("SELECT * FROM outfitgenie_users WHERE UserID = %s", (update.UserID,))
        result = await cursor.fetchone()
        if result:
            return User(**result)
        raise HTTPException(status_code=404, detail="User not found")
    
    


@app.post("/upload_clothes/")
async def upload_clothes(user_id: int = Form(...), category: str = Form(...), color: str = Form(...), file: UploadFile = File(...), db=Depends(get_db)):
    try:
        logging.info(f"Received upload request: user_id={user_id}, filename={file.filename}")

        # 파일 데이터 읽기
        file_data = await file.read()
        encoded_file_data = base64.b64encode(file_data).decode('utf-8')

        # 데이터베이스에 옷 정보 삽입
        async with db.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO outfitgenie_clothes (UserID, ImageData, Category, Color) VALUES (%s, %s, %s, %s)",
                (user_id, encoded_file_data, category, color)
            )
            await db.commit()
            clothes_id = cursor.lastrowid
            return Clothes(ClothesID=clothes_id, UserID=user_id, ImageData=encoded_file_data, Category=category, Color=color)
    except aiomysql.MySQLError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error during upload: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# 사용자 이름으로 옷 데이터 가져오기
@app.get("/clothes/{username}", response_model=List[Clothes])
async def get_clothes_by_username(username: str, db=Depends(get_db)):
    try:
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
                SELECT c.* FROM outfitgenie_clothes c
                JOIN outfitgenie_users u ON c.UserID = u.UserID
                WHERE u.Username = %s
            """, (username,))
            result = await cursor.fetchall()

            clothes_list = []
            for row in result:
                # 바이너리 데이터를 base64로 인코딩
                row['ImageData'] = base64.b64encode(row['ImageData']).decode('utf-8')
                clothes_list.append(Clothes(**row))

            return clothes_list
    except aiomysql.MySQLError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# 옷 검색 기능
@app.get("/search_clothes", response_model=List[Clothes])
async def search_clothes(category: str = "", color: str = "", db=Depends(get_db)):
    query = "SELECT * FROM outfitgenie_clothes WHERE 1=1"
    params = []
    if category:
        query += " AND Category = %s"
        params.append(category)
    if color:
        query += " AND Color = %s"
        params.append(color)
    
    try:
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, params)
            result = await cursor.fetchall()

            clothes_list = []
            for row in result:
                row['ImageData'] = base64.b64encode(row['ImageData']).decode('utf-8')
                clothes_list.append(Clothes(**row))

            return clothes_list
    except aiomysql.MySQLError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# 옷 세트 만들기
@app.post("/create_outfit")
async def create_outfit(outfit: Outfit, db=Depends(get_db)):
    try:
        async with db.cursor() as cursor:
            for clothes_id in outfit.ClothesIDs:
                await cursor.execute(
                    "INSERT INTO outfitgenie_outfits (ClothesID) VALUES (%s)",
                    (clothes_id,)
                )
            await db.commit()
            return {"message": "Outfit created successfully"}
    except aiomysql.MySQLError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# 프로필 업데이트
@app.post("/update_profile")
async def update_profile(user_id: int = Form(...), nickname: str = Form(...), db=Depends(get_db)):
    try:
        async with db.cursor() as cursor:
            await cursor.execute(
                "UPDATE outfitgenie_users SET Nickname = %s WHERE UserID = %s",
                (nickname, user_id)
            )
            await db.commit()
            return {"message": "Profile updated successfully"}
    except aiomysql.MySQLError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# weather api
@app.get("/getWeather")
async def read_weather():
    weather_data = get_weather()  # getWeather.py의 함수를 호출하여 날씨 데이터를 가져옴
    return {"weather": weather_data}

# 메인 실행문
if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("main:app", host="0.0.0.0", port=8001, log_level="info")