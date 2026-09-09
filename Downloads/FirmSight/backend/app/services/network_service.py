from sqlalchemy.orm import Session
from app.models.firmware import Firmware
from app.models.network import NetworkEvent
from app.networking.demo_network import generate_demo_network_events


def generate_network_events_for_firmware(db: Session, firmware: Firmware):
    db.query(NetworkEvent).filter(NetworkEvent.firmware_id == firmware.id).delete()

    simulated_events = generate_demo_network_events()
    stored_events = []
    for item in simulated_events:
        event = NetworkEvent(
            firmware_id=firmware.id,
            source_ip=item["source_ip"],
            destination_ip=item["destination_ip"],
            source_port=item["source_port"],
            destination_port=item["destination_port"],
            protocol=item["protocol"],
            is_dns=item["is_dns"],
            dns_query=item["dns_query"],
            http_destination=item["http_destination"],
            is_simulated=True,
        )
        db.add(event)
        stored_events.append(event)

    db.commit()
    for event in stored_events:
        db.refresh(event)
    return stored_events


def get_network_events(db: Session, firmware_id: str):
    return (
        db.query(NetworkEvent)
        .filter(NetworkEvent.firmware_id == firmware_id)
        .order_by(NetworkEvent.captured_at.desc())
        .all()
    )
