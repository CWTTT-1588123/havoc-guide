FROM python:3.12-slim
WORKDIR /app

# 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用 + 前端 + 关键数据（大体积原始 records.jsonl 不打包，运行时用不到）
COPY webapp.py .
COPY static ./static
COPY processed/stats.json processed/augment_icons.json processed/augment_names.json \
     processed/champion_names.json processed/item_names.json processed/champion_tags.json \
     processed/users.json ./processed/

# 可选环境变量（.env 会注入）
COPY .env.example .env
ENV PATCH_VERSION=16.16
ENV DRAGON_VER=16.17.1

EXPOSE 8000
CMD ["uvicorn", "webapp:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
