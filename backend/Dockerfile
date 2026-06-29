FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/usr/local/lib

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    ninja-build \
    ca-certificates \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth=1 https://github.com/open-quantum-safe/liboqs /tmp/liboqs && \
    cmake -S /tmp/liboqs -B /tmp/liboqs/build \
      -GNinja \
      -DBUILD_SHARED_LIBS=ON \
      -DOQS_BUILD_ONLY_LIB=ON \
      -DCMAKE_BUILD_TYPE=Release && \
    cmake --build /tmp/liboqs/build --parallel 2 && \
    cmake --install /tmp/liboqs/build && \
    ldconfig && \
    rm -rf /tmp/liboqs

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir git+https://github.com/open-quantum-safe/liboqs-python.git

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]