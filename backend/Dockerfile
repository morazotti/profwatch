FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
RUN uv sync
RUN pip install "fastapi[standard]"
RUN apt-get update && apt-get install -y \
    chromium-driver chromium \
    && rm -rf /var/lib/apt/lists/*


COPY . .

EXPOSE 8000

CMD ["uv", "run", "fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]

