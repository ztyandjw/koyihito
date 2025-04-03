from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
import os
import subprocess
import threading
import time
import httpx
import uuid
from pathlib import Path
from .audio_api import router as audio_router  # 导入音频处理路由
from app.api.chat_api import router as chat_router

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)  # 上一级目录(backend)
media_dir = os.path.join(backend_dir, "chat_media")


# 挂载静态文件目录
app.mount("/chat_media", StaticFiles(directory=media_dir), name="chat_media")
print(f"静态文件服务已挂载: {media_dir} -> /chat_media")
# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 包含音频处理路由
app.include_router(audio_router)

# 注册 API 路由
app.include_router(
    chat_router,
    prefix="/api",
    tags=["chat"]  # 改为更通用的标签名
)

# 开发模式配置
DEV_MODE = True  # 可以通过环境变量控制
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
TEMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../temp"))

# 确保临时目录存在
os.makedirs(TEMP_DIR, exist_ok=True)

# 直接挂载 public 目录
app.mount("/public", StaticFiles(directory=os.path.join(FRONTEND_DIR, "public")), name="public")

# 根路径直接返回 index.html
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "public", "index.html"))



def start_vite_server():
    os.chdir(FRONTEND_DIR)
    subprocess.Popen(["npm", "run", "dev"], shell=True)

if DEV_MODE:
    print("DEV MODE ...")
    # 启动 Vite 开发服务器
    threading.Thread(target=start_vite_server, daemon=True).start()
    time.sleep(2)  # 等待 Vite 服务器启动
    
    @app.get("/{path:path}")
    async def proxy_to_vite(path: str, request: Request):
        # 排除 API 路由和已经处理的根路径
        if path.startswith("api/") or path == "":
            return {"error": "API endpoint not found"}
            
        async with httpx.AsyncClient() as client:
            try:
                # 注意这里使用 0.0.0.0 会导致问题，改为 localhost 或 127.0.0.1
                url = f"http://127.0.0.1:3000/{path}"
                response = await client.get(url, headers=dict(request.headers))
                return StreamingResponse(
                    content=response.aiter_bytes(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            except httpx.ConnectError:
                return {"error": "Could not connect to Vite dev server"}

    # 如果在开发模式下，挂载前端静态文件
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

else:
    print("prod mode")
    # 生产模式：服务静态文件
    app.mount("/", StaticFiles(directory=os.path.join(FRONTEND_DIR, "dist"), html=True), name="static")

# API路由
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("Starting server on 0.0.0.0:3888 - Access via http://YOUR_IP_ADDRESS:3888")
    uvicorn.run(app, host="0.0.0.0", port=3888, reload=True)