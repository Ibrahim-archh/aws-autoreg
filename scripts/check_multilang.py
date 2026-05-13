#!/usr/bin/env python3
"""
тестмногоЯзыквыбор
"""

from multilang import lang_selector
from config import REGION_CURRENT

print("=" * 60)
print("многоЯзыквыбортест")
print("=" * 60)

print(f"\n📍 текущийРегион: {REGION_CURRENT.upper()}")
lang_selector.print_current_language()

print("\n🔍 тествыборгенерация:")
print("-" * 60)

# тесткнопкавыбор
print("\n1. Continue кнопка XPath:")
continue_xpath = lang_selector.get_button_xpath('continue')
print(f"   {continue_xpath}")

print("\n2. Sign upкнопка XPath:")
signup_xpath = lang_selector.get_text_xpath('sign_up_with_builder_id')
print(f"   {signup_xpath}")

print("\n3. всеЯзык  Continue текст:")
variations = lang_selector.get_all_text_variations('continue')
for i, text in enumerate(variations, 1):
    print(f"   {i}. {text}")

print("\n4. всеЯзык  Sign up текст:")
variations = lang_selector.get_all_text_variations('sign_up_with_builder_id')
for i, text in enumerate(variations, 1):
    print(f"   {i}. {text}")

print("\n" + "=" * 60)
print("✅ многоЯзыквыбортест成")
print("=" * 60)
