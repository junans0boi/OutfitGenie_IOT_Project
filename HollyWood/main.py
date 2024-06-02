from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# FastAPI 앱 초기화
app = FastAPI()

# 정적 파일 디렉토리 마운트
# /static 경로로 요청이 들어오면 templates 디렉토리의 파일을 제공
app.mount("/static", StaticFiles(directory="templates"), name="static")

# 루트 URL (/)에서 index.html 파일 제공
@app.get("/", response_class=HTMLResponse)
async def read_index():
    # index.html 파일 경로 설정
    index_path = Path("templates") / "index.html"
    # index.html 파일이 존재하는지 확인하고, 존재하면 파일 내용을 반환
    if index_path.exists():
        return index_path.read_text()
    # 파일이 존재하지 않으면 404 상태 코드와 메시지 반환
    return HTMLResponse(content="index.html not found", status_code=404)

# 메인 실행문
# uvicorn을 사용하여 FastAPI 앱 실행
if __name__ == "__main__":
    import uvicorn
    # 앱을 0.0.0.0 호스트와 8000 포트에서 실행
    uvicorn.run(app, host="0.0.0.0", port=8000)
