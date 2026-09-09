.PHONY: install backend frontend test demo clean

install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && . .venv/bin/activate && pytest -v

demo:
	python3 scripts/generate_sample_firmware.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/.pytest_cache
	rm -rf frontend/dist
