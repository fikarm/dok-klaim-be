import pickle
from typing import Any
from pathlib import Path
from src.core.settings import settings


def cache(name, content: Any = None):
    cache_path = Path(settings.TEMP_DIR, f"{name}.pkl")
    print("cache path", cache_path)

    if cache_path.exists():
        print("cache path exists")
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "wb") as f:
        print("cache path create")
        pickle.dump(content, f)
        return content
