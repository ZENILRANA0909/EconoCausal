Placeholder for demo_router_firmware.bin

This directory holds a small synthetic sample firmware image used for
DEMO / SIMULATED analysis in FirmSight. It intentionally contains no real
vendor firmware and no functioning executable code — it exists purely to
demonstrate the upload -> extract -> analyze -> emulate -> report workflow.

Generate it locally with:

    python3 scripts/generate_sample_firmware.py

This produces samples/demo_router_firmware.bin (~4KB) that can be uploaded
through the Firmware Upload page.
