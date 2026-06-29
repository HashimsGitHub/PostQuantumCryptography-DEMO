import base64
import math
import os
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


app = FastAPI(
    title="Post-Quantum Cryptography Web Demo",
    version="2.0.0",
    description="Alice and Bob demo for RSA, weak RSA break, Harvest Now Decrypt Later, and ML-KEM.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEMO_MESSAGE = "Hello Bob, this confidential message was encrypted by Alice."


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def short_b64(data: bytes, length: int = 88) -> str:
    value = b64(data)
    return value if len(value) <= length else value[:length] + "...truncated..."


def derive_aes_key(shared_secret: bytes, context: bytes) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=context,
    )
    return hkdf.derive(shared_secret)


def aes_roundtrip(message: str, key: bytes) -> Dict[str, Any]:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, message.encode("utf-8"), None)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")

    return {
        "algorithm": "AES-256-GCM",
        "nonce_b64": b64(nonce),
        "ciphertext_b64_preview": short_b64(ciphertext),
        "decrypted_message": plaintext,
        "success": plaintext == message,
    }


def response_template(
    scenario_id: str,
    title: str,
    summary: str,
    steps: List[Dict[str, str]],
    crypto: Dict[str, Any],
    teaching_point: str,
    started: float,
) -> Dict[str, Any]:
    return {
        "id": scenario_id,
        "title": title,
        "status": "success",
        "time_ms": round((time.perf_counter() - started) * 1000, 2),
        "summary": summary,
        "steps": steps,
        "crypto": crypto,
        "teaching_point": teaching_point,
        "disclaimer": (
            "Educational demo only. The weak RSA attack uses deliberately tiny values. "
            "This demo does not break RSA-2048, AES-256, TLS, or production cryptography."
        ),
    }


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/scenarios")
def scenarios() -> Dict[str, Any]:
    return {
        "scenarios": [
            {
                "id": "classical-rsa",
                "title": "Conventional RSA + AES",
                "risk": "Quantum-vulnerable key exchange",
            },
            {
                "id": "weak-rsa-break",
                "title": "Weak RSA Break",
                "risk": "Toy attack principle",
            },
            {
                "id": "harvest-now",
                "title": "Harvest Now, Decrypt Later",
                "risk": "Future quantum risk",
            },
            {
                "id": "pqc-mlkem",
                "title": "Post-Quantum ML-KEM + AES",
                "risk": "Quantum-resistant key establishment",
            },
        ]
    }


@app.get("/api/scenario/classical-rsa")
def classical_rsa_demo() -> Dict[str, Any]:
    started = time.perf_counter()

    bob_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    bob_public_key = bob_private_key.public_key()

    alice_aes_key = os.urandom(32)

    wrapped_aes_key = bob_public_key.encrypt(
        alice_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    bob_aes_key = bob_private_key.decrypt(
        wrapped_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    aes_result = aes_roundtrip(DEMO_MESSAGE, bob_aes_key)

    public_pem = bob_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    return response_template(
        scenario_id="classical-rsa",
        title="Conventional RSA + AES",
        summary="Alice uses AES-256-GCM for the message and RSA-2048-OAEP to wrap the AES key for Bob.",
        steps=[
            {"actor": "Bob", "action": "Generates an RSA-2048 public/private key pair."},
            {"actor": "Alice", "action": "Creates a random AES-256 session key."},
            {"actor": "Alice", "action": "Encrypts the message with AES-256-GCM."},
            {"actor": "Alice", "action": "Wraps the AES key using Bob's RSA public key."},
            {"actor": "Bob", "action": "Uses his RSA private key to recover the AES key and decrypt the message."},
            {"actor": "Eve", "action": "Can capture the public key and ciphertext, but cannot classically break RSA-2048 in this demo."},
        ],
        crypto={
            "key_transport": "RSA-2048-OAEP",
            "data_encryption": aes_result["algorithm"],
            "rsa_public_key_preview": public_pem[:260] + "...",
            "wrapped_aes_key_b64_preview": short_b64(wrapped_aes_key),
            "aes": aes_result,
        },
        teaching_point=(
            "This is a common classical pattern: public-key cryptography protects the session key, "
            "and symmetric cryptography protects the data. The future quantum concern is RSA key transport, "
            "not AES-256-GCM itself."
        ),
        started=started,
    )


def egcd(a: int, b: int):
    if a == 0:
        return b, 0, 1
    g, y, x = egcd(b % a, a)
    return g, x - (b // a) * y, y


def modinv(a: int, m: int) -> int:
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist.")
    return x % m


def factor_small_n(n: int) -> Optional[tuple[int, int]]:
    for candidate in range(2, math.isqrt(n) + 1):
        if n % candidate == 0:
            return candidate, n // candidate
    return None


@app.get("/api/scenario/weak-rsa-break")
def weak_rsa_break_demo() -> Dict[str, Any]:
    started = time.perf_counter()

    p = 3557
    q = 2579
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = modinv(e, phi)

    plaintext_number = 123456
    ciphertext_number = pow(plaintext_number, e, n)

    recovered = factor_small_n(n)
    if recovered is None:
        raise RuntimeError("Could not factor toy RSA modulus.")

    recovered_p, recovered_q = recovered
    recovered_phi = (recovered_p - 1) * (recovered_q - 1)
    recovered_d = modinv(e, recovered_phi)
    recovered_plaintext = pow(ciphertext_number, recovered_d, n)

    return response_template(
        scenario_id="weak-rsa-break",
        title="Weak RSA Break",
        summary="Eve factors a deliberately tiny RSA modulus and reconstructs Bob's private key.",
        steps=[
            {"actor": "Bob", "action": "Publishes a toy RSA public key with a very small modulus n."},
            {"actor": "Alice", "action": "Encrypts a demo number using Bob's weak public key."},
            {"actor": "Eve", "action": "Factors n into p and q."},
            {"actor": "Eve", "action": "Calculates phi(n), reconstructs d, and decrypts the ciphertext."},
            {"actor": "Result", "action": "The original plaintext is recovered."},
        ],
        crypto={
            "warning": "Toy RSA only. These values are intentionally tiny for a live educational demo.",
            "public_key": {"n": n, "e": e},
            "original_private_values": {"p": p, "q": q, "d": d},
            "ciphertext_number": ciphertext_number,
            "attacker_recovered": {
                "p": recovered_p,
                "q": recovered_q,
                "phi": recovered_phi,
                "d": recovered_d,
                "decrypted_number": recovered_plaintext,
            },
            "success": recovered_plaintext == plaintext_number,
        },
        teaching_point=(
            "RSA security depends on the difficulty of factoring n. This toy example is easy to factor. "
            "A sufficiently powerful future quantum computer running Shor's algorithm threatens this assumption "
            "for real RSA sizes."
        ),
        started=started,
    )


@app.get("/api/scenario/harvest-now")
def harvest_now_demo() -> Dict[str, Any]:
    started = time.perf_counter()

    captured_record = {
        "year_2026": "Eve captures encrypted traffic today.",
        "contains": [
            "Bob's RSA public key",
            "RSA-wrapped AES session key",
            "AES-GCM ciphertext",
        ],
        "cannot_decrypt_today": True,
    }

    future_risk = {
        "future_capability": "Large-scale cryptographically relevant quantum computer",
        "attack": "Recover RSA private key or session key material from vulnerable public-key exchange",
        "impact": "Old captured encrypted data may become readable later if it still has intelligence value.",
    }

    return response_template(
        scenario_id="harvest-now",
        title="Harvest Now, Decrypt Later",
        summary="Eve records encrypted traffic today and waits for future quantum capability.",
        steps=[
            {"actor": "Alice", "action": "Sends encrypted data using a classical public-key mechanism."},
            {"actor": "Eve", "action": "Stores the traffic even though she cannot decrypt it today."},
            {"actor": "Future Eve", "action": "Uses future quantum capability against the vulnerable key exchange."},
            {"actor": "Enterprise lesson", "action": "Long-lived secrets should migrate early to quantum-safe key establishment."},
        ],
        crypto={
            "captured_record": captured_record,
            "future_risk": future_risk,
            "mitigation": [
                "Inventory cryptography",
                "Prioritise long-lived sensitive data",
                "Adopt crypto-agility",
                "Replace RSA/DH/ECDH key exchange with ML-KEM or hybrid PQC approaches",
                "Keep AES-256 and SHA-384/SHA-512 where appropriate",
            ],
        },
        teaching_point=(
            "The threat is not only decryption today. Sensitive traffic can be harvested now and decrypted later "
            "when quantum capability matures. That is why migration planning matters before the crisis arrives."
        ),
        started=started,
    )


def get_mlkem_algorithm() -> str:
    import oqs

    enabled = oqs.get_enabled_kem_mechanisms()
    preferred = ["ML-KEM-768", "Kyber768", "ML-KEM-512", "Kyber512"]

    for candidate in preferred:
        if candidate in enabled:
            return candidate

    raise RuntimeError(
        "No ML-KEM/Kyber mechanism found. Enabled examples: "
        + ", ".join(enabled[:20])
    )


@app.get("/api/scenario/pqc-mlkem")
def pqc_mlkem_demo() -> Dict[str, Any]:
    started = time.perf_counter()

    import oqs

    kem_algorithm = get_mlkem_algorithm()

    with oqs.KeyEncapsulation(kem_algorithm) as bob_kem:
        bob_public_key = bob_kem.generate_keypair()

        with oqs.KeyEncapsulation(kem_algorithm) as alice_kem:
            kem_ciphertext, alice_shared_secret = alice_kem.encap_secret(bob_public_key)

        bob_shared_secret = bob_kem.decap_secret(kem_ciphertext)

    shared_secret_match = alice_shared_secret == bob_shared_secret

    aes_key = derive_aes_key(
        bob_shared_secret,
        b"pqc-demo-mlkem-aes-key",
    )

    aes_result = aes_roundtrip(DEMO_MESSAGE, aes_key)

    return response_template(
        scenario_id="pqc-mlkem",
        title="Post-Quantum ML-KEM + AES",
        summary="Alice and Bob use ML-KEM to establish a shared secret, then use AES-256-GCM for the message.",
        steps=[
            {"actor": "Bob", "action": "Generates an ML-KEM public/private key pair."},
            {"actor": "Alice", "action": "Uses Bob's ML-KEM public key to encapsulate a shared secret."},
            {"actor": "Bob", "action": "Decapsulates Alice's KEM ciphertext and derives the same shared secret."},
            {"actor": "Alice and Bob", "action": "Derive an AES-256 key from the shared secret."},
            {"actor": "Eve", "action": "Can see the public key and KEM ciphertext, but there is no RSA modulus to factor."},
        ],
        crypto={
            "kem_algorithm": kem_algorithm,
            "purpose": "Post-quantum key establishment",
            "data_encryption": aes_result["algorithm"],
            "bob_public_key_b64_preview": short_b64(bob_public_key),
            "kem_ciphertext_b64_preview": short_b64(kem_ciphertext),
            "alice_shared_secret_b64_preview": short_b64(alice_shared_secret, 52),
            "bob_shared_secret_b64_preview": short_b64(bob_shared_secret, 52),
            "shared_secret_match": shared_secret_match,
            "aes": aes_result,
        },
        teaching_point=(
            "PQC normally does not replace AES for bulk data encryption. It replaces vulnerable public-key "
            "key establishment. ML-KEM gives Alice and Bob a shared secret that can be used to derive an AES key."
        ),
        started=started,
    )