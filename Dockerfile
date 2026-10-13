FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY autopilot ./autopilot
RUN pip install --no-cache-dir .
ENTRYPOINT ["python", "-m", "autopilot"]
