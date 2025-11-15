FROM python:3.13.0rc2-bookworm AS auth_ser

WORKDIR /app

# Install system dependencies with caching
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y  build-essential curl git libssl-dev pkg-config rustc && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    rm -rf /var/lib/apt/lists/*

# Update PATH for Rust
ENV PATH="/root/.cargo/bin:${PATH}"


COPY requirements.txt main.py /app/

RUN pip install --upgrade pip && \
    pip install --only-binary=:all: -r requirements.txt

ENTRYPOINT ["python", "main.py"]

