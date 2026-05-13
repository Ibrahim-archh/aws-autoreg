#!/usr/bin/env python3
"""
智запускскрипт
автосогласноПроксиIP геолокацияконфигокружение
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.proxy_manager import proxy_manager
from helpers.multilang import lang_selector

def auto_configure_environment():
    """согласноПроксиIPавтоконфигокружение"""
    
    print("\n" + "=" * 60)
    print("🤖 智окружениеконфиг")  
    print("=" * 60)
    
    # получитьПрокси
    proxy_url = None
    proxy_region = "usa"  # по умолчаниюРегион
    
    if proxy_manager.use_proxy:
        print("\n🔄 получитьПроксив...")
        proxy_url = proxy_manager.get_proxy()
        
        if not proxy_url:
            print("⚠️  Проксиполучитьнеудача，использованиепо умолчанию美国окружение")
        elif proxy_manager.proxy_location:
            # использованиеПроксиIP геолокация
            proxy_region = proxy_manager.proxy_location.get('region', 'usa')
            country = proxy_manager.proxy_location.get('country', 'Unknown')
            
            print(f"\n📍 обнаруженоПроксиIPпозиция:")
            print(f"   страна: {country}")
            print(f"   автоконфигокружение: {proxy_region.upper()}")
    else:
        print("\n⚠️  Проксивыключен，использованиепо умолчанию美国окружение")
    
    # обновлениемногоЯзыквыбор
    lang_selector.update_region(proxy_region)
    
    print("\n✅ окружениеконфиг成!")
    print(f"   Регион: {proxy_region.upper()}")
    lang_selector.print_current_language()
    
    print("=" * 60)
    print("\n🚀 запуск主序...\n")
    
    # 存конфиг→переменная окружения，供main.pyиспользование
    import os
    os.environ['AUTO_REGION'] = proxy_region
    
    # 导入并运строка主序
    from runners.main import run
    run()


if __name__ == "__main__":
    try:
        auto_configure_environment()
    except KeyboardInterrupt:
        print("\n\n⚠️  пользовательв")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 生неудача: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
