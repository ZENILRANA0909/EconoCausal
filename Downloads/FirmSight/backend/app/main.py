from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from app.upload import save_firmware


app = FastAPI(
    title="FirmSight",
    description="IoT Firmware Security Analysis Platform",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "FirmSight",
        "version": "1.0.0",
        "status": "running",
        "message": "FirmSight backend is running",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "FirmSight API",
    }


@app.get("/api/system/info")
def system_info():
    return {
        "application": "FirmSight",
        "version": "1.0.0",
        "environment": "development",
        "status": "online",
    }


@app.post("/api/firmware/upload")
async def upload_firmware(
    file: UploadFile = File(...)
):
    result = await save_firmware(file)

    return {
        "success": True,
        "message": "Firmware uploaded successfully",
        "firmware": result,
    }
