#!/usr/bin/env python3
"""отладкаскрипт - просмотрстраницаэлемент"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

def debug_page():
    print("🔍 запускотладкабраузер...")
    
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = uc.Chrome(options=options)
    
    try:
        print("📄 开 AWS Builder страница...")
        driver.get("https://builder.aws.com/start")
        time.sleep(5)
        
        print(f"\nЗаголовок страницы: {driver.title}")
        print(f"страницаURL: {driver.current_url}")
        
        # поисквсекнопка
        print("\n=== всекнопка ===")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, btn in enumerate(buttons[:10]):
            text = btn.text.strip()[:50] if btn.text else "(неттекст)"
            print(f"  [{i}] {text}")
        
        # поисквсессылка
        print("\n=== всессылка ===")
        links = driver.find_elements(By.TAG_NAME, "a")
        for i, link in enumerate(links[:15]):
            text = link.text.strip()[:50] if link.text else "(неттекст)"
            href = link.get_attribute("href") or ""
            print(f"  [{i}] {text} -> {href[:60]}")
        
        # поисксодержит sign/register/builder  элемент
        print("\n=== 关键词элемент ===")
        keywords = ["sign", "register", "builder", "create", "start"]
        for kw in keywords:
            els = driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{kw}')]")
            if els:
                print(f"  '{kw}': Найдено {len(els)}  ")
                for el in els[:3]:
                    print(f"    - <{el.tag_name}> {el.text[:40]}")
        
        print("\n⏸️  браузер持开，按 Ctrl+C закрыть...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nзакрытьбраузер...")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_page()
