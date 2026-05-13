"""
Проксиуправление模
支持静Прокси и 动APIПрокси
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from config import (
    REGION_USE_PROXY,
    REGION_PROXY_MODE,
    REGION_PROXY_URL,
    REGION_PROXY_API,
    HTTP_TIMEOUT
)


class ProxyManager:
    """Менеджер прокси"""
    
    def __init__(self):
        self.use_proxy = REGION_USE_PROXY
        self.proxy_mode = REGION_PROXY_MODE
        self.static_proxy = REGION_PROXY_URL
        self.api_config = REGION_PROXY_API
        self.current_proxy = None
        self.proxy_location = None  # 存储ПроксиIP геолокацияинформация
    
    def get_proxy(self):
        """
        получитьПрокси
        
        Returns:
            str: ПроксиURL (例如: http://ip:port или socks5://ip:port)
            None: еслинеиспользованиеПроксиилиполучитьнеудача
        """
        if not self.use_proxy:
            return None
        
        if self.proxy_mode == "static":
            # использование静Прокси
            self.current_proxy = self.static_proxy
            return self.static_proxy
        
        elif self.proxy_mode == "dynamic":
            # изAPIполучить动Прокси
            return self._fetch_proxy_from_api()
        
        return None
    
    def _fetch_proxy_from_api(self):
        """изAPIполучитьПроксиIP"""
        if not self.api_config or not self.api_config.get('url'):
            print("⚠️  ПроксиAPIнеконфиг")
            return None
        
        api_url = self.api_config['url']
        timeout = self.api_config.get('timeout', 10)
        protocol = self.api_config.get('protocol', 'http')
        auth_required = self.api_config.get('auth_required', False)
        
        try:
            print(f"🔄 изAPIполучитьПрокси...")
            response = requests.get(api_url, timeout=timeout)
            
            if response.status_code == 200:
                # получитьвозврат  IP:PORT
                proxy_text = response.text.strip()
                
                # 清возможно 换строка符 и пусто格
                proxy_text = proxy_text.replace('\n', '').replace('\r', '').strip()
                
                if not proxy_text:
                    print("⚠️  APIвозвратпустосодержимое")
                    return None
                
                # 构建полный ПроксиURL
                if auth_required:
                    username = self.api_config.get('username', '')
                    password = self.api_config.get('password', '')
                    proxy_url = f"{protocol}://{username}:{password}@{proxy_text}"
                else:
                    proxy_url = f"{protocol}://{proxy_text}"
                
                self.current_proxy = proxy_url
                print(f"✅ Проксиполучитьуспех: {proxy_text}")
                
                # запросПроксиIP геолокация
                self._query_proxy_location(proxy_text.split(':')[0])
                
                return proxy_url
            else:
                print(f"⚠️  APIзапроснеудача: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"⚠️  APIзапрос超когда (>{timeout}сек)")
            return None
        except Exception as e:
            print(f"⚠️  получитьПроксинеудача: {e}")
            return None
    
    def _query_proxy_location(self, ip_address):
        """запросПроксиIP геолокация"""
        try:
            from helpers.ip_location import get_region_config_from_ip
            self.proxy_location = get_region_config_from_ip(ip_address)
        except Exception as e:
            print(f"   запросIPпозициянеудача: {e}")
            self.proxy_location = None
    
    def test_proxy(self, proxy_url=None):
        """
        тестПроксилидоступный
        
        Args:
            proxy_url: тест ПроксиURL，есликакNone则тесттекущийПрокси
        
        Returns:
            bool: True表示доступный，False表示недоступный
        """
        if proxy_url is None:
            proxy_url = self.current_proxy
        
        if not proxy_url:
            return False
        
        try:
            print(f"🔍 тестПрокси...")
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # тестдоступодин轻量уровень 网站
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                ip_info = response.json()
                print(f"✅ Прокситестуспех！текущийIP: {ip_info.get('origin', 'Unknown')}")
                return True
            else:
                print(f"⚠️  Прокситестнеудача: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️  Прокситестнеудача: {e}")
            return False
    
    def get_current_proxy(self):
        """получитьтекущийиспользование Прокси"""
        return self.current_proxy
    
    def print_proxy_info(self):
        """印Проксиинформация"""
        if not self.use_proxy:
            print("🔒 Прокси: выключен")
            return
        
        print(f"🔒 Прокси模: {self.proxy_mode.upper()}")
        
        if self.proxy_mode == "static" and self.static_proxy:
            print(f"   静Прокси: {self.static_proxy}")
        elif self.proxy_mode == "dynamic":
            if self.current_proxy:
                # 隐藏полныйПроксиинформация，只показатьIP
                display_proxy = self.current_proxy.split('@')[-1] if '@' in self.current_proxy else self.current_proxy
                print(f"   动Прокси: {display_proxy}")
            else:
                print(f"   动Прокси: ожиданиеполучить...")


# 创建局Менеджер прокси例
proxy_manager = ProxyManager()


def get_proxy():
    """получитьПрокси 便捷函число"""
    return proxy_manager.get_proxy()


def test_current_proxy():
    """тесттекущийПрокси 便捷函число"""
    return proxy_manager.test_proxy()
