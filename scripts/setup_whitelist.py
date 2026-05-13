#!/usr/bin/env python3
"""
Проксибелый список手动конфигутилита
длятест и конфигбелый список参число
"""

import requests
import sys


def test_whitelist_api():
    """тестбелый списокAPI не同参число组合"""
    
    print("=" * 70)
    print("Проксибелый списокAPIтестутилита")
    print("=" * 70)
    
    # получитьтекущийIP
    print("\n1️⃣  получитьтекущий公网IP...")
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text.strip()
        print(f"   ✅ текущийIP: {ip}")
    except:
        print("   ⚠️  получитьIPнеудача")
        ip = input("   请手动вводты 公网IP: ").strip()
    
    # вводAPI Key
    print("\n2️⃣  вводAPIконфиг:")
    key = input("   API Key: ").strip()
    if not key:
        print("   ❌ API Key некакпусто")
        return False
    brand = input("   Brand (по умолчанию: 2): ").strip() or "2"
    
    # тестне同 API调 
    print("\n3️⃣  началотестAPI...")
    print("-" * 70)
    
    # тест1: неиспользованиеsign
    print("\n📝 тест1: неиспользованиеsign参число")
    url1 = f"http://your-proxy-api.com/white/add?key={key}&brand={brand}&ip={ip}"
    print(f"   URL: {url1}")
    try:
        resp = requests.get(url1, timeout=10)
        print(f"   статус код: {resp.status_code}")
        print(f"   ответ: {resp.text[:200]}")
        if resp.status_code == 200:
            print("   ✅ успех!")
            return True
    except Exception as e:
        print(f"   ❌ неудача: {e}")
    
    # тест2: использованиепустоsign
    print("\n📝 тест2: использованиепустоsign参число")
    url2 = f"http://your-proxy-api.com/white/add?key={key}&brand={brand}&sign=&ip={ip}"
    print(f"   URL: {url2}")
    try:
        resp = requests.get(url2, timeout=10)
        print(f"   статус код: {resp.status_code}")
        print(f"   ответ: {resp.text[:200]}")
        if resp.status_code == 200:
            print("   ✅ успех!")
            return True
    except Exception as e:
        print(f"   ❌ неудача: {e}")
    
    # тест3: просмотрбелый список（ненужноIP参число）
    print("\n📝 тест3: просмотртекущийбелый список")
    url3 = f"http://your-proxy-api.com/white/fetch?key={key}&brand={brand}"
    print(f"   URL: {url3}")
    try:
        resp = requests.get(url3, timeout=10)
        print(f"   статус код: {resp.status_code}")
        print(f"   ответ: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ неудача: {e}")
    
    # тест4: не同 brand值
    print("\n📝 тест4: попыткаbrand=1")
    url4 = f"http://your-proxy-api.com/white/add?key={key}&brand=1&ip={ip}"
    print(f"   URL: {url4}")
    try:
        resp = requests.get(url4, timeout=10)
        print(f"   статус код: {resp.status_code}")
        print(f"   ответ: {resp.text[:200]}")
        if resp.status_code == 200:
            print("   ✅ успех!")
            return True
    except Exception as e:
        print(f"   ❌ неудача: {e}")
    
    print("\n" + "=" * 70)
    print("💡 建议:")
    print("   1. 检APIдокументацияв 正参число")
    print("   2. 认keyли正")
    print("   3. 联系Проксисервис商客服认белый списокAPI использованиеметод")
    print("=" * 70)
    
    return False


def manual_add():
    """手动добавитьIP→белый список"""
    print("\n" + "=" * 70)
    print("手动добавитьIP→белый список")
    print("=" * 70)
    
    url = input("\n请вводполный API URL: ").strip()
    
    if not url:
        print("❌ URLнекакпусто")
        return
    
    try:
        print(f"\n🔄 调 API...")
        print(f"   URL: {url}")
        
        resp = requests.get(url, timeout=10)
        print(f"\n📊 результат:")
        print(f"   статус код: {resp.status_code}")
        print(f"   ответсодержимое:")
        print(f"   {resp.text}")
        
        if resp.status_code == 200:
            print("\n✅ запросуспех！检上面 ответсодержимое认лидобавитьуспех")
        else:
            print(f"\n⚠️  запросвозвратстатус код {resp.status_code}")
    
    except Exception as e:
        print(f"\n❌ запроснеудача: {e}")


if __name__ == "__main__":
    print("\nвыбороперация:")
    print("1. автотестбелый списокAPI")
    print("2. 手动вводполныйURLтест")
    
    choice = input("\n请выбор (1/2, по умолчанию1): ").strip() or "1"
    
    if choice == "1":
        test_whitelist_api()
    elif choice == "2":
        manual_add()
    else:
        print("невалидныйвыбор")
