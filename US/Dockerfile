FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask requests
COPY us.py .
EXPOSE 8080
CMD ["python", "-u", "us.py"]