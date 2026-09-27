# Post-Quantum Cryptography Web Demo

An interactive, Docker-based demonstration of **Conventional Cryptography vs Post-Quantum Cryptography (PQC)**.

The application visualizes how encrypted communication works between **Alice**, **Bob**, and an attacker (**Eve**), while executing real cryptographic operations through a FastAPI backend. It is designed for engineers, students, security professionals, and technical presentations.

---

## Features

- 🔐 Conventional RSA + AES hybrid encryption
- ⚠️ Weak RSA attack using educational toy parameters
- 🛡️ Post-Quantum ML-KEM + AES key establishment
- 🎬 Interactive Matrix-style visualization
- 💻 Live terminal view showing cryptographic operations
- 📊 Live backend execution (not a prerecorded animation)
- ⚡ FastAPI REST backend
- ⚛️ React frontend
- 🐳 Docker Compose deployment
- 🔬 Built using Open Quantum Safe (liboqs)

---

# Demonstration Scenarios

The demo includes four interactive scenarios:

1. **Conventional RSA + AES**
   - Hybrid encryption
   - RSA protects the AES session key
   - Demonstrates current enterprise encryption

2. **Weak RSA Break**
   - Educational toy RSA example
   - Demonstrates why factoring breaks RSA
   - Does **NOT** attack RSA-2048

3. **Harvest Now, Decrypt Later**
   - Explains why attackers capture encrypted traffic today
   - Demonstrates long-term quantum risk

4. **Post-Quantum ML-KEM + AES**
   - Uses Open Quantum Safe
   - Demonstrates quantum-resistant key establishment
   - Shows why PQC replaces RSA for key exchange

---

# Live Video Demo

Click the screenshot below to watch the complete demonstration.

[![Watch Demo](https://github.com/user-attachments/assets/82a6a63c-64b4-4462-be67-4c503b36482c)](https://smbclouddrive.blob.core.windows.net/sitecontent/PQC-Demo.mp4)


---

# Architecture

```
                    +----------------------+
                    |      React UI        |
                    |  Matrix Dashboard    |
                    +----------+-----------+
                               |
                         REST API
                               |
                    +----------v-----------+
                    |     FastAPI          |
                    |  Cryptographic API   |
                    +----------+-----------+
                               |
          +--------------------+--------------------+
          |                    |                    |
     RSA + AES            Toy RSA             ML-KEM
   cryptography        Demonstration      Open Quantum Safe
                                              (liboqs)
```

---

# Technology Stack

| Component | Technology |
|----------|------------|
| Frontend | React + Vite |
| Backend | FastAPI |
| Cryptography | Python cryptography |
| Post-Quantum | Open Quantum Safe (liboqs) |
| Container | Docker Compose |
| UI Theme | Matrix-inspired |

---

# Live Demo

Open your browser

```
https://post-quantum-cryptography-demo.vercel.app/
```

---

# Educational Objectives

This project demonstrates:

- Hybrid encryption
- Public-key cryptography
- AES session encryption
- RSA key exchange
- Why RSA is vulnerable to quantum computers
- Harvest Now, Decrypt Later attacks
- ML-KEM (Module-Lattice Key Encapsulation Mechanism)
- Post-Quantum Cryptography migration concepts

---

# Important Disclaimer

This project is intended for **education, demonstrations, workshops and technical presentations**.

The **Weak RSA Break** scenario intentionally uses very small RSA parameters so that factoring completes instantly. It **does not** break RSA-2048 or any production cryptographic system.

This project should **not** be used as a production cryptographic implementation.

---

# References

- NIST Post-Quantum Cryptography Standardization
- Open Quantum Safe (liboqs)
- ML-KEM (formerly CRYSTALS-Kyber)
- Python cryptography library

---

# License

This project is released for educational purposes.

Contributions, improvements and suggestions are welcome.
## Test locally before deploying to Vercel

From the repository root, with Docker Desktop (or Docker Engine with Compose) running:

```bash
docker compose up --build
```

Open http://localhost/ and exercise all four scenarios in the UI. Verify the API:

```bash
curl -f http://localhost/api/health
curl -f http://localhost/api/scenarios
curl -f http://localhost/api/scenario/pqc-mlkem
```

The first build compiles liboqs and downloads its Python bindings, so it can take several minutes. Stop with `docker compose down`. This Compose setup tests the same app and cryptographic backend. To build the exact Vercel container images separately:

```bash
docker build -f backend/Dockerfile.vercel -t pqc-vercel-backend backend
docker build -f frontend/Dockerfile.vercel -t pqc-vercel-frontend frontend
```

The Vercel images can be tested with `docker run --rm -p 8000:80 pqc-vercel-backend` and, in another terminal, `docker run --rm -p 8080:80 pqc-vercel-frontend`. The frontend container alone cannot route `/api` locally: Docker Compose provides that proxy locally, while `vercel.json` provides it on Vercel.

After local testing, push the changes to a branch and import the repository in Vercel with the **repository root** as the project root. `vercel.json` defines the two services and same-origin `/api` routing. Container images on Vercel are currently a beta feature; consult Vercel's container image limits before deployment.
