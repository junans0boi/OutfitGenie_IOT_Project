from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Initialize the FastAPI app
app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="templates"), name="static")

# Serve index.html at the root URL
@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = Path("templates") / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return HTMLResponse(content="index.html not found", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
