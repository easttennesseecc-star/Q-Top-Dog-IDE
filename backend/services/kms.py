"""
KMS signer interface scaffold with optional cloud providers.

Providers:
- local (default): LocalEd25519 signer using services.attestation.
- aws: AWS KMS asymmetric sign (if boto3 available) or simulated fallback.
- gcp: Google Cloud KMS asymmetric sign (if google-cloud-kms available) or fallback.
- azure: Azure Key Vault Keys sign (if azure packages available) or fallback.

Env configuration examples:
- KMS_PROVIDER=aws | gcp | azure | local
- AWS_KMS_KEY_ID=arn:aws:kms:...:key/...
- GCP_KMS_RESOURCE=projects/.../locations/.../keyRings/.../cryptoKeys/.../cryptoKeyVersions/1
- AZURE_KEYVAULT_URL=https://<vault>.vault.azure.net/ ; AZURE_KEY_ID or KEY_NAME/KEY_VERSION
"""
from __future__ import annotations
import os
from typing import Tuple, Protocol

class Signer(Protocol):
    def keypair(self) -> Tuple[str, str]:
        ...
    def sign(self, artifact: dict) -> Tuple[str, str]:
        """Returns (signature_b64, public_key_b64)."""
        ...


class LocalEd25519Signer:
    def __init__(self) -> None:
        from .attestation import get_env_signing_keypair, generate_keypair
        kp = get_env_signing_keypair()
        if kp:
            self._sk, self._pk = kp
        else:
            self._sk, self._pk = generate_keypair()

    def keypair(self) -> Tuple[str, str]:
        return self._sk, self._pk

    def sign(self, artifact: dict) -> Tuple[str, str]:
        from .attestation import sign_artifact
        return sign_artifact(artifact, self._sk)


def get_signer() -> Signer:
    provider = os.getenv("KMS_PROVIDER", "local").lower()
    if provider in ("local", "local_ed25519"):
        return LocalEd25519Signer()
    if provider == "aws":
        try:
            import boto3  # type: ignore
            class AWSKmsSigner:
                def __init__(self):
                    self.key_id = os.getenv("AWS_KMS_KEY_ID", "")
                    self.client = boto3.client("kms")
                def keypair(self):
                    return (self.key_id, "")
                def sign(self, artifact: dict):
                    import json
                    import base64
                    import hashlib
                    payload = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    # AWS KMS Sign requires a message digest for many key types
                    digest = hashlib.sha256(payload).digest()
                    resp = self.client.sign(
                        KeyId=self.key_id,
                        Message=digest,
                        MessageType="DIGEST",
                        SigningAlgorithm=os.getenv("AWS_KMS_SIGN_ALG", "RSASSA_PSS_SHA_256"),
                    )
                    sig_b64 = base64.b64encode(resp["Signature"]).decode("ascii")
                    # Public key retrieval optional; return empty if not fetched
                    return (sig_b64, "")
            return AWSKmsSigner()
        except Exception:
            # Simulated fallback: HMAC-like using AWS_KMS_SIM_SECRET
            class AwsSimSigner:
                def __init__(self):
                    self.secret = os.getenv("AWS_KMS_SIM_SECRET", "aws-sim-secret")
                def keypair(self):
                    return (self.secret, "")
                def sign(self, artifact: dict):
                    import json
                    import hashlib
                    import base64
                    payload = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    sig = hashlib.sha256(self.secret.encode("utf-8") + payload).digest()
                    return (base64.b64encode(sig).decode("ascii"), "")
            return AwsSimSigner()
    if provider == "gcp":
        try:
            from google.cloud import kms  # type: ignore
            class GcpKmsSigner:
                def __init__(self):
                    self.resource = os.getenv("GCP_KMS_RESOURCE", "")
                    self.client = kms.KeyManagementServiceClient()
                def keypair(self):
                    return (self.resource, "")
                def sign(self, artifact: dict):
                    import json
                    import base64
                    import hashlib
                    payload = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    digest = hashlib.sha256(payload).digest()
                    from google.cloud.kms_v1 import Digest  # type: ignore
                    resp = self.client.asymmetric_sign(request={"name": self.resource, "digest": Digest(sha256=digest)})
                    sig_b64 = base64.b64encode(resp.signature).decode("ascii")
                    return (sig_b64, "")
            return GcpKmsSigner()
        except Exception:
            class GcpSimSigner:
                def __init__(self):
                    self.secret = os.getenv("GCP_KMS_SIM_SECRET", "gcp-sim-secret")
                def keypair(self):
                    return (self.secret, "")
                def sign(self, artifact: dict):
                    import json
                    import hashlib
                    import base64
                    payload = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    sig = hashlib.sha256(self.secret.encode("utf-8") + payload).digest()
                    return (base64.b64encode(sig).decode("ascii"), "")
            return GcpSimSigner()
    if provider == "azure":
        try:
            from azure.identity import DefaultAzureCredential  # type: ignore
            from azure.keyvault.keys.crypto import CryptographyClient, SignatureAlgorithm  # type: ignore
            from azure.keyvault.keys import KeyClient  # type: ignore
            class AzureKmsSigner:
                def __init__(self):
                    vault_url = os.getenv("AZURE_KEYVAULT_URL", "")
                    key_id = os.getenv("AZURE_KEY_ID", "")
                    cred = DefaultAzureCredential()
                    if key_id:
                        self.crypto = CryptographyClient(key_id, cred)
                    else:
                        key_name = os.getenv("AZURE_KEY_NAME", "")
                        key_version = os.getenv("AZURE_KEY_VERSION", None)
                        kc = KeyClient(vault_url=vault_url, credential=cred)
                        key = kc.get_key(key_name, version=key_version)
                        self.crypto = CryptographyClient(key, cred)
                def keypair(self):
                    return ("azure-key", "")
                def sign(self, artifact: dict):
                    import json
                    import base64
                    import hashlib
                    payload = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    digest = hashlib.sha256(payload).digest()
                    resp = self.crypto.sign(SignatureAlgorithm.rs_pss_sha_256, digest)
                    return (base64.b64encode(resp.signature).decode("ascii"), "")
            return AzureKmsSigner()
        except Exception:
            class AzureSimSigner:
                def __init__(self):
                    self.secret = os.getenv("AZURE_KMS_SIM_SECRET", "azure-sim-secret")
                def keypair(self):
                    return (self.secret, "")
                def sign(self, artifact: dict):
                    import json
                    import hashlib
                    import base64
                    payload = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    sig = hashlib.sha256(self.secret.encode("utf-8") + payload).digest()
                    return (base64.b64encode(sig).decode("ascii"), "")
            return AzureSimSigner()
    # Fallback
    return LocalEd25519Signer()
