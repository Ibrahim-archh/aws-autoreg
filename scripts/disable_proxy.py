#!/usr/bin/env python3
"""
临когдаконфигпереключениеутилита - 禁 Прокси
"""

import yaml
from pathlib import Path

config_path = Path(__file__).parent / "config.yaml"

# чтениеконфиг
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 禁 Прокси
config['region']['use_proxy'] = False

# 存конфиг
with open(config_path, 'w', encoding='utf-8') as f:
    yaml.dump(config, f, allow_unicode=True, sort_keys=False)

print("✅ Проксиуже 临когда禁 ")
print("   如需重新启 ，手动修改 config.yaml в  use_proxy: true")
