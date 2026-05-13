#!/usr/bin/env python3
"""
fingerprintпроверкатест
доступfingerprintпроверка网站，проверкаслучайный效果
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from fingerprint import fingerprint_randomizer
import time

def test_fingerprint():
    """тестРандомизация fingerprint效果"""
    
    print("=" * 70)
    print("🎭 браузерРандомизация fingerprintтест")
    print("=" * 70)
    
    # конфигбраузер
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    
    # Запуск браузера
    print("\n🚀 Запуск браузера...")
    driver = uc.Chrome(options=options)
    
    # инъекцияРандомизация fingerprint
    print("🎭 инъекцияРандомизация fingerprintскрипт...")
    fingerprint_randomizer.inject_to_driver(driver)
    
    # тест网站список
    test_sites = [
        {
            'name': 'BrowserLeaks - Canvas',
            'url': 'https://browserleaks.com/canvas',
            'desc': 'тестCanvasfingerprint'
        },
        {
            'name': 'BrowserLeaks - WebGL',
            'url': 'https://browserleaks.com/webgl',
            'desc': 'тестWebGLfingerprint'
        },
        {
            'name': 'CreepJS',
            'url': 'https://abrahamjuliot.github.io/creepjs/',
            'desc': '综合fingerprintпроверка'
        }
    ]
    
    print("\n📊 将доступнижеfingerprintпроверка网站:")
    for i, site in enumerate(test_sites, 1):
        print(f"   {i}. {site['name']} - {site['desc']}")
    
    choice = input("\nвыбордоступ 网站 (1-3, или按Enterдоступ第1 ): ").strip() or "1"
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(test_sites):
            site = test_sites[idx]
            print(f"\n🔗 开: {site['name']}")
            print(f"   URL: {site['url']}")
            
            driver.get(site['url'])
            print("\n✅ страницауже загрузка")
            print("📝 请在браузервпросмотрfingerprintпроверкарезультат")
            print("   注：次运строка都会генерацияне同 fingerprint！")
            
            input("\n按Enter键закрытьбраузер...")
        else:
            print("❌ невалидныйвыбор")
    except ValueError:
        print("❌ невалидныйввод")
    except Exception as e:
        print(f"❌ 生неудача: {e}")
    finally:
        driver.quit()
        print("\n✅ тест成")


if __name__ == "__main__":
    test_fingerprint()
