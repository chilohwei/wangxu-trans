# 使用官方Python镜像作为基础镜像
FROM python:3.8-slim

# 设置工作目录为/app
WORKDIR /app

# 将当前目录下的文件复制到容器的/app目录下
COPY . /app

# 使用pip安装requirements.txt中列出的依赖
RUN pip install --no-cache-dir -r requirements.txt

# 让容器的8501端口可用于外部
EXPOSE 8501

# 运行Streamlit应用
CMD ["streamlit", "run", "trans.py", "--server.port=8501", "--server.address=0.0.0.0"]