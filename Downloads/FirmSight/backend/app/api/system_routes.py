from datetime import datetime
from fastapi import APIRouter
from app.config.settings import settings
from app.schemas.system import HealthResponse, SystemInfoResponse, ToolStatusResponse
from app.utils.tool_detection import detect_all_tools, get_platform_info

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.utcnow(),
    )


@router.get("/system-info", response_model=SystemInfoResponse)
def system_info():
    platform_info = get_platform_info()
    tools = detect_all_tools()
    core_tools_available = all(
        tools[name].available for name in ("binwalk", "tcpdump") if name in tools
    )
    return SystemInfoResponse(
        system=platform_info["system"],
        release=platform_info["release"],
        machine=platform_info["machine"],
        python_version=platform_info["python_version"],
        demo_mode_recommended=not core_tools_available,
    )


@router.get("/tools", response_model=list[ToolStatusResponse])
def tool_status():
    tools = detect_all_tools()
    return [
        ToolStatusResponse(
            name=status.name,
            available=status.available,
            path=status.path,
            install_hint=status.install_hint,
        )
        for status in tools.values()
    ]
