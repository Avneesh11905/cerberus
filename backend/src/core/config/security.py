from pathlib import Path

from pydantic import model_validator
from pydantic_settings import SettingsConfigDict

from .base import _BaseSettings


class SecuritySettings(_BaseSettings):
    SESSION_SECRET: str
    ENCRYPTION_KEY: str
    JWT_PRIVATE_KEY: str = ""
    JWT_PUBLIC_KEY: str = ""
    JWT_PRIVATE_KEY_PATH: str = ""
    JWT_PUBLIC_KEY_PATH: str = ""

    @model_validator(mode="after")
    def load_keys(self) -> "SecuritySettings":
        base_dir = Path(__file__).resolve().parent.parent.parent.parent

        if self.JWT_PRIVATE_KEY_PATH:
            private_path = Path(self.JWT_PRIVATE_KEY_PATH)
            if not private_path.is_absolute():
                private_path = base_dir / private_path.as_posix().lstrip("/")
            try:
                self.JWT_PRIVATE_KEY = private_path.read_text(encoding="utf-8")
            except FileNotFoundError:
                raise ValueError(
                    f"JWT_PRIVATE_KEY_PATH specified but file not found at {private_path}"
                )

        if self.JWT_PUBLIC_KEY_PATH:
            public_path = Path(self.JWT_PUBLIC_KEY_PATH)
            if not public_path.is_absolute():
                public_path = base_dir / public_path.as_posix().lstrip("/")
            try:
                self.JWT_PUBLIC_KEY = public_path.read_text(encoding="utf-8")
            except FileNotFoundError:
                raise ValueError(
                    f"JWT_PUBLIC_KEY_PATH specified but file not found at {public_path}"
                )

        if not self.JWT_PRIVATE_KEY:
            try:
                self.JWT_PRIVATE_KEY = (
                    base_dir / "keys" / "jwt_private.pem"
                ).read_text(encoding="utf-8")
            except FileNotFoundError:
                raise ValueError(
                    "JWT_PRIVATE_KEY or JWT_PRIVATE_KEY_PATH must be provided."
                )
        if not self.JWT_PUBLIC_KEY:
            try:
                self.JWT_PUBLIC_KEY = (base_dir / "keys" / "jwt_public.pem").read_text(
                    encoding="utf-8"
                )
            except FileNotFoundError:
                raise ValueError(
                    "JWT_PUBLIC_KEY or JWT_PUBLIC_KEY_PATH must be provided."
                )

        return self


class TurnstileSettings(_BaseSettings):
    SECRET_KEY: str = ""

    model_config = SettingsConfigDict(
        **(_BaseSettings.model_config | {"env_prefix": "TURNSTILE_"})
    )
