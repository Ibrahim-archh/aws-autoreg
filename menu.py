# -*- coding: utf-8 -*-
"""
Интерактивное главное меню AWS Builder ID Авторег.

Запуск:
    python menu.py
"""
import os
import sys
import json
import subprocess
from pathlib import Path

# Кросс-платформенные ANSI цвета
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    R = "\033[31m"      # red
    G = "\033[32m"      # green
    Y = "\033[33m"      # yellow
    B = "\033[34m"      # blue
    M = "\033[35m"      # magenta
    CY = "\033[36m"     # cyan
    W = "\033[37m"      # white


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

CONFIG_PATH = ROOT / "config" / "config.yaml"


def clear():
    os.system("cls" if sys.platform == "win32" else "clear")


def banner():
    print(f"{C.M}{C.BOLD}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       AWS Builder ID Авторег — главное меню              ║")
    print("║                  github.com/Ibrahim-archh                ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(C.RESET)


def read_config_field(field: str) -> str:
    if not CONFIG_PATH.exists():
        return ""
    import re
    text = CONFIG_PATH.read_text(encoding="utf-8")
    m = re.search(rf'{field}:\s*"([^"]*)"', text)
    return m.group(1) if m else ""


def write_config_field(field: str, value: str):
    if not CONFIG_PATH.exists():
        return
    import re
    text = CONFIG_PATH.read_text(encoding="utf-8")
    text = re.sub(rf'{field}:\s*"[^"]*"', f'{field}: "{value}"', text)
    CONFIG_PATH.write_text(text, encoding="utf-8", newline="\n")


REGION_FLAGS = {
    "usa": "🇺🇸 USA",
    "germany": "🇩🇪 Germany",
    "japan": "🇯🇵 Japan",
}
DEVICE_ICONS = {
    "desktop": "💻 desktop",
    "mobile": "📱 mobile",
}


def status_line():
    worker = read_config_field("worker_url") or "(не задан)"
    domain = read_config_field("domain") or "(не задан)"
    region = read_config_field_yaml_simple("current") or "?"
    device = read_config_field_yaml_simple("device_type") or "?"
    proxy = read_config_field_yaml_simple("use_proxy") or "false"

    region_view = REGION_FLAGS.get(region, region)
    device_view = DEVICE_ICONS.get(device, device)
    proxy_mark = f"{C.G}🟢 вкл{C.RESET}" if proxy.lower() == "true" else f"{C.DIM}⚪ выкл{C.RESET}"

    print(f"  {C.DIM}Worker:{C.RESET} {worker}")
    print(f"  {C.DIM}Домен: {C.RESET} {domain}")
    print(f"  {C.DIM}Регион:{C.RESET} {region_view}   {C.DIM}Устройство:{C.RESET} {device_view}   {C.DIM}Прокси:{C.RESET} {proxy_mark}")
    print()


def read_config_field_yaml_simple(field: str) -> str:
    """Простой поиск 'field: value' для нестрочных значений (true/false/usa)."""
    if not CONFIG_PATH.exists():
        return ""
    import re
    text = CONFIG_PATH.read_text(encoding="utf-8")
    m = re.search(rf'{field}:\s*"?([^"\s#]+)', text)
    return m.group(1) if m else ""


# ============== Меню действия ==============

def action_configure():
    print(f"\n{C.CY}Настройка Cloudflare Worker для почты{C.RESET}\n")
    print("Если ты ещё НЕ деплоил cloudflare_temp_email Worker — сначала пройди docs/SETUP.md")
    print("Здесь просто введи готовые значения от уже работающего Worker'а.\n")

    cur_worker = read_config_field("worker_url")
    cur_domain = read_config_field("domain")
    cur_admin = read_config_field("admin_password")

    print(f"{C.DIM}Текущий worker_url:{C.RESET} {cur_worker}")
    worker = input(f"{C.Y}worker_url{C.RESET} [Enter = оставить как есть]: ").strip()
    if not worker:
        worker = cur_worker

    print(f"{C.DIM}Текущий domain:{C.RESET} {cur_domain}")
    domain = input(f"{C.Y}domain{C.RESET} [Enter = оставить]: ").strip()
    if not domain:
        domain = cur_domain

    print(f"{C.DIM}Текущий admin_password:{C.RESET} {'*' * len(cur_admin) if cur_admin else '(пусто)'}")
    admin = input(f"{C.Y}admin_password{C.RESET} [Enter = оставить]: ").strip()
    if not admin:
        admin = cur_admin

    write_config_field("worker_url", worker)
    write_config_field("domain", domain)
    write_config_field("admin_password", admin)

    print(f"\n{C.G}Сохранено в config/config.yaml{C.RESET}")

    # Тест соединения
    if input(f"\n{C.Y}Сделать тестовый запрос к Worker? [y/N]: {C.RESET}").lower() == "y":
        try:
            import requests
            r = requests.post(
                f"{worker}/api/new_address",
                json={"name": "menucheck"},
                timeout=15,
            )
            if r.status_code == 200 and r.json().get("jwt"):
                addr = r.json().get("address", "?")
                print(f"{C.G}OK{C.RESET} — Worker отвечает, тестовый ящик: {addr}")
            else:
                print(f"{C.R}Не сработало:{C.RESET} HTTP {r.status_code} — {r.text[:200]}")
        except Exception as e:
            print(f"{C.R}Ошибка соединения:{C.RESET} {e}")

    input(f"\n{C.DIM}[Enter для возврата в меню]{C.RESET}")


def action_single():
    print(f"\n{C.CY}Одиночная регистрация{C.RESET}\n")
    main_path = ROOT / "src" / "runners" / "main.py"
    subprocess.run([sys.executable, str(main_path)], cwd=ROOT)
    input(f"\n{C.DIM}[Enter для возврата в меню]{C.RESET}")


def action_batch():
    print(f"\n{C.CY}Батч-регистрация{C.RESET}\n")

    n_str = input(f"{C.Y}Сколько аккаунтов зарегистрировать?{C.RESET} (число, например 10): ").strip()
    try:
        n = int(n_str)
        if n < 1 or n > 1000:
            print(f"{C.R}Число должно быть от 1 до 1000{C.RESET}")
            input("[Enter]")
            return
    except ValueError:
        print(f"{C.R}Некорректное число{C.RESET}")
        input("[Enter]")
        return

    print(f"\nЗапуск {C.G}{n}{C.RESET} регистраций последовательно (одна за другой)...\n")
    print(f"{C.DIM}Каждая занимает 2-5 минут. Между регистрациями пауза 30 секунд для безопасности.{C.RESET}\n")

    main_path = ROOT / "src" / "runners" / "main.py"
    success = 0
    failed = 0
    for i in range(1, n + 1):
        print(f"\n{C.M}═══ Регистрация {i}/{n} ═══{C.RESET}")
        r = subprocess.run([sys.executable, str(main_path)], cwd=ROOT)
        if r.returncode == 0:
            success += 1
        else:
            failed += 1
        if i < n:
            import time
            print(f"\n{C.DIM}Пауза 30 сек перед следующей...{C.RESET}")
            time.sleep(30)

    print(f"\n{C.G}Готово!{C.RESET}  Успешно: {success}/{n}  Провалов: {failed}/{n}")
    print(f"Результаты в accounts.jsonl и accounts_failed.jsonl")
    input(f"\n{C.DIM}[Enter]{C.RESET}")


def action_view_mail():
    print(f"\n{C.CY}Просмотр писем и OTP-кодов{C.RESET}\n")

    worker = read_config_field("worker_url")
    admin = read_config_field("admin_password")
    if not worker or not admin:
        print(f"{C.R}Сначала настрой Worker в пункте 1{C.RESET}")
        input("[Enter]")
        return

    addr = input(f"{C.Y}Адрес{C.RESET} (Enter = все письма): ").strip()
    n_str = input(f"{C.Y}Сколько последних?{C.RESET} (Enter = 10): ").strip() or "10"
    try:
        n = int(n_str)
    except ValueError:
        n = 10

    import re
    try:
        import requests
        r = requests.get(
            f"{worker}/admin/mails?limit={n}&offset=0",
            headers={"x-admin-auth": admin},
            timeout=15,
        )
        data = r.json()
    except Exception as e:
        print(f"{C.R}Запрос упал:{C.RESET} {e}")
        input("[Enter]")
        return

    mails = data.get("results") if isinstance(data, dict) else data
    mails = mails or []
    if addr:
        mails = [m for m in mails if m.get("address") == addr]

    if not mails:
        print(f"{C.Y}Писем нет{C.RESET}")
        input("[Enter]")
        return

    from services.email_service import _extract_code

    for m in mails:
        raw = m.get("raw", "")
        a = m.get("address", "?")
        created = m.get("created_at", "")
        subj_m = re.search(r"^Subject:\s*(.+)$", raw, re.M | re.I)
        from_m = re.search(r"^From:\s*(.+)$", raw, re.M | re.I)
        subj = subj_m.group(1).strip() if subj_m else "(нет темы)"
        from_ = from_m.group(1).strip() if from_m else "(?)"
        code = _extract_code(raw)
        print(f"\n{C.CY}[{created}] {a}{C.RESET}")
        print(f"  From:    {from_}")
        print(f"  Subject: {subj}")
        if code:
            print(f"  CODE:    {C.G}{C.BOLD}{code}{C.RESET}")
        else:
            print(f"  CODE:    {C.DIM}(не найден){C.RESET}")

    input(f"\n{C.DIM}[Enter]{C.RESET}")


def action_view_accounts():
    print(f"\n{C.CY}Зарегистрированные аккаунты{C.RESET}\n")
    p = ROOT / "accounts.jsonl"
    if not p.exists():
        print(f"{C.Y}Файл accounts.jsonl пуст или не создан{C.RESET}")
        input("[Enter]")
        return
    lines = p.read_text(encoding="utf-8").splitlines()
    print(f"Всего записей: {C.G}{len(lines)}{C.RESET}\n")
    for i, line in enumerate(lines, 1):
        try:
            d = json.loads(line)
            print(f"  {C.DIM}#{i:3d}{C.RESET}  {d.get('email','?'):40s}  {C.Y}{d.get('password','?')}{C.RESET}  {d.get('created_at','?')}")
        except json.JSONDecodeError:
            print(f"  {C.R}#{i} bad json{C.RESET}")
    input(f"\n{C.DIM}[Enter]{C.RESET}")


def action_view_failed():
    print(f"\n{C.CY}Провальные попытки{C.RESET}\n")
    p = ROOT / "accounts_failed.jsonl"
    if not p.exists():
        print(f"{C.G}Файл accounts_failed.jsonl пуст{C.RESET}")
        input("[Enter]")
        return
    lines = p.read_text(encoding="utf-8").splitlines()
    print(f"Всего провалов: {C.R}{len(lines)}{C.RESET}\n")
    for i, line in enumerate(lines, 1):
        try:
            d = json.loads(line)
            print(f"  {C.DIM}#{i}{C.RESET} {d.get('email','?'):40s}")
            print(f"      reason: {C.Y}{d.get('reason','?')[:80]}{C.RESET}")
        except json.JSONDecodeError:
            print(f"  {C.R}#{i} bad json{C.RESET}")
    input(f"\n{C.DIM}[Enter]{C.RESET}")


def action_switch():
    print(f"\n{C.CY}Сменить регион / устройство / прокси{C.RESET}\n")
    print("  1. Сменить регион (usa / germany / japan)")
    print("  2. Сменить устройство (desktop / mobile)")
    print("  3. Включить/выключить прокси")
    print("  0. Назад")
    choice = input(f"\n{C.Y}>{C.RESET} ").strip()

    text = CONFIG_PATH.read_text(encoding="utf-8")
    import re

    if choice == "1":
        print(f"\n  1. {REGION_FLAGS['usa']}")
        print(f"  2. {REGION_FLAGS['germany']}")
        print(f"  3. {REGION_FLAGS['japan']}")
        sub = input(f"{C.Y}>{C.RESET} ").strip()
        mapping = {"1": "usa", "2": "germany", "3": "japan"}
        new = mapping.get(sub) or sub.lower()
        if new in ("usa", "germany", "japan"):
            text = re.sub(r'current:\s*"[^"]*"', f'current: "{new}"', text)
            CONFIG_PATH.write_text(text, encoding="utf-8", newline="\n")
            print(f"{C.G}Регион установлен: {REGION_FLAGS[new]}{C.RESET}")
        else:
            print(f"{C.R}Неверный регион{C.RESET}")
    elif choice == "2":
        print(f"\n  1. {DEVICE_ICONS['desktop']}")
        print(f"  2. {DEVICE_ICONS['mobile']}")
        sub = input(f"{C.Y}>{C.RESET} ").strip()
        mapping = {"1": "desktop", "2": "mobile"}
        new = mapping.get(sub) or sub.lower()
        if new in ("desktop", "mobile"):
            text = re.sub(r'device_type:\s*"[^"]*"', f'device_type: "{new}"', text)
            CONFIG_PATH.write_text(text, encoding="utf-8", newline="\n")
            print(f"{C.G}Устройство установлено: {DEVICE_ICONS[new]}{C.RESET}")
        else:
            print(f"{C.R}Неверный тип{C.RESET}")
    elif choice == "3":
        cur = read_config_field_yaml_simple("use_proxy")
        new_val = "false" if cur.lower() == "true" else "true"
        text = re.sub(r'use_proxy:\s*\S+', f'use_proxy: {new_val}', text)
        CONFIG_PATH.write_text(text, encoding="utf-8", newline="\n")
        print(f"{C.G}Прокси теперь: {new_val}{C.RESET}")
        if new_val == "true":
            cur_url = read_config_field("proxy_url")
            new_url = input(f"proxy_url (Enter = оставить '{cur_url}'): ").strip()
            if new_url:
                write_config_field("proxy_url", new_url)
                print(f"{C.G}Прокси URL обновлён{C.RESET}")

    input(f"\n{C.DIM}[Enter]{C.RESET}")


def action_clear_accounts():
    print(f"\n{C.CY}Очистить accounts.jsonl{C.RESET}\n")
    p = ROOT / "accounts.jsonl"
    pf = ROOT / "accounts_failed.jsonl"
    print("  1. Очистить только accounts.jsonl (успехи)")
    print("  2. Очистить только accounts_failed.jsonl (провалы)")
    print("  3. Очистить ОБА")
    print("  0. Назад")
    c = input(f"\n{C.Y}>{C.RESET} ").strip()

    if c == "1" and p.exists():
        p.unlink(); print(f"{C.G}accounts.jsonl удалён{C.RESET}")
    elif c == "2" and pf.exists():
        pf.unlink(); print(f"{C.G}accounts_failed.jsonl удалён{C.RESET}")
    elif c == "3":
        if p.exists(): p.unlink()
        if pf.exists(): pf.unlink()
        print(f"{C.G}Оба файла удалены{C.RESET}")

    input(f"\n{C.DIM}[Enter]{C.RESET}")


# ============== Главный цикл ==============

MENU = [
    ("1", "Настройка Cloudflare Worker (worker_url, domain, admin)", action_configure),
    ("2", "Одиночная регистрация", action_single),
    ("3", "Батч-регистрация (несколько подряд)", action_batch),
    ("4", "Просмотр писем и OTP-кодов", action_view_mail),
    ("5", "Список зарегистрированных аккаунтов", action_view_accounts),
    ("6", "Провальные попытки", action_view_failed),
    ("7", "Сменить регион / устройство / прокси", action_switch),
    ("8", "Очистить accounts.jsonl", action_clear_accounts),
    ("0", "Выход", None),
]


def main():
    while True:
        clear()
        banner()
        status_line()
        for key, label, _ in MENU:
            mark = f"{C.R}*{C.RESET}" if key == "0" else f"{C.G}{key}{C.RESET}"
            print(f"  {mark}  {label}")
        choice = input(f"\n{C.Y}>{C.RESET} ").strip()

        for key, _, fn in MENU:
            if choice == key:
                if fn is None:
                    print(f"\n{C.M}До встречи{C.RESET}\n")
                    return
                try:
                    fn()
                except KeyboardInterrupt:
                    print(f"\n{C.Y}Прервано{C.RESET}")
                    input("[Enter]")
                except Exception as e:
                    print(f"\n{C.R}Ошибка:{C.RESET} {e}")
                    input("[Enter]")
                break
        else:
            print(f"{C.R}Неверный выбор{C.RESET}")
            input("[Enter]")


def cli():
    """Не-интерактивный CLI для автоматизации (ботам / ИИ-агентам / скриптам)."""
    import argparse, re

    p = argparse.ArgumentParser(
        prog="menu.py",
        description="AWS Builder ID авторег. Без аргументов — интерактивное меню. С флагами — non-interactive.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python menu.py                                   # интерактивное меню
  python menu.py --run                             # одна регистрация
  python menu.py --batch 50                        # 50 регистраций подряд
  python menu.py --batch 10 --delay 60             # 10 регистраций, пауза 60 сек
  python menu.py --set-worker https://x.workers.dev --set-domain my.ru --set-admin pwd
  python menu.py --region usa --device desktop     # сменить регион и устройство
  python menu.py --proxy on --proxy-url socks5://u:p@h:port
  python menu.py --proxy off
  python menu.py --mail                            # все письма (последние 10)
  python menu.py --mail tmpXXX@my.ru               # письма для адреса
  python menu.py --mail tmpXXX@my.ru --code-only   # только код (для shell)
  python menu.py --list                            # все аккаунты (JSON в stdout)
  python menu.py --list --format csv               # CSV
  python menu.py --failed                          # неудачные попытки
  python menu.py --clear accounts                  # стереть accounts.jsonl
  python menu.py --clear failed                    # стереть accounts_failed.jsonl
  python menu.py --clear all                       # стереть оба
  python menu.py --status                          # текущая конфигурация (JSON)
  python menu.py --test-worker                     # проверить соединение с Worker
""",
    )

    # Действия (взаимоисключающие)
    g = p.add_mutually_exclusive_group()
    g.add_argument("--run", action="store_true", help="запустить одну регистрацию")
    g.add_argument("--batch", type=int, metavar="N", help="запустить N регистраций подряд")
    g.add_argument("--mail", nargs="?", const="", metavar="ADDRESS",
                   help="показать письма (опц. для конкретного адреса)")
    g.add_argument("--list", action="store_true", help="вывести список зарег. аккаунтов")
    g.add_argument("--failed", action="store_true", help="вывести список провалов")
    g.add_argument("--clear", choices=["accounts", "failed", "all"], help="очистить журналы")
    g.add_argument("--status", action="store_true", help="вывести текущую конфигурацию")
    g.add_argument("--test-worker", action="store_true", help="проверить связь с Worker")

    # Опции
    p.add_argument("--delay", type=int, default=30, metavar="SEC",
                   help="пауза между регистрациями в батче (сек, default 30)")
    p.add_argument("--mail-limit", type=int, default=10, metavar="N",
                   help="сколько последних писем показать (default 10)")
    p.add_argument("--code-only", action="store_true",
                   help="с --mail: вывести только 6-значный код (для shell-pipe)")
    p.add_argument("--format", choices=["json", "jsonl", "csv"], default="jsonl",
                   help="формат вывода --list/--failed (default jsonl)")

    # Установка конфига
    p.add_argument("--set-worker", metavar="URL", help="установить worker_url")
    p.add_argument("--set-domain", metavar="DOMAIN", help="установить domain")
    p.add_argument("--set-admin", metavar="PWD", help="установить admin_password")
    p.add_argument("--region", choices=["usa", "germany", "japan"], help="сменить регион")
    p.add_argument("--device", choices=["desktop", "mobile"], help="сменить устройство")
    p.add_argument("--proxy", choices=["on", "off"], help="включить/выключить прокси")
    p.add_argument("--proxy-url", metavar="URL", help="установить proxy_url")
    p.add_argument("--headless", choices=["true", "false"], help="режим headless для browser")

    args = p.parse_args()

    # === Установка значений конфига (можно вместе с действием) ===
    if args.set_worker:
        write_config_field("worker_url", args.set_worker)
        print(f"worker_url = {args.set_worker}")
    if args.set_domain:
        write_config_field("domain", args.set_domain)
        print(f"domain = {args.set_domain}")
    if args.set_admin:
        write_config_field("admin_password", args.set_admin)
        print(f"admin_password = ***")
    if args.proxy_url:
        write_config_field("proxy_url", args.proxy_url)
        print(f"proxy_url = {args.proxy_url}")

    cfg_text = CONFIG_PATH.read_text(encoding="utf-8") if CONFIG_PATH.exists() else ""
    if args.region:
        cfg_text = re.sub(r'current:\s*"[^"]*"', f'current: "{args.region}"', cfg_text)
        print(f"region = {args.region}")
    if args.device:
        cfg_text = re.sub(r'device_type:\s*"[^"]*"', f'device_type: "{args.device}"', cfg_text)
        print(f"device = {args.device}")
    if args.proxy:
        v = "true" if args.proxy == "on" else "false"
        cfg_text = re.sub(r'use_proxy:\s*\S+', f'use_proxy: {v}', cfg_text)
        print(f"proxy = {v}")
    if args.headless:
        cfg_text = re.sub(r'headless:\s*\S+', f'headless: {args.headless}', cfg_text)
        print(f"headless = {args.headless}")
    if CONFIG_PATH.exists() and cfg_text:
        CONFIG_PATH.write_text(cfg_text, encoding="utf-8", newline="\n")

    # === Действия ===
    if args.run:
        main_path = ROOT / "src" / "runners" / "main.py"
        return subprocess.call([sys.executable, str(main_path)], cwd=ROOT)

    if args.batch is not None:
        n = max(1, min(args.batch, 1000))
        main_path = ROOT / "src" / "runners" / "main.py"
        success = failed = 0
        for i in range(1, n + 1):
            print(f"\n=== {i}/{n} ===", flush=True)
            rc = subprocess.call([sys.executable, str(main_path)], cwd=ROOT)
            if rc == 0:
                success += 1
            else:
                failed += 1
            if i < n:
                import time as _t
                _t.sleep(args.delay)
        print(f"\nDONE: success={success} failed={failed}")
        return 0

    if args.mail is not None:
        worker = read_config_field("worker_url")
        admin = read_config_field("admin_password")
        if not worker or not admin:
            print("ERROR: worker_url или admin_password не заданы", file=sys.stderr)
            return 2
        import requests
        from services.email_service import _extract_code
        try:
            r = requests.get(
                f"{worker}/admin/mails?limit={args.mail_limit}&offset=0",
                headers={"x-admin-auth": admin}, timeout=15,
            )
            data = r.json()
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 3
        mails = data.get("results") if isinstance(data, dict) else data
        mails = mails or []
        if args.mail:
            mails = [m for m in mails if m.get("address") == args.mail]
        if args.code_only:
            for m in mails:
                code = _extract_code(m.get("raw", ""))
                if code:
                    print(code)
                    return 0
            return 1  # код не найден
        # Полный JSON-вывод
        out = []
        for m in mails:
            raw = m.get("raw", "")
            subj_m = re.search(r"^Subject:\s*(.+)$", raw, re.M | re.I)
            from_m = re.search(r"^From:\s*(.+)$", raw, re.M | re.I)
            out.append({
                "id": m.get("id"),
                "address": m.get("address"),
                "from": from_m.group(1).strip() if from_m else None,
                "subject": subj_m.group(1).strip() if subj_m else None,
                "code": _extract_code(raw),
                "created_at": m.get("created_at"),
            })
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    if args.list or args.failed:
        fn = "accounts.jsonl" if args.list else "accounts_failed.jsonl"
        f = ROOT / fn
        if not f.exists():
            print(f"{fn}: пусто")
            return 0
        rows = []
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        if args.format == "json":
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        elif args.format == "csv":
            import csv
            if rows:
                w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
        else:  # jsonl
            for r in rows:
                print(json.dumps(r, ensure_ascii=False))
        return 0

    if args.clear:
        files = {
            "accounts": ["accounts.jsonl"],
            "failed": ["accounts_failed.jsonl"],
            "all": ["accounts.jsonl", "accounts_failed.jsonl"],
        }[args.clear]
        for f in files:
            p = ROOT / f
            if p.exists():
                p.unlink()
                print(f"deleted: {f}")
        return 0

    if args.status:
        status = {
            "worker_url": read_config_field("worker_url"),
            "domain": read_config_field("domain"),
            "admin_password_set": bool(read_config_field("admin_password")),
            "region": read_config_field_yaml_simple("current"),
            "device": read_config_field_yaml_simple("device_type"),
            "use_proxy": read_config_field_yaml_simple("use_proxy"),
            "proxy_url": read_config_field("proxy_url"),
            "headless": read_config_field_yaml_simple("headless"),
            "accounts_count": sum(1 for _ in open(ROOT / "accounts.jsonl", encoding="utf-8")) if (ROOT / "accounts.jsonl").exists() else 0,
            "failed_count": sum(1 for _ in open(ROOT / "accounts_failed.jsonl", encoding="utf-8")) if (ROOT / "accounts_failed.jsonl").exists() else 0,
        }
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return 0

    if args.test_worker:
        worker = read_config_field("worker_url")
        if not worker:
            print("ERROR: worker_url не задан", file=sys.stderr)
            return 2
        import requests
        try:
            r = requests.post(
                f"{worker}/api/new_address",
                json={"name": "clitest"},
                timeout=15,
            )
            if r.status_code == 200 and r.json().get("jwt"):
                print(json.dumps({"ok": True, "address": r.json().get("address")}, ensure_ascii=False))
                return 0
            else:
                print(json.dumps({"ok": False, "http": r.status_code, "body": r.text[:200]}, ensure_ascii=False))
                return 1
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False), file=sys.stderr)
            return 3

    # Если из CLI ничего конкретного не вызвано но конфиг менялся — просто выйдем
    if any([args.set_worker, args.set_domain, args.set_admin, args.proxy_url,
            args.region, args.device, args.proxy, args.headless]):
        return 0

    # Иначе — интерактивное меню
    main()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(cli() or 0)
    except KeyboardInterrupt:
        print(f"\n{C.M}Прервано{C.RESET}\n")
