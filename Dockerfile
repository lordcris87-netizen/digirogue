FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py index.html game.html loading.html ./
COPY assets ./assets
ENV HOST=0.0.0.0 PORT=8765 DIGIROGUE_DB=/data/ranking.sqlite3 PYTHONUNBUFFERED=1
RUN mkdir -p /data
EXPOSE 8765
CMD ["python","server.py"]
