FROM python:3.12-slim

WORKDIR /service
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir flask==3.0.3

COPY . .

EXPOSE 5001
CMD ["python", "app.py"]
