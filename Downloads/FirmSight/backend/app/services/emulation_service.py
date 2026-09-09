from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.firmware import Firmware
from app.models.emulation import EmulationSession
from app.emulation.qemu_manager import launch_emulation, stop_emulation, is_emulation_running
from app.emulation.demo_emulation import generate_demo_boot_log
from app.services.firmware_service import get_firmware_path


def start_emulation_session(db: Session, firmware: Firmware, force_demo: bool = False) -> EmulationSession:
    session = EmulationSession(firmware_id=firmware.id, status="starting")
    db.add(session)
    db.flush()

    if force_demo or firmware.architecture == "unknown":
        session.mode = "demo"
        session.status = "running"
        session.is_demo = True
        session.process_id = 0
        session.output_log = generate_demo_boot_log()
        db.commit()
        db.refresh(session)
        return session

    firmware_path = get_firmware_path(firmware)
    launch_result = launch_emulation(session.id, firmware.architecture, firmware_path)

    session.mode = launch_result.mode
    session.qemu_binary = launch_result.qemu_binary
    session.is_demo = launch_result.is_demo

    if launch_result.success:
        session.status = "running"
        session.process_id = launch_result.process_id
        session.output_log = launch_result.message
    else:
        session.status = "running"
        session.mode = "demo"
        session.is_demo = True
        session.output_log = f"{launch_result.message}\n\n{generate_demo_boot_log()}"

    db.commit()
    db.refresh(session)
    return session


def stop_emulation_session(db: Session, session: EmulationSession) -> EmulationSession:
    if not session.is_demo:
        stop_emulation(session.id)
    session.status = "stopped"
    session.stopped_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


def get_latest_emulation(db: Session, firmware_id: str):
    return (
        db.query(EmulationSession)
        .filter(EmulationSession.firmware_id == firmware_id)
        .order_by(EmulationSession.started_at.desc())
        .first()
    )


def refresh_emulation_status(db: Session, session: EmulationSession) -> EmulationSession:
    if session.status == "running" and not session.is_demo:
        if not is_emulation_running(session.id):
            session.status = "stopped"
            session.stopped_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
    return session
