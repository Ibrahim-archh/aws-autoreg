"""
многоЯзыквыбор模
支持не同Регион 本地界面элемент定位
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from selenium.webdriver.common.by import By
from config import REGION_CURRENT


class MultiLangSelector:
    """многоЯзыквыбор"""
    
    def __init__(self):
        # загрузкаЯзыкконфиг (конфиг в корне проекта config/ 下)
        lang_config_path = Path(__file__).parent.parent.parent / "config" / "languages.yaml"
        with open(lang_config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
        
        # получитьтекущийРегион对应 Язык
        self.current_lang = self._config['region_language_map'].get(
            REGION_CURRENT, 
            'en'  # по умолчанию английский
        )
        
        # получитьвсеЯзык текст（для兼容）
        self.texts = self._config['languages']
        self.current_texts = self.texts.get(self.current_lang, self.texts['en'])
    
    def get_text(self, key):
        """получитьтекущийЯзык текст"""
        return self.current_texts.get(key, key)
    
    def get_all_text_variations(self, key):
        """получитьвсеЯзык版本 текст（для创建兼容всеЯзык выбор）"""
        variations = []
        for lang_code, lang_texts in self.texts.items():
            text = lang_texts.get(key)
            if text and text not in variations:
                variations.append(text)
        return variations
    
    def get_button_xpath(self, key):
        """
        генерациямногоЯзык兼容 кнопка XPath
        例如: //button[contains(., 'Continue') or contains(., 'Weiter') or contains(., '続строка')]
        """
        variations = self.get_all_text_variations(key)
        if not variations:
            return f"//button"
        
        # Сборка OR-условия
        conditions = [f"contains(., '{text}')" for text in variations]
        xpath = f"//button[{' or '.join(conditions)}]"
        return xpath
    
    def get_link_xpath(self, key):
        """
        генерациямногоЯзык兼容 ссылка XPath
        """
        variations = self.get_all_text_variations(key)
        if not variations:
            return f"//a"
        
        conditions = [f"contains(., '{text}')" for text in variations]
        xpath = f"//a[{' or '.join(conditions)}]"
        return xpath
    
    def get_text_xpath(self, key):
        """
        генерациямногоЯзык兼容 任элемент XPath（дляпоисксодержит定текст элемент）
        """
        variations = self.get_all_text_variations(key)
        if not variations:
            return f"//*"
        
        conditions = [f"contains(., '{text}')" for text in variations]
        xpath = f"//*[{' or '.join(conditions)}]"
        return xpath
    
    def get_by_xpath(self, key, element_type='button'):
        """
        Возвращает Selenium By
        
        Args:
            key: ключ строки
            element_type: 'button', 'link', 'any'
        
        Returns:
            (By.XPATH, xpath_string)
        """
        if element_type == 'button':
            xpath = self.get_button_xpath(key)
        elif element_type == 'link':
            xpath = self.get_link_xpath(key)
        else:
            xpath = self.get_text_xpath(key)
        
        return (By.XPATH, xpath)
    
    def print_current_language(self):
        """印текущийиспользование Язык"""
        lang_names = {
            'de': 'немецкий (Deutsch)',
            'ja': 'японский (本語)',
            'en': 'английский (English)'
        }
        lang_name = lang_names.get(self.current_lang, self.current_lang)
        print(f"🌍 Язык интерфейса: {lang_name}")
    
    def update_region(self, region_name):
        """动обновлениеРегион"""
        self.current_lang = self._config['region_language_map'].get(
            region_name,
            'en'
        )
        self.current_texts = self.texts.get(self.current_lang, self.texts['en'])



# Глобальный инстанс
lang_selector = MultiLangSelector()


def get_continue_button_selector():
    """получить Continue кнопка многоЯзыквыбор"""
    return lang_selector.get_by_xpath('continue', 'button')


def get_signup_button_selector():
    """получить Sign up кнопка многоЯзыквыбор"""
    return lang_selector.get_by_xpath('sign_up_with_builder_id', 'any')
