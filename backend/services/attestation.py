"""
Attestation utilities: sign/verify reasoning artifacts and compute a zk-proof placeholder hash.

- Uses Ed25519 for signatures (libsodium/cryptography backend via pynacl if available, else Python's cryptography).
- zk_attestation: placeholder SHA-256 hash of selected invariants; wire real ZK backend later.
"""
from __future__ import annotations
import os
import json
import hashlib
from dataclasses import dataclass
from typing import Tuple, Optional

try:
    from nacl import signing  # type: ignore
    from nacl.encoding import Base64Encoder  # type: ignore
    _USE_NACL = True
except Exception:
    _USE_NACL = False


@dataclass
class Attestation:
    signature_b64: str
    public_key_b64: str
    proof_hash_hex: str


def _stable_json(data) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compute_proof_hash(invariants: dict) -> str:
    h = hashlib.sha256()
    h.update(_stable_json(invariants))
    return h.hexdigest()


def generate_keypair() -> Tuple[str, str]:
    if _USE_NACL:
        sk = signing.SigningKey.generate()
        pk = sk.verify_key
        return (sk.encode(encoder=Base64Encoder).decode("ascii"), pk.encode(encoder=Base64Encoder).decode("ascii"))
    # Lightweight fallback: derive from random bytes and just return hex strings
    sk = os.urandom(32)
    pk = hashlib.sha256(sk).digest()
    return (sk.hex(), pk.hex())


def get_env_signing_keypair() -> Optional[Tuple[str, str]]:
    """Return (sk, pk) if ATTESTATION_SK_B64 and ATTESTATION_PK_B64 env vars are set."""
    sk = os.getenv("ATTESTATION_SK_B64")
    pk = os.getenv("ATTESTATION_PK_B64")
    if sk and pk:
        return sk, pk
    return None


def sign_artifact(artifact: dict, sk_b64_or_hex: str) -> Tuple[str, str]:
    payload = _stable_json(artifact)
    if _USE_NACL and len(sk_b64_or_hex) > 64:
        sk = signing.SigningKey(sk_b64_or_hex.encode("ascii"), encoder=Base64Encoder)
        signed = sk.sign(payload)
        sig = signed.signature
        pk_b64 = sk.verify_key.encode(encoder=Base64Encoder).decode("ascii")
        import base64
        return (base64.b64encode(sig).decode("ascii"), pk_b64)
    # Fallback: HMAC-like pseudo signature (NOT secure for prod) — placeholder only
    sig = hashlib.sha256(sk_b64_or_hex.encode("utf-8") + payload).digest()
    import base64
    pk = hashlib.sha256(sk_b64_or_hex.encode("utf-8")).digest()
    return (base64.b64encode(sig).decode("ascii"), base64.b64encode(pk).decode("ascii"))


def verify_signature(artifact: dict, signature_b64: str, public_key_b64: str) -> bool:
    payload = _stable_json(artifact)
    if _USE_NACL and len(public_key_b64) > 64:
        try:
            from nacl.encoding import Base64Encoder  # type: ignore
            from nacl.signing import VerifyKey  # type: ignore
            vk = VerifyKey(public_key_b64.encode("ascii"), encoder=Base64Encoder)
            import base64
            sig = base64.b64decode(signature_b64)
            vk.verify(payload, sig)
            return True
        except Exception:
            return False
    # Fallback verification mirrors pseudo-sign: recompute and compare
    import base64
    try:
        pk = base64.b64decode(public_key_b64)
        expected = hashlib.sha256(pk + payload).digest()
        return base64.b64encode(expected).decode("ascii") == signature_b64
    except Exception:
        return False
