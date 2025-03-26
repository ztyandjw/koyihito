from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
from pathlib import Path

router = APIRouter()

# 配置音频文件存储路径
AUDIO_DIR = Path(__file__).parent.parent / "audio_files"
AUDIO_DIR.mkdir(exist_ok=True)

@router.post("/api/upload-audio")
async def upload_audio(audio_file: UploadFile = File(...)):
    try:
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = str(uuid.uuid4())[:8]
        filename = f"recording_{timestamp}_{file_id}.wav"
        file_path = AUDIO_DIR / filename

        # 保存音频文件
        content = await audio_file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        return JSONResponse({
            "success": True,
            "message": "音频上传成功",
            "filename": filename,
            "file_path": str(file_path),
            "file_size": len(content)
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@router.get("/api/audio-files")
async def list_audio_files():
    """获取所有已上传的音频文件列表"""
    try:
        files = []
        for file in AUDIO_DIR.glob("*.wav"):
            files.append({
                "filename": file.name,
                "path": str(file),
                "size": file.stat().st_size,
                "created_at": datetime.fromtimestamp(file.stat().st_ctime).isoformat()
            })
        return JSONResponse({
            "success": True,
            "files": files
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500) 