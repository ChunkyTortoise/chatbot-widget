.PHONY: widget test lint format typecheck

widget:
	@echo "Building chatbot widget..."
	@mkdir -p widget/dist
	@npx terser widget/src/chatbot.js -o widget/dist/chatbot.min.js \
		--compress --mangle --source-map "url='chatbot.min.js.map'" \
		|| (echo "terser not found, copying unminified..." && cp widget/src/chatbot.js widget/dist/chatbot.min.js)
	@echo "Widget built: widget/dist/chatbot.min.js"

test:
	pytest tests/ -q --tb=short

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .

typecheck:
	mypy
