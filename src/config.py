import shutil
import yaml
from pathlib import Path

# Чтение конфига. Если config.yaml ещё нет — копируем из config.yaml.example.
_cfg_dir = Path(__file__).parent.parent / "config"
config_path = _cfg_dir / "config.yaml"
_example_path = _cfg_dir / "config.yaml.example"

if not config_path.exists() and _example_path.exists():
    shutil.copy(_example_path, config_path)
    print(f"[config] создан {config_path.name} из шаблона — запусти menu.py и настрой")

with open(config_path, "r", encoding="utf-8") as f:
    _config = yaml.safe_load(f)

# 邮箱конфиг
EMAIL_WORKER_URL = _config["email"]["worker_url"]
EMAIL_DOMAIN = _config["email"]["domain"]
EMAIL_PREFIX_LENGTH = _config["email"]["prefix_length"]
EMAIL_WAIT_TIMEOUT = _config["email"]["wait_timeout"]
EMAIL_POLL_INTERVAL = _config["email"]["poll_interval"]
EMAIL_ADMIN_PASSWORD = _config["email"].get("admin_password", "")

# браузерконфиг
HEADLESS = _config["browser"]["headless"]
SLOW_MO = _config["browser"]["slow_mo"]

# Регионконфиг
REGION_CURRENT = _config["region"]["current"]
DEVICE_TYPE = _config["region"].get("device_type", "desktop")
REGION_USE_PROXY = _config["region"].get("use_proxy", False)
REGION_PROXY_MODE = _config["region"].get("proxy_mode", "static")
REGION_PROXY_URL = _config["region"].get("proxy_url", "")
REGION_PROXY_API = _config["region"].get("proxy_api", {})
REGION_PROFILES = _config["region"]["profiles"]



# HTTP конфиг
HTTP_TIMEOUT = _config["http"]["timeout"]
