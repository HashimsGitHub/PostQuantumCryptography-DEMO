# Post-Quantum Cryptography Web Demo

A user-friendly Alice and Bob web demo showing:

1. Conventional RSA + AES encryption
2. Weak RSA break using toy RSA
3. Post-Quantum ML-KEM + AES encryption

## Important Disclaimer

This project is for education and demonstration only.

The weak RSA scenario uses deliberately tiny toy RSA parameters so that factoring can complete instantly. It does not break RSA-2048 or production cryptography.

## Architecture

- React frontend
- FastAPI backend
- Docker Compose
- Python cryptography library
- Open Quantum Safe liboqs / liboqs-python for ML-KEM

## Run Locally

```bash
docker compose up --build -d