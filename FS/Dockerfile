FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask
COPY fs.py .
EXPOSE 9090
CMD ["python", "-u", "fs.py"]