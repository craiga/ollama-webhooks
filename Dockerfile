FROM python:3-alpine AS app
ENV PYTHONUNBUFFERED=1

RUN ["apk", "add", "--update", "curl"]
WORKDIR /app
COPY requirements.txt .
RUN ["pip", "install", "--requirement", "requirements.txt", "--no-cache-dir"]
COPY . .

FROM app AS web
EXPOSE 8000
CMD ["bin/web"]

FROM app AS worker
CMD ["bin/worker"]
