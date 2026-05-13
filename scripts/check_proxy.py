#!/usr/bin/env python3
"""
ПроксиAPIтестутилита
тестПроксиAPIли正常工
"""

from proxy_manager import proxy_manager

print("=" * 60)
print("ПроксиAPIтест")
print("=" * 60)

# показатьтекущийконфиг
print("\n📋 текущийконфиг:")
print(f"   Прокси启 : {proxy_manager.use_proxy}")
print(f"   Прокси模: {proxy_manager.proxy_mode}")

if proxy_manager.use_proxy:
    print("\n" + "-" * 60)
    
    # получитьПрокси
    proxy_url = proxy_manager.get_proxy()
    
    if proxy_url:
        print(f"\n✅ Проксиполучитьуспех!")
        print(f"   полныйURL: {proxy_url}")
        
        # тестПрокси
        print("\n" + "-" * 60)
        is_working = proxy_manager.test_proxy()
        
        if is_working:
            print("\n🎉 Прокситестчерез，можно以正常использование！")
        else:
            print("\n❌ Прокситестнеудача，请检Проксинастройка")
    else:
        print("\n❌ Проксиполучитьнеудача")
        print("   请检:")
        print("   1. API URL ли正")
        print("   2. API密钥лиесть效")
        print("   3. сетьсоединениели正常")
else:
    print("\n⚠️  Проксивыключен")
    print("   如需启 ，请修改 config.yaml в  use_proxy как true")

print("\n" + "=" * 60)
