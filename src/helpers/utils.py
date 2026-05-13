import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import random
import requests
from config import REGION_CURRENT, REGION_PROFILES, DEVICE_TYPE

# HTTP-сессия для всех запросов
http_session = requests.Session()


def get_region_config():
    """Конфиг текущего региона из config.yaml."""
    return REGION_PROFILES.get(REGION_CURRENT, REGION_PROFILES.get("usa"))


def get_user_agent():
    """Случайный User-Agent под текущий регион и тип устройства."""
    region_config = get_region_config()
    if DEVICE_TYPE == "mobile":
        user_agents = region_config.get("mobile_user_agents", [])
        if not user_agents:
            user_agents = region_config.get("desktop_user_agents", [])
    else:
        user_agents = region_config.get("desktop_user_agents", [])

    if not user_agents:
        user_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
            if DEVICE_TYPE == "mobile" else
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.7778.167 Safari/537.36"
        ]

    return random.choice(user_agents)


def is_mobile():
    """True если в конфиге выбран мобильный режим."""
    return DEVICE_TYPE == "mobile"


def get_locale():
    """Локаль текущего региона."""
    region_config = get_region_config()
    return region_config.get("locale", "en-US")


def get_timezone():
    """Таймзона текущего региона."""
    region_config = get_region_config()
    return region_config.get("timezone", "America/New_York")


def get_accept_language():
    """Accept-Language заголовок для текущего региона."""
    region_config = get_region_config()
    return region_config.get("accept_language", "en-US,en;q=0.9")


def extract_verification_code(text: str):
    """
    Извлечь 6-значный код подтверждения из текста.
    Используется только для outlook IMAP / резервных сценариев.
    Для писем cloudflare_temp_email — отдельная логика в services/email_service.py.
    """
    if not text:
        return None

    patterns = [
        r'(?:verification\s+code|your\s+code|code\s+is|builder\s+id)\D{0,80}?(\d{6})\b',
        r'\b(\d{6})\b',
    ]

    blacklist = {f"{d}" * 6 for d in "0123456789"}

    for pattern in patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            code = m.group(1)
            if code in blacklist:
                continue
            if code.startswith(('19', '20')) and 1900 <= int(code[:4]) <= 2100:
                continue
            return code

    return None


# === Поддержка динамического выбора региона ===

def get_region_config_by_name(region_name):
    """Конфиг указанного региона."""
    return REGION_PROFILES.get(region_name, REGION_PROFILES.get("usa"))


def get_user_agent_for_region(region_name):
    """User-Agent для указанного региона + текущего типа устройства.
    Берёт из config.yaml (а не генерит синтетически), чтобы UA совпадал
    с реальной версией Chrome 148 в profile'ах."""
    region_config = get_region_config_by_name(region_name)
    if DEVICE_TYPE == "mobile":
        user_agents = region_config.get("mobile_user_agents", [])
        if not user_agents:
            user_agents = region_config.get("desktop_user_agents", [])
    else:
        user_agents = region_config.get("desktop_user_agents", [])

    if not user_agents:
        # Запасной актуальный Chrome 148
        return ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/148.0.7778.167 Safari/537.36")

    return random.choice(user_agents)


def get_locale_for_region(region_name):
    """Локаль указанного региона."""
    region_config = get_region_config_by_name(region_name)
    return region_config.get("locale", "en-US")


def get_timezone_for_region(region_name):
    """Таймзона указанного региона."""
    region_config = get_region_config_by_name(region_name)
    return region_config.get("timezone", "America/New_York")


def get_accept_language_for_region(region_name):
    """Accept-Language указанного региона."""
    region_config = get_region_config_by_name(region_name)
    return region_config.get("accept_language", "en-US,en;q=0.9")
