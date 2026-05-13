from main import run
from outlook_accounts import OUTLOOK_ACCOUNTS
import time

def debug_one():
    # 取第один账号
    account = OUTLOOK_ACCOUNTS[0]
    print(f"🐞 начало单 Debug 运строка: {account['email']}")
    print("👀 请观察браузерстрокакак...")
    
    # 运строка
    try:
        run(fixed_account=account)
    except Exception as e:
        print(f"❌ 运строканеудача: {e}")

if __name__ == "__main__":
    debug_one()
