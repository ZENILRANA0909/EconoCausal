DEMO_BOOT_LOG = """[DEMO MODE] Simulated boot sequence
[    0.000000] Booting simulated kernel (DEMO / SIMULATED)
[    0.412000] Initializing simulated network interface eth0
[    0.812000] Starting simulated services: httpd, telnetd
[    1.203000] Simulated device ready
[DEMO MODE] No real hardware or QEMU system emulation was executed
"""


def generate_demo_boot_log() -> str:
    return DEMO_BOOT_LOG
