from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any
import tomllib

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


ENCRYPTED_SECRETS_VERSION = 1
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
KEY_LENGTH = 32
SALT_LENGTH = 16
AES_GCM_NONCE_LENGTH = 12

_unlocked_payload: dict[str, Any] = {}


class SecretsError(Exception):
    pass


def load_openai_api_key(
    legacy_secrets_path: str | Path,
    encrypted_secrets_path: str | Path | None = None,
) -> str:
    env_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key

    if encrypted_secrets_path is not None:
        encrypted_key = _openai_key_from_payload(_unlocked_payload)
        if encrypted_key:
            return encrypted_key

    path = Path(legacy_secrets_path)
    if not path.exists():
        return ""

    data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    return _openai_key_from_legacy_data(data)


def has_unlocked_openai_api_key() -> bool:
    return bool(_openai_key_from_payload(_unlocked_payload))


def clear_unlocked_secrets() -> None:
    _unlocked_payload.clear()


def encrypted_secrets_exists(path: str | Path) -> bool:
    return Path(path).exists()


def unlock_encrypted_secrets(path: str | Path, password: str) -> dict[str, Any]:
    payload = decrypt_secrets_file(path, password)
    _unlocked_payload.clear()
    _unlocked_payload.update(payload)
    return dict(payload)


def encrypt_secrets_file(
    path: str | Path,
    payload: dict[str, Any],
    password: str,
) -> None:
    if not password:
        raise SecretsError("Adminlösenord får inte vara tomt.")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    salt = os.urandom(SALT_LENGTH)
    nonce = os.urandom(AES_GCM_NONCE_LENGTH)
    key = _derive_key(password, salt)
    plaintext = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
    envelope = {
        "version": ENCRYPTED_SECRETS_VERSION,
        "kdf": "scrypt",
        "kdf_parameters": {
            "n": SCRYPT_N,
            "r": SCRYPT_R,
            "p": SCRYPT_P,
            "length": KEY_LENGTH,
        },
        "salt": _b64encode(salt),
        "cipher": "AES-256-GCM",
        "nonce": _b64encode(nonce),
        "ciphertext": _b64encode(ciphertext),
    }
    target.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")


def decrypt_secrets_file(path: str | Path, password: str) -> dict[str, Any]:
    source = Path(path)
    try:
        envelope = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(envelope, dict):
            raise ValueError
        _validate_envelope(envelope)
        salt = _b64decode(str(envelope["salt"]))
        nonce = _b64decode(str(envelope["nonce"]))
        ciphertext = _b64decode(str(envelope["ciphertext"]))
        kdf_parameters = envelope["kdf_parameters"]
        key = _derive_key(
            password,
            salt,
            n=int(kdf_parameters["n"]),
            r=int(kdf_parameters["r"]),
            p=int(kdf_parameters["p"]),
            length=int(kdf_parameters["length"]),
        )
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
        payload = json.loads(plaintext.decode("utf-8"))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, InvalidTag) as error:
        raise SecretsError(
            "Kunde inte låsa upp krypterade secrets. Kontrollera lösenordet och filen."
        ) from error

    if not isinstance(payload, dict):
        raise SecretsError("Krypterade secrets har ogiltigt format.")
    return payload


def read_encrypted_envelope(path: str | Path) -> dict[str, Any]:
    envelope = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(envelope, dict):
        raise SecretsError("Krypterade secrets har ogiltigt format.")
    return envelope


def set_openai_api_key(path: str | Path, password: str, api_key: str) -> None:
    payload = _load_or_empty_payload(path, password)
    providers = payload.setdefault("providers", {})
    if not isinstance(providers, dict):
        providers = {}
        payload["providers"] = providers
    providers["openai"] = {"api_key": api_key.strip()}
    encrypt_secrets_file(path, payload, password)
    _unlocked_payload.clear()
    _unlocked_payload.update(payload)


def remove_openai_api_key(path: str | Path, password: str) -> None:
    payload = _load_or_empty_payload(path, password)
    providers = payload.get("providers", {})
    if isinstance(providers, dict):
        providers.pop("openai", None)
    encrypt_secrets_file(path, payload, password)
    _unlocked_payload.clear()
    _unlocked_payload.update(payload)


def initialize_encrypted_secrets(
    path: str | Path,
    password: str,
    openai_api_key: str = "",
    overwrite: bool = False,
) -> None:
    target = Path(path)
    if target.exists() and not overwrite:
        raise SecretsError("Krypterade secrets finns redan.")
    payload: dict[str, Any] = {"providers": {}}
    if openai_api_key.strip():
        payload["providers"]["openai"] = {"api_key": openai_api_key.strip()}
    encrypt_secrets_file(target, payload, password)
    _unlocked_payload.clear()
    _unlocked_payload.update(payload)


def _load_or_empty_payload(path: str | Path, password: str) -> dict[str, Any]:
    source = Path(path)
    if source.exists():
        return decrypt_secrets_file(source, password)
    return {"providers": {}}


def _derive_key(
    password: str,
    salt: bytes,
    n: int = SCRYPT_N,
    r: int = SCRYPT_R,
    p: int = SCRYPT_P,
    length: int = KEY_LENGTH,
) -> bytes:
    return Scrypt(salt=salt, length=length, n=n, r=r, p=p).derive(
        password.encode("utf-8")
    )


def _validate_envelope(envelope: dict[str, Any]) -> None:
    if envelope.get("version") != ENCRYPTED_SECRETS_VERSION:
        raise ValueError
    if envelope.get("kdf") != "scrypt":
        raise ValueError
    if envelope.get("cipher") != "AES-256-GCM":
        raise ValueError
    if not isinstance(envelope.get("kdf_parameters"), dict):
        raise ValueError
    for field in ("salt", "nonce", "ciphertext"):
        if not isinstance(envelope.get(field), str):
            raise ValueError


def _openai_key_from_payload(payload: dict[str, Any]) -> str:
    providers = payload.get("providers", {})
    if not isinstance(providers, dict):
        return ""
    openai = providers.get("openai", {})
    if not isinstance(openai, dict):
        return ""
    return str(openai.get("api_key", "")).strip()


def _openai_key_from_legacy_data(data: dict[str, Any]) -> str:
    openai_section = data.get("openai", {})
    if not isinstance(openai_section, dict):
        return ""
    return str(openai_section.get("api_key", "")).strip()


def _b64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"), validate=True)
