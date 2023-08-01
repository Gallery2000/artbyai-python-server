# 构建阶段
# 设置基础镜像
FROM python:3.9 AS builder

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 运行阶段
# 设置基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 从构建阶段复制已安装的项目依赖
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# 复制项目文件到工作目录
COPY . /app

RUN pip install gunicorn

EXPOSE 5000

# 启动应用程序
CMD ["gunicorn", "handlers:app", "-b", "0.0.0.0:5000"]
