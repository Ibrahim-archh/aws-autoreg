"""
Сервис временной почты — патч под cloudflare_temp_email (myrealagent.ru)
Сохраняет тот же интерфейс: create_temp_email() -> (address, jwt_token),
                              wait_for_verification_email(jwt_token, timeout) -> code|None
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import random
import string
import re

from config import (
    EMAIL_WORKER_URL,
    EMAIL_DOMAIN,
    EMAIL_PREFIX_LENGTH,
    EMAIL_WAIT_TIMEOUT,
    EMAIL_POLL_INTERVAL,
    HTTP_TIMEOUT,
)
from helpers.utils import http_session, get_user_agent


def _headers(token: str | None = None) -> dict:
    h = {
        "User-Agent": get_user_agent(),
        "Content-Type": "application/json",
    }
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def create_temp_email():
    """
    Создать временный ящик через наш cloudflare_temp_email Worker.
    Возвращает: (address, jwt_token) или (None, None) при ошибке.
    """
    prefix = ''.join(random.choices(
        string.ascii_lowercase + string.digits,
        k=EMAIL_PREFIX_LENGTH,
    ))

    try:
        print(f"  Создаю ящик на {EMAIL_DOMAIN}...")
        resp = http_session.post(
            f"{EMAIL_WORKER_URL}/api/new_address",
            headers=_headers(),
            json={"name": prefix, "domain": EMAIL_DOMAIN},
            timeout=HTTP_TIMEOUT,
        )

        if resp.status_code != 200:
            print(f"  Ошибка создания: HTTP {resp.status_code} - {resp.text[:200]}")
            return None, None

        data = resp.json()
        jwt_token = data.get("jwt")
        address = data.get("address")

        if not jwt_token:
            print("  Ошибка: в ответе нет jwt")
            return None, None

        if not address:
            address = f"tmp{prefix}@{EMAIL_DOMAIN}"

        print(f"  Ящик готов: {address}")
        return address, jwt_token

    except Exception as e:
        print(f"  Ошибка создания почты: {e}")
        return None, None


def _fetch_mails(jwt_token: str) -> list:
    """Список писем по JWT адреса."""
    try:
        resp = http_session.get(
            f"{EMAIL_WORKER_URL}/api/mails?limit=20&offset=0",
            headers=_headers(jwt_token),
            timeout=HTTP_TIMEOUT,
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("results") or data.get("mails") or []
    except Exception:
        pass
    return []


def _get_mail_detail(jwt_token: str, mail_id) -> dict | None:
    """Детали одного письма."""
    try:
        resp = http_session.get(
            f"{EMAIL_WORKER_URL}/api/mail/{mail_id}",
            headers=_headers(jwt_token),
            timeout=HTTP_TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def _strip_email_headers(raw: str) -> str:
    """Отрезать RFC822 заголовки и вернуть тело письма.
    Multipart — собрать text/plain и text/html секции."""
    if not raw:
        return ""
    parts = re.split(r'\r?\n\r?\n', raw, maxsplit=1)
    body = parts[1] if len(parts) > 1 else raw

    boundaries = re.findall(r'boundary="?([^"\s;]+)', raw)
    if boundaries:
        collected = []
        for b in boundaries:
            pattern = rf'--{re.escape(b)}\s*\r?\n([\s\S]*?)(?=--{re.escape(b)})'
            for chunk in re.findall(pattern, body):
                ct_low = chunk.lower()
                if 'text/plain' in ct_low or 'text/html' in ct_low:
                    sub_parts = re.split(r'\r?\n\r?\n', chunk, maxsplit=1)
                    if len(sub_parts) > 1:
                        collected.append(sub_parts[1])
        if collected:
            return "\n".join(collected)
    return body


def _extract_code(text: str) -> str | None:
    """Вытащить 6-значный код AWS Builder ID.
    Игнорирует заголовки письма и мусорные значения."""
    if not text:
        return None

    head = text[:600]
    if 'Content-Type:' in head or 'Received:' in head or 'DKIM-Signature' in head:
        text = _strip_email_headers(text)

    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'=\r?\n', '', clean)
    clean = re.sub(r'=[0-9A-Fa-f]{2}', ' ', clean)

    blacklist = {f"{d}" * 6 for d in "0123456789"}

    near_patterns = [
        r'(?:verification\s+code|code\s+is|your\s+code|builder\s+id|one[- ]?time\s+(?:password|code)|otp)\D{0,80}?(\d{6})\b',
        r'\b(\d{6})\D{0,80}?(?:is\s+your\s+(?:verification|builder|aws|amazon|one[- ]?time)|verification\s+code|builder\s+id|expires?)',
    ]
    for pat in near_patterns:
        for m in re.finditer(pat, clean, re.IGNORECASE):
            code = m.group(1)
            if code not in blacklist:
                return code

    for m in re.finditer(r'\b(\d{6})\b', clean):
        code = m.group(1)
        if code in blacklist:
            continue
        if code.startswith(('19', '20')) and 1900 <= int(code[:4]) <= 2100:
            continue
        return code

    return None


def wait_for_verification_email(jwt_token: str, timeout: int = None) -> str | None:
    """
    Ждать письмо от AWS и достать код подтверждения.
    Возвращает 6-значный код или None.
    """
    if timeout is None:
        timeout = EMAIL_WAIT_TIMEOUT

    print(f"  Жду письмо от AWS (макс {timeout} сек)...")
    start = time.time()
    seen_ids = set()

    while time.time() - start < timeout:
        mails = _fetch_mails(jwt_token)

        for m in mails:
            mid = m.get("id") or m.get("message_id")
            if mid in seen_ids:
                continue
            seen_ids.add(mid)

            raw = m.get("raw") or ""
            subject = m.get("subject") or ""
            sender = (m.get("source") or m.get("from") or "").lower()

            if raw and (not subject or not sender):
                msub = re.search(r'^Subject:\s*(.+)$', raw, re.MULTILINE | re.IGNORECASE)
                if msub and not subject:
                    subject = msub.group(1).strip()
                mfrom = re.search(r'^From:\s*(.+)$', raw, re.MULTILINE | re.IGNORECASE)
                if mfrom and not sender:
                    sender = mfrom.group(1).strip().lower()

            is_aws = ('amazon' in sender or 'aws' in sender
                      or 'verify' in subject.lower()
                      or 'verification' in subject.lower()
                      or 'builder id' in subject.lower())

            if not is_aws:
                continue

            print(f"\n  Письмо от AWS: {subject[:80]}")

            # КОД ИЩЕМ ТОЛЬКО В ТЕЛЕ, не в subject (там не бывает)
            code = _extract_code(raw)

            if not code:
                detail = _get_mail_detail(jwt_token, mid)
                if detail:
                    code = (_extract_code(detail.get("raw") or "")
                            or _extract_code(detail.get("text") or "")
                            or _extract_code(detail.get("html") or ""))

            if code:
                print(f"  Код: {code}")
                return code

            print("  Письмо есть, но кода не нашли — продолжаю ждать...")

        elapsed = int(time.time() - start)
        print(f"  ... ожидание ({elapsed}с)", end="\r")
        time.sleep(EMAIL_POLL_INTERVAL)

    print(f"\n  Письмо не пришло за {timeout} сек")
    return None
