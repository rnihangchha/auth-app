FROM python:3.13-alpine AS auth_ser

WORKDIR /app

# Install system dependencies
RUN apk update && apk upgrade && \
    apk add --no-cache \
        build-base \
        cargo \
        curl \
        git \
        openssl-dev \
        pkgconfig 
        

# Note: Alpine has rust/cargo in repositories, no need for rustup

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY main.py .

RUN adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser
EXPOSE 3002
ENTRYPOINT ["python", "main.py"]