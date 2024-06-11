from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import aiomysql
import logging
import base64
from datetime import datetime
from OutfitGenie.getWeather import get_weather  # 날씨 API 코드 Import 
from OutfitGenie.getGrid import dfs_xy_conv

# FastAPI 앱 초기화
app = FastAPI()

# CORS 설정
origins = ["*"]
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

class User(BaseModel):
    UserID: int = Field(None, alias="UserID")
    Username: str = Field(..., alias="Username")
    Password: str = Field(..., alias="Password")
    Nickname: str = Field(None, alias="Nickname")
    gridX: float = Field(default=0.0, alias="gridX")
    gridY: float = Field(default=0.0, alias="gridY")

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

@app.get("/", response_class=HTMLResponse)
async def read_index():
    """
    루트 URL (/)에서 index.html 파일 제공
    """
    index_path = Path("templates") / "index.html"
    if (index_path.exists()):
        return index_path.read_text()
    return HTMLResponse(content="index.html not found", status_code=404)

@app.post("/login/")
async def login(user: UserLogin, db=Depends(get_db)):
    """
    로그인 기능 구현
    """
    async with db.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            "SELECT * FROM outfitgenie_users WHERE Username = %s AND Password = %s",
            (user.Username, user.Password)
        )
        result = await cursor.fetchone()
        if result:
            result['Location'] = result.get('Location', "")
            result['gridX'] = result.get('gridX', 0.0)
            result['gridY'] = result.get('gridY', 0.0)
            return User(**result)
        raise HTTPException(status_code=401, detail="Invalid username or password")


@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, db=Depends(get_db)):
    """
    특정 사용자 정보 가져오기
    """
    async with db.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM outfitgenie_users WHERE UserID = %s", (user_id,))
        result = await cursor.fetchone()
        if result:
            return User(**result)
        raise HTTPException(status_code=404, detail="User not found")

# 사용자 추가하기 (회원가입)
@app.post("/users/", response_model=User)
async def create_user(user: User, db=Depends(get_db)):
    """
    사용자 추가하기 (회원가입)
    """
    user.gridX = 0.0  # 기본값 0으로 설정
    user.gridY = 0.0  # 기본값 0으로 설정
    
    try:
        async with db.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO outfitgenie_users (Username, Password, Nickname, gridX, gridY) VALUES (%s, %s, %s, %s, %s)",
                (user.Username, user.Password, user.Nickname, user.gridX, user.gridY)
            )
            await db.commit()
            user.UserID = cursor.lastrowid
            return user
    except aiomysql.MySQLError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login/")
async def login(user: UserLogin, db=Depends(get_db)):
    """
    로그인 기능 구현
    """
    async with db.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            "SELECT * FROM outfitgenie_users WHERE Username = %s AND Password = %s",
            (user.Username, user.Password)
        )
        result = await cursor.fetchone()
        if result:
            result['Location'] = result.get('Location', "")
            result['gridX'] = result.get('gridX', 0.0)
            result['gridY'] = result.get('gridY', 0.0)
            return User(**result)
        raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/update_location/")
async def update_location(location: UpdateLocation, db=Depends(get_db)):
    """
    사용자 위치 정보 업데이트
    """
    try:
        async with db.cursor() as cursor:
            await cursor.execute(
                "UPDATE outfitgenie_users SET gridX = %s, gridY = %s WHERE UserID = %s",
                (location.gridX, location.gridY, location.UserID)
            )
            await db.commit()
            return {"message": "Location updated successfully"}
    except aiomysql.MySQLError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Define the upload_clothes function with correct type hinting
@app.post("/upload_clothes/")
async def upload_clothes(
    user_id: int = Form(...),
    image_data: str = Form(...),
    category: str = Form(...),
    color: str = Form(...),
    db: aiomysql.Connection = Depends(get_db)
):
    """
    옷 이미지 업로드
    """
    try:
        image_data_bytes = base64.b64decode(image_data)
        
        async with db.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO outfitgenie_clothes (UserID, ImageData, Category, Color) VALUES (%s, %s, %s, %s)",
                (user_id, image_data_bytes, category, color)
            )
            await db.commit()
            return {"message": "Image uploaded successfully"}
    except base64.binascii.Error as e:
        logging.error(f"Invalid image data: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid image data")
    except aiomysql.MySQLError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/clothes/{username}", response_model=List[Clothes])
async def get_clothes_by_username(username: str, db=Depends(get_db)):
    """
    사용자 이름으로 옷 데이터 가져오기
    """
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
                row['ImageData'] = base64.b64encode(row['ImageData']).decode('utf-8')
                clothes_list.append(Clothes(**row))

            return clothes_list
    except aiomysql.MySQLError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/search_clothes", response_model=List[Clothes])
async def search_clothes(category: str = "", color: str = "", db=Depends(get_db)):
    """
    옷 검색 기능
    """
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

@app.post("/create_outfit")
async def create_outfit(outfit: Outfit, db=Depends(get_db)):
    """
    옷 세트 만들기
    """
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

@app.post("/update_profile")
async def update_profile(user_id: int = Form(...), nickname: str = Form(...), db=Depends(get_db)):
    """
    프로필 업데이트
    """
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

# 날씨 데이터를 저장하는 함수
async def save_weather_data(weather_data: dict, db):
    query = """
    INSERT INTO outfitgenie_weather (date, location, hour00, hour01, hour02, hour03, hour04, hour05, hour06, hour07, hour08, hour09, hour10, hour11, hour12, hour13, hour14, hour15, hour16, hour17, hour18, hour19, hour20, hour21, hour22, hour23)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    # 날짜 형식을 변환 (YYYY-MM-DD)
    date_value = datetime.strptime(weather_data['date'], "%Y년 %m월 %d일").strftime("%Y-%m-%d")
    
    values = (
        date_value, weather_data['location'], weather_data.get('hour00'), weather_data.get('hour01'), 
        weather_data.get('hour02'), weather_data.get('hour03'), weather_data.get('hour04'), weather_data.get('hour05'), 
        weather_data.get('hour06'), weather_data.get('hour07'), weather_data.get('hour08'), weather_data.get('hour09'), 
        weather_data.get('hour10'), weather_data.get('hour11'), weather_data.get('hour12'), weather_data.get('hour13'), 
        weather_data.get('hour14'), weather_data.get('hour15'), weather_data.get('hour16'), weather_data.get('hour17'), 
        weather_data.get('hour18'), weather_data.get('hour19'), weather_data.get('hour20'), weather_data.get('hour21'), 
        weather_data.get('hour22'), weather_data.get('hour23')
    )
    async with db.cursor() as cursor:
        await cursor.execute(query, values)
        await db.commit()

@app.get("/getWeather/{user_id}")
async def get_weather_for_user(user_id: int, db=Depends(get_db)):
    """
    Get weather information for a specific user based on their location and save it to the database
    """
    async with db.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM outfitgenie_users WHERE UserID = %s", (user_id,))
        result = await cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        lat, lng = result['gridX'], result['gridY']
        gridX, gridY = dfs_xy_conv("toXY", lat, lng)
        weather_data = get_weather(gridX, gridY)
        
        if 'error' in weather_data:
            raise HTTPException(status_code=500, detail=weather_data['error'])
        
        await save_weather_data(weather_data, db)
        
        return weather_data

# Main execution block
if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")