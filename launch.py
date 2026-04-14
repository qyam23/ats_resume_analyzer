from __future__ import annotations

import uvicorn

from config.settings import get_settings


def main() -> None:
    settings = get_settings()
    host = "0.0.0.0" if settings.app_env.lower() == "production" else settings.api_host
    uvicorn.run("api.main:app", host=host, port=settings.runtime_port)


if __name__ == "__main__":
    main()
