#!/usr/bin/env python3
"""
Устройствотиппереключениеутилита
быстро速在桌面 и 移动Устройство之间переключение
"""

import yaml
import sys
from pathlib import Path


def switch_device(device_type: str):
    """переключениеУстройствотип"""
    valid_devices = ['desktop', 'mobile']
    
    if device_type not in valid_devices:
        print(f"❌ невалидный Устройствотип: {device_type}")
        print(f"✅ доступныйтип: {', '.join(valid_devices)}")
        return False
    
    config_path = Path(__file__).parent / "config.yaml"
    
    # чтениеконфиг
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # обновлениеУстройствотип
    old_device = config['region'].get('device_type', 'desktop')
    config['region']['device_type'] = device_type
    
    # 存конфиг
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)
    
    emoji = "📱" if device_type == "mobile" else "💻"
    print(f"{emoji} Устройствотипуже переключение: {old_device} -> {device_type}")
    
    # показатьтекущийконфиг
    region = config['region']['current']
    profile = config['region']['profiles'][region]
    
    ua_key = f"{device_type}_user_agents"
    user_agents = profile.get(ua_key, [])
    
    print(f"\n📱 текущийконфиг:")
    print(f"  Устройствотип: {device_type.upper()}")
    print(f"  Регион: {region.upper()}")
    print(f"  User-Agent количество: {len(user_agents)}")
    if user_agents:
        print(f"  示例 UA: {user_agents[0][:80]}...")
    
    return True


def show_current():
    """показатьтекущийУстройствоконфиг"""
    config_path = Path(__file__).parent / "config.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    device_type = config['region'].get('device_type', 'desktop')
    region = config['region']['current']
    profile = config['region']['profiles'][region]
    
    emoji = "📱" if device_type == "mobile" else "💻"
    print(f"{emoji} текущийУстройствотип: {device_type.upper()}")
    print(f"📍 Регион: {region.upper()}")
    
    ua_key = f"{device_type}_user_agents"
    user_agents = profile.get(ua_key, [])
    print(f"🔧 User-Agent количество: {len(user_agents)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(" :")
        print("  просмотртекущийконфиг: python switch_device.py show")
        print("  переключениеУстройствотип: python switch_device.py [desktop|mobile]")
        print()
        show_current()
    elif sys.argv[1] == "show":
        show_current()
    else:
        switch_device(sys.argv[1].lower())
