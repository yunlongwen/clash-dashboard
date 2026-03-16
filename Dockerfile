FROM python:3.11-slim

WORKDIR /app

# 安装依赖
RUN pip3 install flask requests pyyaml

# 复制文件
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY scripts/ /app/scripts/

# 暴露端口
EXPOSE 80 9090

# 启动服务
CMD ["python3", "/app/backend/api_server.py"]
