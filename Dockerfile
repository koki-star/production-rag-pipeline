FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
COPY src ./src
COPY docs ./docs
COPY tests ./tests
COPY ai_prompt_log.md ./

RUN uv sync

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "src/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
