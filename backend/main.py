import uvicorn
from dotenv import load_dotenv

load_dotenv(".env.local")
from src.core.config import get_settings  # noqa: E402


def main():
    uvicorn.run(
        "src:app",
        host="0.0.0.0",
        port=8000,
        reload=(get_settings().core.ENV == "development"),
        env_file=".env.local",
    )


if __name__ == "__main__":
    main()
