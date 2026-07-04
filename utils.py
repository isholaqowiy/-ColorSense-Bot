import os

TEMP_DIR = "temp_colors"

def ensure_temp_directory():
    """Guarantees the sandbox directories exist before execution loops start."""
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def clear_user_cache(user_id: int):
    """Safely sweeps up binary image logs bound to a specific user ID."""
    if not os.path.exists(TEMP_DIR):
        return
    for filename in os.listdir(TEMP_DIR):
        if filename.startswith(f"user_{user_id}_"):
            try:
                os.remove(os.path.join(TEMP_DIR, filename))
            except Exception:
                pass

