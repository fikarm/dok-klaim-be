import uvicorn
from src.core.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "src:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # settings.is_dev(),
        timeout_graceful_shutdown=settings.GRACEFUL_SHUTDOWN_TIMEOUT,
    )
