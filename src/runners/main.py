import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from faker import Faker
import random
import time
import json
import os
from datetime import datetime
from config import HEADLESS, SLOW_MO
from services.email_service import create_temp_email, wait_for_verification_email
from selenium.webdriver.common.action_chains import ActionChains
from helpers.multilang import lang_selector


fake = Faker('en_US')


def generate_strong_password():
    """Сгенерировать надёжный пароль"""
    import string
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choices(chars, k=16))
    # обеспечить буквы, цифры, спец. символы
    password = random.choice(string.ascii_uppercase) + random.choice(string.ascii_lowercase) + \
               random.choice(string.digits) + random.choice("!@#$%^&*") + password[4:]
    return password


def save_account(email, password, name, jwt_token=""):
    """Сохранить данные аккаунта в файл"""
    account_info = {
        "email": email,
        "password": password,
        "name": name,
        "jwt_token": jwt_token,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "registered"
    }
    
    file_path = "accounts.json"
    # JSONL для много-процессной безопасности (одна запись на строку) append-режим, без гонок
    file_path = "accounts.jsonl"
    
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(account_info, ensure_ascii=False) + "\n")
        print(f"✅ Аккаунт сохранён: {email}")
    except Exception as e:
        print(f"❌ Не удалось сохранить аккаунт: {e}")


def save_account_failed(email, password, name, jwt_token="", reason="unknown"):
    """Записать неудачную попытку в accounts_failed.jsonl (для отладки)."""
    account_info = {
        "email": email,
        "password": password,
        "name": name,
        "jwt_token": jwt_token,
        "reason": reason,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "failed"
    }
    try:
        with open("accounts_failed.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(account_info, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"❌ Ошибка записи failed: {e}")


def save_account_info(email, password, name, jwt_token):
    """Сохранить данные аккаунта в файл"""
    accounts_file = "accounts.json"
    accounts = []

    if os.path.exists(accounts_file):
        with open(accounts_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)

    account = {
        "email": email,
        "password": password,
        "name": name,
        "jwt_token": jwt_token,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "active"
    }
    accounts.append(account)

    with open(accounts_file, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)

    print(f"Информация записана в {accounts_file}")


def human_delay(min_sec=0.5, max_sec=2.0):
    """Имитация человеческой задержки"""
    # Добавить случайности，естькогда会естьболеедлинный 停顿 (имитация раздумий)
    if random.random() < 0.15:  # 15% вероятность более длинной паузы
        time.sleep(random.uniform(2.5, 5.0))
    time.sleep(random.uniform(min_sec, max_sec))


def human_type(element, text):
    """Имитация человеческого ввода, переменная скорость"""
    # Базовый множитель скорости (0.8 ~ 1.2)，у разных людей разная скорость
    speed_factor = random.uniform(0.7, 1.3)
    
    for char in text:
        element.send_keys(char)
        # база + случайность
        delay = random.uniform(0.04, 0.15) * speed_factor
        
        # случайные паузы (пауза между нажатиями)
        if random.random() < 0.05:
            delay += random.uniform(0.2, 0.5)
            
        time.sleep(delay)


def human_click(driver, element):
    """Имитация клика мышью"""
    try:
        # 1. 移动→элементпозиция (с небольшим случайным смещением)
        action = ActionChains(driver)
        # 偏移ненужно太большой，элементв心附近即можно
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        
        action.move_to_element_with_offset(element, offset_x, offset_y)
        action.perform()
        
        # 2. Зависание (время раздумий)
        time.sleep(random.uniform(0.1, 0.4))
        
        # 3. клик (имитация задержки между нажатием и отпусканием)
        action.click_and_hold().pause(random.uniform(0.05, 0.15)).release().perform()
        
    except Exception as e:
        # Если ActionChains не вышел — обычный клик
        print(f"⚠️ Эмуляция мыши не удалась, обычный клик: {e}")
        try:
            element.click()
        except:
            driver.execute_script("arguments[0].click();", element)


def run():
    # 导入конфиг и утилита
    import os
    from config import REGION_CURRENT, DEVICE_TYPE
    from helpers.utils import (
        get_user_agent_for_region, get_locale_for_region,
        get_timezone_for_region, get_accept_language_for_region, is_mobile
    )
    from services.outlook_service import get_verification_code_from_outlook
    from managers.proxy_manager import proxy_manager
    
    # === использование智识别 Регион(если есть)===
    detected_region = os.environ.get('AUTO_REGION', REGION_CURRENT)
    
    # обновлениемногоЯзыквыбор→正 Регион
    lang_selector.update_region(detected_region)
    
    # показатьТекущие настройки окружения（использованиеобнаружено Регион）
    device_emoji = "📱" if is_mobile() else "💻"
    print(f"\n{device_emoji} === Текущие настройки окружения ===")
    print(f"📍 Регион: {detected_region.upper()}")
    print(f"🖥️  Устройство: {DEVICE_TYPE.upper()}")
    print(f"🌐 Язык: {get_locale_for_region(detected_region)}")
    print(f"🕐 Таймзона: {get_timezone_for_region(detected_region)}")
    lang_selector.print_current_language()
    proxy_manager.print_proxy_info()
    print("=" * 50)
    
    # получитьПрокси（если启 ）- 带тестпроверка
    proxy_url = None
    if proxy_manager.use_proxy:
        max_proxy_attempts = 3
        for proxy_attempt in range(max_proxy_attempts):
            proxy_url = proxy_manager.get_proxy()
            if not proxy_url:
                print("⚠️  Проксиполучитьнеудача")
                continue
            
            # тестПроксилидоступный
            print("🔍 тестПроксисоединение...")
            try:
                import requests
                proxies = {'http': proxy_url, 'https': proxy_url}
                test_resp = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
                if test_resp.status_code == 200:
                    print(f"✅ Прокситестчерез，出口IP: {test_resp.json().get('origin', 'Unknown')}")
                    break
                else:
                    print(f"⚠️  Прокситестнеудача (HTTP {test_resp.status_code})，ретрай...")
                    proxy_url = None
            except Exception as e:
                print(f"⚠️  Прокситестнеудача: {e}，ретрай...")
                proxy_url = None
        
        if not proxy_url:
            print("❌ всеПроксипопытканеудача，выход运строка")
            print("=" * 50)
            return  # 直выход，не允нетПрокси运строка
        print("=" * 50)
    
    # Создаём временный ящик
    print("📧 Создание временного ящика...")
    email_address, jwt_token = create_temp_email()
    if not email_address:
        print("Не удалось создать ящик，выход")
        return

    # Настройки Chrome — усиленная изоляция
    options = uc.ChromeOptions()
    
    # Базовые опции
    if HEADLESS:
        options.add_argument('--headless=new')
    
    # 移动Устройство殊настройка
    if is_mobile():
        # 移动Устройство视口
        options.add_argument('--window-size=375,812')  # iPhone 尺寸
        # Эмуляция touch
        options.add_argument('--touch-events=enabled')
    else:
        # Случайный размер окна — имитация разных мониторов
        common_resolutions = [
            "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720"
        ]
        chosen_res = random.choice(common_resolutions)
        options.add_argument(f'--window-size={chosen_res}')
        options.add_argument('--start-maximized')
    
    # случайный User-Agent   Sec-Ch-Ua (Chrome定)
    # options.add_argument(f'--sec-ch-ua-platform="{random.choice(["Windows", "macOS", "Linux"])}"')

    # Регионокружениенастройка（использованиеобнаружено Регион）
    
    # Регионокружениенастройка（использованиеобнаружено Регион）
    options.add_argument(f'--lang={get_locale_for_region(detected_region)}')
    options.add_argument(f'--accept-lang={get_accept_language_for_region(detected_region)}')
    
    # Усиленный anti-detect
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    
    # WebGL  и  Canvas fingerprint
    options.add_argument('--enable-webgl')
    options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
    
    # Аудио
    options.add_argument('--autoplay-policy=no-user-gesture-required')
    
    # === Усиленная приватность ===
    # Запрет утечки локального IP через WebRTC
    options.add_argument('--force-webrtc-ip-handling-policy=default_public_interface_only')
    options.add_argument('--disable-features=WebRtcHideLocalIpsWithMdns')

    
    # User-Agent（использованиеобнаружено Регион）
    user_agent = get_user_agent_for_region(detected_region)
    options.add_argument(f'--user-agent={user_agent}')
    print(f"User-Agent: {user_agent[:80]}...")
    
    # Проксинастройка - использование动получить Прокси
    if proxy_url:
        options.add_argument(f'--proxy-server={proxy_url}')
        print(f"✅ Проксиуже 应 →браузер")

    
    # Запуск браузера
    
    # Создаю изолированный временный профиль，без остатков Cookie/Cache
    try:
        driver = None
        for attempt in range(3):
            try:
                driver = uc.Chrome(options=options, version_main=148)
                break
            except Exception as e:
                print(f"  попытка {attempt+1}/3: {e}")
                time.sleep(2)
        if not driver:
            print("❌ Не удалось запустить Chrome")
            return
        wait = WebDriverWait(driver, 30)
        
        # === Инъекция фейк-fingerprint (CPU核心число/внутри存) ===
        # разнобой конфигов чтобы не палиться
        cores = random.choice([4, 8, 12, 16])
        memory = random.choice([4, 8, 16, 32])
        
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": f"""
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {cores}
                }});
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: () => {memory}
                }});
                // 试图干扰 Canvas чтение→  GPU информация (не证 100% есть效ноувеличить干扰)
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    // 37445 是 UNMASKED_VENDOR_WEBGL
                    // 37446 是 UNMASKED_RENDERER_WEBGL
                    if (parameter === 37445) {{
                        return 'Intel Inc.';
                    }}
                    if (parameter === 37446) {{
                        return 'Intel Iris OpenGL Engine';
                    }}
                    return getParameter(parameter);
                }};
            """
        })
        
        # ... (后续代 код)
        
    except Exception as e:
        print(f"❌ Браузер не запустился: {e}")
        return

    # === инъекцияРандомизация fingerprintскрипт (暂когда禁 以排проверка问题) ===
    # print("🎭 инъекцияРандомизация fingerprint...")
    # from fingerprint import fingerprint_randomizer
    # fingerprint_randomizer.inject_to_driver(driver)
    
    # настройкаТаймзона（использованиеобнаружено Регион）
    try:
        driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
            'timezoneId': get_timezone_for_region(detected_region)
        })
        print(f"Таймзона установлена: {get_timezone_for_region(detected_region)}")
    except Exception as e:
        print(f"Не удалось задать таймзону (не критично): {e}")
    
    # настройкагеолокация权限（использованиеобнаружено Регион）
    try:
        # 各Регион большой致坐标
        geo_locations = {
            'germany': {'latitude': 52.52, 'longitude': 13.405, 'accuracy': 100},
            'japan': {'latitude': 35.6762, 'longitude': 139.6503, 'accuracy': 100},
            'usa': {'latitude': 40.7128, 'longitude': -74.0060, 'accuracy': 100}
        }
        location = geo_locations.get(detected_region, geo_locations['usa'])
        driver.execute_cdp_cmd('Emulation.setGeolocationOverride', location)
        print(f"Геолокация установлена")
    except Exception as e:
        print(f"Не удалось задать геолокацию (не критично): {e}")

    try:
        # Шаг 2: открыть страницу AWS Builder
        print("\nОткрываю страницу AWS Builder...")
        driver.get("https://builder.aws.com/start")
        human_delay(2, 3)
        print(f"Заголовок страницы: {driver.title}")

        # обработкаCookieвсплывающее окно（必须先закрыть，否则会遮挡элемент）
        print("Проверяю Cookie-баннер...")
        human_delay(3, 4)  # 给足когда间让всплывающее окнозагрузка
        
        cookie_closed = False
        
        # попыткамногометодзакрытьCookieвсплывающее окно
        try:
            # метод1: прямой поискAcceptкнопка（самый частый）
            accept_selectors = [
                "//button[text()='Accept']",
                "//button[contains(text(), 'Accept')]",
                "//button[@id='awsccc-cb-btn-accept']",
                "//button[contains(@class, 'awsccc')]",
                "//div[@id='awsccc-cs-modalcontent']//button[1]",  # Cookieвсплывающее окно 第одинкнопка
                "//button[contains(@class, 'primary')]",
            ]
            
            for selector in accept_selectors:
                try:
                    cookie_btn = driver.find_element(By.XPATH, selector)
                    if cookie_btn and cookie_btn.is_displayed():
                        print(f"   Нашёл Cookie-кнопку, кликаю...")
                        # прокрутка→底（因какcookieвсплывающее окно在底）
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        human_delay(1, 1.5)
                        
                        # подсветитьпоказатькнопка（отладка ）
                        human_delay(0.5, 1)
                        
                        # 强制клик
                        human_click(driver, cookie_btn)
                        print("✅ Cookie-баннер закрыт!")
                        cookie_closed = True
                        human_delay(2, 3)  # ожиданиевсплывающее окно消失
                        break
                except:
                    continue
            
            # метод2: Пробую нажать ESCзакрыть
            if not cookie_closed:
                print("   Пробую нажать ESC...")
                from selenium.webdriver.common.keys import Keys
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                human_delay(1, 2)
            
        except Exception as e:
            print(f"   Ошибка обработки Cookie: {e}")
        
        if cookie_closed:
            print("   Cookie-баннер обработан")
        else:
            print("   ⚠️  Не удалось закрыть Cookie-баннер, продолжаю...")
        
        # клик Sign up with Builder ID
        print("Кликаю Sign up with Builder ID...")
        human_delay(4, 6)  # увеличитьвремя ожидания，обеспечитьстраницазагрузка
        
        signup_clicked = False
        original_url = driver.current_url
        
        # попыткапоисксодержит关键текст всеэлемент (самыймногоретрай3次)
        for scan_attempt in range(3):
            if signup_clicked:
                break
                
            if scan_attempt > 0:
                print(f"   🔄 ретрай扫描 ({scan_attempt + 1}/3)...")
                human_delay(3, 5)
        
            try:
                print("   🔍 Сканирую элементы страницы...")
                # поиск任何содержит "Sign up with Builder ID" или "Builder-ID"  видимыйэлемент
                # 注：текствозможно在子элемент(如span)в，поэтому  .// 来搜索后代текст
                key_texts = ["Sign up with Builder ID", "Mit Builder-ID anmelden", "Builder ID", "Builder-ID"]
                
                found_elements = []
                for text in key_texts:
                    # 先找精содержиттекст  span элемент
                    xpath = f"//span[contains(text(), '{text}')]"
                    elements = driver.find_elements(By.XPATH, xpath)
                    for el in elements:
                        if el.is_displayed():
                            found_elements.append(el)
                    
                    # ещё找任элемент（包括后代текст）
                    if not found_elements:
                        xpath = f"//*[contains(., '{text}')]"
                        elements = driver.find_elements(By.XPATH, xpath)
                        for el in elements:
                            if el.is_displayed() and el.tag_name in ['a', 'button', 'span', 'div']:
                                found_elements.append(el)
                
                print(f"   Найдено {len(found_elements)} релевантных элементов")
                
                for i, element in enumerate(found_elements):
                    try:
                        # получитьэлемент 标签 и текст
                        tag_name = element.tag_name
                        text_content = element.text
                        print(f"   элемент {i+1}: <{tag_name}> '{text_content[:20]}...'")
                        
                        # еслиэлементсам являетсяссылкаиликнопка，прямой клик
                        target_element = element
                        
                        # еслине是，попытка向上поискродительссылкаиликнопка (самыймного5)
                        if tag_name not in ['a', 'button']:
                            parent = element
                            for _ in range(5):
                                try:
                                    parent = parent.find_element(By.XPATH, "./..")
                                    if parent.tag_name in ['a', 'button'] or parent.get_attribute('role') in ['button', 'link']:
                                        target_element = parent
                                        print(f"      Найденородителькликабельныйэлемент: <{parent.tag_name}>")
                                        break
                                except:
                                    break
                        
                        
                        # Пробую кликнуть
                        print(f"      👉 Пробую кликнуть...")
                        
                        # 优先использование JS клик (самый强力)
                        human_click(driver, target_element)
                        human_delay(2, 3)
                        
                        if driver.current_url != original_url:
                            print(f"✅ Перешли на: {driver.current_url}")
                            signup_clicked = True
                            break
                        
                        # еслиJSклик没反应，попытка ActionChains
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(driver).move_to_element(target_element).click().perform()
                        human_delay(2, 3)
                        
                        if driver.current_url != original_url:
                            print(f"✅ Перешли на: {driver.current_url}")
                            signup_clicked = True
                            break
                            
                    except Exception as e:
                        print(f"      попытка клика провалена: {e}")
                        continue
                    
                    if signup_clicked:
                        break
                        
            except Exception as e:
                print(f"   扫描элементкогданеудача: {e}")

        # если上面 智扫描неудача，попыткапоследний 硬编 код备选
        if not signup_clicked:
            print("⚠️  Умный поиск не сработал, пробую CSS...")
            try:
                # попыткасамый частый CSS名组合 (согласноAWSобычно规律)
                css_selectors = [
                    "a[href*='signup']",
                    "a[href*='register']",
                    ".lb-btn-primary",
                    "button[type='submit']"
                ]
                for css in css_selectors:
                    try:
                        els = driver.find_elements(By.CSS_SELECTOR, css)
                        for el in els:
                            if el.is_displayed() and "Builder ID" in el.text:
                                human_click(driver, el)
                                human_delay(2, 3)
                                if driver.current_url != original_url:
                                    signup_clicked = True
                                    break
                        if signup_clicked: break
                    except: continue
            except: pass

        if not signup_clicked:
            print("❌ Критическая неудача: не могу войти в форму регистрации")
            # это里неиспользование备 URL，因какпользовательобратная связь备 案невалидный
            pass
        
        print(f"Текущий URL: {driver.current_url}")
        
        # 截图

        # Шаг 3: ввод email (с ретраями)
        print(f"Ввожу email: {email_address}")
        
        def safe_input(selector, value, max_retries=3):
            """安ввод函число，обработкаstale element"""
            for attempt in range(max_retries):
                try:
                    element = wait.until(EC.presence_of_element_located(selector))
                    element.click()
                    human_delay(0.3, 0.8)
                    element.clear()
                    human_type(element, value)
                    return True
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"   Повтор ввода {attempt + 1}/{max_retries}...")
                        human_delay(1, 2)
                    else:
                        raise e
            return False
        
        safe_input((By.CSS_SELECTOR, 'input[placeholder="username@example.com"]'), email_address)
        print("Email введён")

        # кликпродолжитькнопка
        human_delay(1, 2)
        print("Кликаю Continue...")
        continue_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="test-primary-button"]'))
        )
        continue_btn.click()

        # ожидание姓名страницазагрузка
        human_delay(3, 5)
        print(f"Текущий URL: {driver.current_url}")

        # Шаг 4: ввод имени (с ретраями)
        random_name = fake.name()
        print(f"Ввожу имя: {random_name}")
        
        # увеличить一случайныйстрокакак
        driver.execute_script("window.scrollBy(0, 10)")
        human_delay(0.5, 1)
        
        # болееможно靠 姓名ввод
        name_input_success = False
        for name_attempt in range(3):
            try:
                # ожиданиеввод框出现
                name_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]')))
                
                # кликввод框получить焦
                name_input.click()
                human_delay(0.3, 0.5)
                
                # использование Ctrl+A 选затем删除， clear() болееможно靠
                from selenium.webdriver.common.keys import Keys
                name_input.send_keys(Keys.CONTROL + "a")
                human_delay(0.1, 0.2)
                name_input.send_keys(Keys.DELETE)
                human_delay(0.2, 0.4)
                
                # ввод姓名
                human_type(name_input, random_name)
                human_delay(0.5, 1)
                
                # проверкавводлиуспех
                actual_value = name_input.get_attribute('value')
                if actual_value and len(actual_value) > 0:
                    print(f"   Проверка ввода: '{actual_value}'")
                    name_input_success = True
                    break
                else:
                    print(f"   Проверка вводанеудача，ретрай...")
                    
            except Exception as e:
                print(f"   Повтор ввода имени {name_attempt + 1}/3: {e}")
                human_delay(1, 2)
        
        if not name_input_success:
            print("⚠️ ввод имени, возможно неудача，продолжаю попытки...")

        print("Имя введено")

        # кликпродолжить (многоЯзык兼容) - 带неудачапроверка и много次ретрай
        max_continue_attempts = 5  # увеличить→5次ретрай
        page_changed = False
        original_url = driver.current_url
        
        for continue_attempt in range(max_continue_attempts):
            human_delay(1, 2)
            print(f"Кликаю Continue... (попытка {continue_attempt + 1}/{max_continue_attempts})")
            
            try:
                # Пробую разные способы найти Continue
                continue_btn = None
                continue_selectors = [
                    lang_selector.get_by_xpath('continue', 'button'),
                    (By.XPATH, "//button[contains(., 'Continue')]"),
                    (By.XPATH, "//button[contains(., 'продолжить')]"),
                    (By.XPATH, "//button[@type='submit']"),
                    (By.CSS_SELECTOR, '[data-testid="test-primary-button"]'),
                ]
                
                for selector in continue_selectors:
                    try:
                        continue_btn = driver.find_element(*selector)
                        if continue_btn and continue_btn.is_displayed():
                            break
                    except:
                        continue
                
                if continue_btn:
                    # прокрутка→кнопкаобеспечитьвидимый
                    driver.execute_script("arguments[0].scrollIntoView(true);", continue_btn)
                    human_delay(0.3, 0.5)
                    
                    # Пробую разные способы клика
                    try:
                        human_click(driver, continue_btn)
                    except:
                        driver.execute_script("arguments[0].click();", continue_btn)
                else:
                    print("   ⚠️ Continue не найдена")
                    continue
                    
            except Exception as e:
                print(f"   неудача клика: {e}")
                continue
            
            # жду ответ страницы (稍微длинный一)
            human_delay(3, 5)
            
            # 检страницалиуже 跳转 (URLилизаголовок)
            current_url = driver.current_url
            if current_url != original_url or 'verification' in current_url.lower() or 'code' in driver.title.lower():
                print(f"   ✅ Страница перешла")
                page_changed = True
                break
            
            # проверкалиестьнеудачавсплывающее окно/подсказка
            error_found = False
            try:
                # более полная проверка ошибок
                error_selectors = [
                    "//*[contains(text(), 'error processing')]",
                    "//*[contains(text(), 'Error')]",
                    "//*[contains(text(), 'try again')]",
                    "//*[contains(text(), 'Sorry')]",
                    "//*[contains(@class, 'error')]",
                    "//*[contains(@class, 'alert')]",
                    "//div[contains(@role, 'alert')]",
                ]
                
                for error_xpath in error_selectors:
                    try:
                        error_elements = driver.find_elements(By.XPATH, error_xpath)
                        for el in error_elements:
                            if el.is_displayed():
                                error_text = el.text.strip()
                                if error_text and len(error_text) > 5:
                                    # отсеять не-ошибочный текст
                                    if 'required' not in error_text.lower():
                                        error_found = True
                                        print(f"   ⚠️ обнаружена неудача: {error_text[:60]}...")
                                        break
                        if error_found:
                            break
                    except:
                        continue
                
                if error_found:
                    # Пробую закрыть окно ошибки
                    try:
                        close_selectors = [
                            "//button[contains(@aria-label, 'close')]",
                            "//button[contains(@class, 'close')]",
                            "//button[text()='×']",
                            "//button[text()='OK']",
                            "//button[text()='定']",
                        ]
                        for close_xpath in close_selectors:
                            try:
                                close_btn = driver.find_element(By.XPATH, close_xpath)
                                if close_btn.is_displayed():
                                    close_btn.click()
                                    human_delay(1, 2)
                                    break
                            except:
                                continue
                    except:
                        pass
                    
                    # нажать ESC попытказакрыть
                    try:
                        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        human_delay(1, 2)
                    except:
                        pass
                    
                    print(f"   🔄 ожидание и retry...")
                    human_delay(2, 4)  # неудача后ожиданиеболеедлинныйкогда间
                    continue
                    
            except Exception as e:
                pass
            
            # если没естьнеудача也没есть跳转，возможнонужноещё一次
            if not error_found and not page_changed:
                print(f"   страница не изменилась，новая попытка...")
                human_delay(1, 2)
        
        if not page_changed:
            print("⚠️ после нескольких попыток страница не перешла，продолжить执строка...")
        
        print(f"Заголовок страницы: {driver.title}")

        # Шаг 5：ожидание并получитькод подтверждения (优先получить，因каквозможностраница还没загрузкакод подтверждения来了)
        print("Жду письмо с кодом...")
        human_delay(3, 5) # 给страница一загрузкакогда间
        
        # увеличить对 JSON разборнеудача 护
        try:
            # 此когдастраницадолжен在求Проверка ввода код
            from services.email_service import wait_for_verification_email
            verification_code = wait_for_verification_email(jwt_token)
        except Exception as e:
            print(f"⚠️  получитькод подтверждениявнеудача: {e}")
            verification_code = None

        if verification_code:
            print(f"Получен код: {verification_code}")

            # заполнитькод подтверждения
            try:
                print("Ищу поле ввода кода...")
                # увеличитьболеедлинный ожидание，обеспечитьстраницауже 稳定загрузка
                # Проксиокружение下，страницавозможно还在疯狂загрузка资源
                human_delay(4, 6)
                
                # ожиданиеввод框出现можно互
                code_input = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder*="digit"], input[type="text"]'))
                )
                
                # ещёи т.д.немного，防止кликкогдаввод框跳动
                human_delay(1, 2)
                code_input.click()
                human_delay(0.5, 1)
                
                human_type(code_input, verification_code)
                print("Код введён")
                
                # заполнить后ещёи т.д.немного
                human_delay(1.5, 2.5)
                
                # кликпроверка/продолжить
                # пользовательобратная связьэто里на самом деле это“продолжить”кнопка，не是 Verify
                verify_clicked = False
                verify_selectors = [
                   "//button[contains(., 'Verify')]", 
                   "//button[contains(., 'Continue')]",  # увеличить Continue
                   "//button[contains(., 'продолжить')]",
                   "//button[@type='submit']"
                ]
                
                print("Ищу Verify/Continue кнопку...")
                for xpath in verify_selectors:
                    try:
                        verify_btn = driver.find_element(By.XPATH, xpath)
                        if verify_btn.is_displayed():
                            # прокрутка→кнопка并подсветить
                            driver.execute_script("arguments[0].scrollIntoView(true);", verify_btn)
                            human_delay(0.5, 1)
                            driver.execute_script("arguments[0].click();", verify_btn)
                            verify_clicked = True
                            print(f"Кнопка нажата (xpath: {xpath})")
                            break
                    except: continue
                
                if not verify_clicked:
                    print("⚠️  не найденоявный кнопка，попытка按Enter")
                    from selenium.webdriver.common.keys import Keys
                    code_input.send_keys(Keys.ENTER)
                
                # клик后ожидание足длинный когда间让страница跳转
                print("Жду переход страницы (из-за прокси возможна задержка)...")
                human_delay(8, 12)

            except Exception as e:
                    print(f"⚠️  заполнитькод подтверждениянеудача: {e}")
        else:
            print("❌ Код не получен")

        # Шаг 6：настройка密 код
        print("Готовлюсь задать пароль...")
        human_delay(5, 8)  # ожиданиепроверкачерез后 跳转
        print(f"Текущая страница: {driver.current_url}")
        
        password = generate_strong_password()
        print(f"Сгенерированный пароль: {password}")

        # заполнить密 код
        try:
            # поискстраница上все 密 кодввод框
            password_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
            
            if len(password_inputs) >= 1:
                print(f"Найдено {len(password_inputs)} полей пароля")
                
                # заполнить第один密 код框 (密 код)
                human_delay(0.5, 1)
                password_inputs[0].click()
                human_type(password_inputs[0], password)
                print("Основной пароль введён")
                
                # еслиесть第二 ，заполнить第二  (认密 код)
                if len(password_inputs) >= 2:
                    human_delay(0.5, 1)
                    password_inputs[1].click()
                    human_type(password_inputs[1], password)
                    print("Подтверждение пароля введено")
                # если не найдено第二 нопользователь说есть两 ，попыткаонпоиск
                else: 
                     try:
                        confirm_selectors = [
                            'input[name="confirmPassword"]',
                            'input[placeholder="Confirm password"]', 
                            'input[placeholder="Re-enter password"]',
                            'input[id*="confirm"]'
                        ]
                        for sel in confirm_selectors:
                            try:
                                confirm_input = driver.find_element(By.CSS_SELECTOR, sel)
                                if confirm_input.is_displayed() and confirm_input != password_inputs[0]:
                                    human_delay(0.5, 1)
                                    confirm_input.click()
                                    human_type(confirm_input, password)
                                    print("Подтверждение пароля введено (через резервный селектор)")
                                    break
                            except: continue
                     except: pass
                
                
                # Кликаю Create/Continue
                human_delay(1, 2)
                print("Кликаю Continue/Создать аккаунт...")
                
                # поисккнопку Submit
                submit_selectors = [
                    "//button[contains(., 'Create AWS Builder ID')]",
                    "//button[contains(., 'Continue')]",
                    "//button[@type='submit']"
                ]
                
                for xpath in submit_selectors:
                    try:
                        btn = driver.find_element(By.XPATH, xpath)
                        if btn.is_displayed():
                            human_click(driver, btn)
                            break
                    except: continue
                    
            else:
                print("⚠️  Поле пароля не найдено，возможно уже авторизован или другой флоу")
        
        except Exception as e:
            print(f"⚠️  Ошибка на этапе пароля: {e}")

        # Ждём финальную страницу
        human_delay(5, 8)
        final_url = driver.current_url
        final_title = driver.title
        print(f"Финальная страница: {final_title}")
        print(f"Финальный URL: {final_url}")

        # Проверка успеха: URL ушёл с /signup/, /verify-otp
        failure_markers = ['/signup/', '/verify-otp', '/login', '/error']
        is_failed = any(marker in final_url for marker in failure_markers)

        if is_failed:
            print(f"❌ РЕГИСТРАЦИЯ НЕ ЗАВЕРШЕНА — застряли на: {final_url}")
            save_account_failed(email_address, password, random_name, jwt_token, reason=f"stuck at {final_url}")
            print("⚠️  Записано в accounts_failed.jsonl для отладки")
        else:
            save_account(email_address, password, random_name, jwt_token)
            print("")
            print(f"✅ Аккаунт успешно зарегистрирован: {email_address}")

    except Exception as e:
        print(f"❌ Ошибка в процессе: {e}")
        try:
            if 'email_address' in locals() and 'password' in locals():
                save_account_failed(
                    email_address,
                    password,
                    random_name if 'random_name' in locals() else "Unknown",
                    jwt_token if 'jwt_token' in locals() else "",
                    reason=f"exception: {e}"
                )
                print("⚠️  Информация записана в accounts_failed.jsonl")
        except: pass

    finally:
        # Финальный exit — защита от WinError 6
        try:
            if 'driver' in locals() and driver:
                # 1. Нормальный выход
                try:
                    driver.quit()
                except: pass
                
                # 2. Ключевой фикс — глушим quit
                # это样когда垃圾调  __del__ -> self.quit() когда，что都не会生
                driver.quit = lambda: None
                
                # 3. 清子процесс引  (双重险)
                try:
                    if hasattr(driver, 'service') and driver.service.process:
                        driver.service.process = None
                except: pass
        except: pass
                


if __name__ == "__main__":
    run()



