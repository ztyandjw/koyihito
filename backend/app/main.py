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
from app.api.ollama_api import router as ollama_router

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
    ollama_router,
    prefix="/api/ollama",
    tags=["ollama"]
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

# 语音识别API
@app.post("/api/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...)):
    """
    接收音频文件并转换为文本
    
    这是一个模拟的语音识别API，实际项目中应该集成真正的语音识别服务
    例如:
    - 百度语音识别
    - 科大讯飞
    - Google Cloud Speech-to-Text
    - Azure Speech Services
    等
    """
    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(audio_file.filename)[1] if audio_file.filename else ".webm"
        temp_file_path = os.path.join(TEMP_DIR, f"{file_id}{file_extension}")
        
        # 保存上传的文件
        with open(temp_file_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)
            file_size = len(content)
        
        # 在实际应用中，这里应该调用语音识别API
        # 例如: result = call_speech_recognition_api(temp_file_path)
        
        # 模拟语音识别过程
        # 实际项目中替换为真实的语音识别调用
        import time
        time.sleep(1)  # 模拟处理延迟
        
        # 模拟返回结果
        result = {
            "success": True,
            "text": f"这是从语音识别API返回的文本。文件大小: {file_size/1024:.2f}KB",
            "confidence": 0.85,
            "file_id": file_id
        }
        
        # 清理临时文件
        try:
            os.remove(temp_file_path)
        except Exception as e:
            print(f"清理临时文件失败: {e}")
            
        return JSONResponse(result)
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

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