"""
IPгеолокациязапрос模
согласноПроксиIPавто识别Регион并настройкаокружение
"""

import requests


def get_ip_location(ip_address):
    """
    запросIPадрес геолокация
    
    Args:
        ip_address: IPадресстрока
    
    Returns:
        dict: содержитстрана代 код、страна名、Таймзонаи т.д.информация
              例如: {'country_code': 'US', 'country': 'United States', 'timezone': 'America/New_York'}
              неудачавозвратNone
    """
    # попыткамного 免费IPзапроссервис
    services = [
        {
            'name': 'ip-api.com',
            'url': f'http://ip-api.com/json/{ip_address}',
            'parser': parse_ipapi
        },
        {
            'name': 'ipapi.co',
            'url': f'https://ipapi.co/{ip_address}/json/',
            'parser': parse_ipapico
        },
        {
            'name': 'ipwhois.app',
            'url': f'http://ipwhois.app/json/{ip_address}',
            'parser': parse_ipwhois
        }
    ]
    
    for service in services:
        try:
            print(f"🔍 запросIPгеолокация ({service['name']})...")
            response = requests.get(service['url'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                result = service['parser'](data)
                
                if result and result.get('country_code'):
                    print(f"✅ IPгеолокация: {result.get('country')} ({result.get('country_code')})")
                    return result
        except Exception as e:
            print(f"   跳 {service['name']}: {e}")
            continue
    
    print("⚠️  нетзапросIPгеолокация，将использованиепо умолчаниюнастройка")
    return None


def parse_ipapi(data):
    """разбор ip-api.com  возвратчисло据"""
    if data.get('status') != 'success':
        return None
    
    return {
        'country_code': data.get('countryCode', ''),
        'country': data.get('country', ''),
        'timezone': data.get('timezone', ''),
        'city': data.get('city', ''),
        'region': data.get('regionName', ''),
        'isp': data.get('isp', '')
    }


def parse_ipapico(data):
    """разбор ipapi.co  возвратчисло据"""
    return {
        'country_code': data.get('country_code', ''),
        'country': data.get('country_name', ''),
        'timezone': data.get('timezone', ''),
        'city': data.get('city', ''),
        'region': data.get('region', ''),
        'isp': data.get('org', '')
    }


def parse_ipwhois(data):
    """разбор ipwhois.app  возвратчисло据"""
    if not data.get('success'):
        return None
    
    return {
        'country_code': data.get('country_code', ''),
        'country': data.get('country', ''),
        'timezone': data.get('timezone', ''),
        'city': data.get('city', ''),
        'region': data.get('region', ''),
        'isp': data.get('isp', '')
    }


def map_country_to_region(country_code):
    """
    将страна代 код映射→я们конфиг Регион
    
    Args:
        country_code: 两字母страна代 код（如 US, DE, JP）
    
    Returns:
        str: Регион名称 ('usa', 'germany', 'japan' и т.д.)，не知возврат 'usa'
    """
    # страна代 код→Регион 映射
    mapping = {
        # 德国 и немецкий区
        'DE': 'germany',
        'AT': 'germany',  # 奥地利，也 немецкий
        'CH': 'germany',  # 瑞士（немецкий区）
        
        # 本
        'JP': 'japan',
        
        # 美国 и английский区
        'US': 'usa',
        'CA': 'usa',  # 加拿большой
        'GB': 'usa',  # 英国
        'AU': 'usa',  # 澳большой利亚
        'NZ': 'usa',  # 新西兰
        'IE': 'usa',  # 爱尔兰
    }
    
    region = mapping.get(country_code.upper(), 'usa')
    return region


def get_region_config_from_ip(ip_address):
    """
    согласноIPадресполучить推荐 Регионконфиг
    
    Args:
        ip_address: IPадрес
    
    Returns:
        dict: {
            'region': Регион名称,
            'country_code': страна代 код,
            'country': страна名称,
            'timezone': Таймзона,
            ...
        }
    """
    location = get_ip_location(ip_address)
    
    if not location:
        return {
            'region': 'usa',
            'country_code': 'US',
            'country': 'United States',
            'timezone': 'America/New_York'
        }
    
    country_code = location.get('country_code', 'US')
    region = map_country_to_region(country_code)
    
    return {
        'region': region,
        'country_code': country_code,
        'country': location.get('country', ''),
        'timezone': location.get('timezone', ''),
        'city': location.get('city', ''),
        'isp': location.get('isp', '')
    }


def extract_ip_from_proxy_url(proxy_url):
    """
    изПроксиURLвизвлечениеIPадрес
    
    Args:
        proxy_url: ПроксиURL，如 http://1.2.3.4:8080 или http://user:pass@1.2.3.4:8080
    
    Returns:
        str: IPадрес，неудачавозвратNone
    """
    try:
        # 移除协议前缀
        url = proxy_url
        if '://' in url:
            url = url.split('://')[1]
        
        # 移除认证информация
        if '@' in url:
            url = url.split('@')[1]
        
        # извлечениеIP（去掉端口）
        ip = url.split(':')[0]
        
        return ip
    except:
        return None
