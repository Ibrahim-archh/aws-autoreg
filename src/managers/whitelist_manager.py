"""
Проксибелый списокуправлениеутилита
автодобавитьтекущийIP→Проксибелый список
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import hashlib
from config import REGION_PROXY_API


def get_public_ip():
    """получитьтекущий公网IP"""
    try:
        # попыткамного IPзапроссервис
        services = [
            'https://api.ipify.org',
            'https://ifconfig.me/ip',
            'http://icanhazip.com',
            'https://ident.me'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip = response.text.strip()
                    print(f"✅ получить→текущий公网IP: {ip}")
                    return ip
            except:
                continue
        
        print("⚠️  нетполучить公网IP")
        return None
    except Exception as e:
        print(f"⚠️  получить公网IPнеудача: {e}")
        return None


def generate_sign(key, brand, ip):
    """
    генерация签名
    согласноAPIдокументация，возможнонужно定 签名算
    еслиненужноsign参число，это 函числоможно以возвратпустострока
    """
    # еслиAPIдокументацияестьописание签名算，在это里现
    # 暂когдавозвратпусто，еслинужноможно以补充
    return ""


def add_to_whitelist(key, ip=None, brand=2):
    """
    добавитьIP→белый список
    
    Args:
        key: API密钥
        ip: добавить IP，есликакNone则автополучитьтекущий公网IP
        brand: 品牌标识 (по умолчанию2)
    
    Returns:
        bool: успехвозвратTrue，неудачавозвратFalse
    """
    if ip is None:
        ip = get_public_ip()
        if not ip:
            return False
    
    # генерация签名（еслинужно）
    sign = generate_sign(key, brand, ip)
    
    # 构建API URL
    if sign:
        url = f"http://your-proxy-api.com/white/add?key={key}&brand={brand}&sign={sign}&ip={ip}"
    else:
        # попытканеиспользованиеsign参число
        url = f"http://your-proxy-api.com/white/add?key={key}&brand={brand}&ip={ip}"
    
    try:
        print(f"🔄 добавитьIP→белый список...")
        print(f"   IP: {ip}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.text.strip()
            print(f"📝 APIответ: {result}")
            
            # 判лиуспех（согласноAPIвозврат格调整）
            if "успех" in result or "success" in result.lower() or "ok" in result.lower():
                print(f"✅ IPуже успехдобавить→белый список！")
                return True
            else:
                print(f"⚠️  добавитьбелый списоквозможнонеудача，请检ответ")
                return False
        else:
            print(f"⚠️  APIзапроснеудача: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  добавитьбелый списокнеудача: {e}")
        return False


def delete_from_whitelist(key, ip=None, brand=2):
    """избелый список删除IP"""
    if ip is None:
        ip = get_public_ip()
        if not ip:
            return False
    
    sign = generate_sign(key, brand, ip)
    
    if sign:
        url = f"http://your-proxy-api.com/white/delete?key={key}&brand={brand}&sign={sign}&ip={ip}"
    else:
        url = f"http://your-proxy-api.com/white/delete?key={key}&brand={brand}&ip={ip}"
    
    try:
        print(f"🔄 избелый список删除IP...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ IPуже избелый список删除")
            print(f"📝 ответ: {response.text}")
            return True
        else:
            print(f"⚠️  删除неудача: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  删除белый списокнеудача: {e}")
        return False


def fetch_whitelist(key, brand=2):
    """просмотрбелый список"""
    sign = generate_sign(key, brand, "")
    
    if sign:
        url = f"http://your-proxy-api.com/white/fetch?key={key}&brand={brand}&sign={sign}"
    else:
        url = f"http://your-proxy-api.com/white/fetch?key={key}&brand={brand}"
    
    try:
        print(f"🔄 запросбелый список...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"📋 текущийбелый список:")
            print(response.text)
            return True
        else:
            print(f"⚠️  запроснеудача: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  запросбелый списокнеудача: {e}")
        return False


def extract_key_from_url(api_url):
    """изAPI URLвизвлечениеkey参число"""
    try:
        # из URL визвлечение key 参число
        if 'key=' in api_url:
            key = api_url.split('key=')[1].split('&')[0]
            return key
        return None
    except:
        return None


def auto_add_whitelist():
    """автодобавитьтекущийIP→белый список"""
    print("=" * 60)
    print("автодобавитьIP→Проксибелый список")
    print("=" * 60)
    
    # изконфигвполучитьAPIинформация
    api_url = REGION_PROXY_API.get('url', '')
    
    if not api_url:
        print("⚠️  не найденоПроксиAPIконфиг")
        return False
    
    # извлечениеkey
    key = extract_key_from_url(api_url)
    
    if not key:
        print("⚠️  нетизAPI URLвизвлечениеkey")
        print(f"   URL: {api_url}")
        return False
    
    print(f"🔑 API Key: {key}")
    print("-" * 60)
    
    # добавить→белый список
    success = add_to_whitelist(key)
    
    if success:
        print("-" * 60)
        print("🎉 белый списокконфиг成！")
        print("💡 подсказка: сейчасможно以运строка python check_proxy.py тестПрокси")
    
    return success


if __name__ == "__main__":
    auto_add_whitelist()
