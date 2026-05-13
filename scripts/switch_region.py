#!/usr/bin/env python3
"""
Регионпереключениеутилита
быстро速переключениене同Регион окружениеконфиг
"""

import yaml
import sys
from pathlib import Path


def switch_region(region: str):
    """переключениеРегионконфиг"""
    valid_regions = ['germany', 'japan', 'usa']
    
    if region not in valid_regions:
        print(f"❌ невалидный Регион: {region}")
        print(f"✅ доступныйРегион: {', '.join(valid_regions)}")
        return False
    
    config_path = Path(__file__).parent / "config.yaml"
    
    # чтениеконфиг
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # обновлениеРегион
    old_region = config['region']['current']
    config['region']['current'] = region
    
    # 存конфиг
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Регионуже переключение: {old_region} -> {region}")
    
    # показатьтекущийконфиг
    profile = config['region']['profiles'][region]
    print(f"\n📍 текущийРегионконфиг:")
    print(f"  Язык: {profile['locale']}")
    print(f"  Таймзона: {profile['timezone']}")
    print(f"  Accept-Language: {profile['accept_language']}")
    print(f"  User-Agent количество: {len(profile['user_agents'])}")
    
    return True


def show_current():
    """показатьтекущийРегионконфиг"""
    config_path = Path(__file__).parent / "config.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    current = config['region']['current']
    profile = config['region']['profiles'][current]
    
    print(f"📍 текущийРегион: {current.upper()}")
    print(f"  Язык: {profile['locale']}")
    print(f"  Таймзона: {profile['timezone']}")
    print(f"  Accept-Language: {profile['accept_language']}")
    print(f"  Прокси: {'включён' if config['region'].get('use_proxy') else 'выключен'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(" :")
        print("  просмотртекущийконфиг: python switch_region.py show")
        print("  переключениеРегион: python switch_region.py [germany|japan|usa]")
        print()
        show_current()
    elif sys.argv[1] == "show":
        show_current()
    else:
        switch_region(sys.argv[1].lower())
