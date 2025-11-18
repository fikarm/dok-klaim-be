import pickle
from pathlib import Path
from src.core.settings import settings


# load dari file
def cache_set(name, content):
    cache_path = Path(settings.TEMP_DIR, name)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "wb") as f:
        pickle.dump(content, f)


def cache_get(name):
    cache_path = Path(settings.TEMP_DIR, name)
    if cache_path.exists():
        with open(cache_path, "rb") as f:
            return pickle.load(f)
