# aws-autoreg

Рабочий авторегистратор аккаунтов **AWS Builder ID** через свой почтовый домен на Cloudflare.

Форк [7836246/aws-builder-id](https://github.com/7836246/aws-builder-id) с фиксами багов, русским UI и интеграцией со своим `cloudflare_temp_email` Worker'ом (вместо публичного `mail.tm`).

Регистрация полностью автоматическая: создаёт почту на твоём домене, проходит форму AWS, ловит OTP, сохраняет готовый аккаунт.

---

## Чем отличается от оригинала

- Почта берётся со своего домена через `cloudflare_temp_email`, не с публичного `mail.tm`
- UI полностью на русском (200+ строк переведено)
- Фикс OTP-парсера — не хватает `000000` из заголовков, ищет код по контексту
- Фикс валидации регистрации — провалы идут в `accounts_failed.jsonl`, не в успехи
- Фикс User-Agent — совпадает с реальной версией Chrome
- Интерактивное меню вместо отдельных команд
- Один `.bat` для запуска всего

---

## Быстрый старт

```powershell
git clone https://github.com/Ibrahim-archh/aws-autoreg.git aws-builder-id
cd aws-builder-id
.\start.bat
```

При первом запуске `start.bat` сам:
- проверит Python
- поставит зависимости
- определит твою версию Chrome и подставит её в код
- запустит интерактивное меню

В меню:
- настройка Cloudflare Worker (тебе нужно ввести `worker_url`, `domain`, `admin_password`)
- одиночная регистрация
- **батч на любое количество регистраций** (введи число — например `10`)
- просмотр писем и OTP-кодов из почты
- список аккаунтов / провалов
- смена региона / устройства / прокси
- очистка журналов

---

## Подключение Cloudflare с нуля

Без этого скрипт не будет работать — нужен свой почтовый Worker.

### 1. Купи домен

Любой регистратор (Beget, Namecheap, RuCenter). `.ru` подходит, но `.com` универсальнее — некоторые внешние сервисы фронтенд-валидатором режут `.ru` (хотя AWS-бэкенд его принимает).

Цена: от 150₽/год за `.ru`, от $10/год за `.com`.

### 2. Подключи домен к Cloudflare

1. Зарегистрируйся на https://dash.cloudflare.com/sign-up (бесплатно)
2. **Add a domain** → введи домен → выбери Free plan
3. Cloudflare покажет два nameserver'а, например:
   ```
   alex.ns.cloudflare.com
   kate.ns.cloudflare.com
   ```
4. Иди к своему регистратору → DNS → **поменяй NS** на эти два
5. Жди статус **Active** (10-30 минут, иногда до 24 часов)

### 3. Получи API-токен Cloudflare

https://dash.cloudflare.com/profile/api-tokens → **Create Token** → шаблон **Edit Cloudflare Workers** → **Use template**.

Далее по кнопке **+ Add more** добавь права:
- `Account` → `D1` → `Edit`
- `Account` → `Email Routing Addresses` → `Edit`
- `Zone` → `Email Routing Rules` → `Edit`

→ Continue to summary → **Create Token** → скопируй `cfut_...` (показывают один раз).

Пропиши токен в переменную окружения навсегда:

```powershell
[Environment]::SetEnvironmentVariable("CLOUDFLARE_API_TOKEN", "cfut_...", "User")
```

Закрой и открой PowerShell заново.

### 4. Поставь wrangler и pnpm

```powershell
npm install -g wrangler pnpm
```

### 5. Разверни `cloudflare_temp_email` Worker

```powershell
git clone https://github.com/dreamhunter2333/cloudflare_temp_email
cd cloudflare_temp_email\worker
```

Создай D1-базу:

```powershell
wrangler d1 create temp-email-db
```

Из вывода скопируй блок с `database_id`.

Создай `worker/wrangler.toml` (шаблон рядом — `wrangler.toml.template`), минимально замени:

| Поле | На что |
|---|---|
| `database_id` | то что выдала `wrangler d1 create` |
| `DEFAULT_DOMAINS = [...]` | свой домен, например `["myrealagent.ru"]` |
| `DOMAINS = [...]` | то же |
| `ADMIN_PASSWORDS = [...]` | придумай пароль, например `["LongRandomPassword123"]` |
| `JWT_SECRET = "..."` | случайная строка 48+ символов |
| `PREFIX = "tmp"` | оставь как есть |

Поставь зависимости и накати схему:

```powershell
pnpm install
wrangler d1 execute temp-email-db --remote --file=..\db\schema.sql
```

Деплой:

```powershell
pnpm run deploy
```

Получишь `worker_url` типа `https://<имя>.<аккаунт>.workers.dev` — это и есть твой `worker_url` для авторега.

Доведи миграции (если в репо были обновления схемы):

```powershell
$W = "https://<твой-worker>.workers.dev"
$ADMIN = "<твой-admin-password>"
curl.exe -X POST "$W/admin/db_migration" -H "x-admin-auth: $ADMIN"
```

### 6. Подключи Email Routing к Worker

В Cloudflare → твой домен → **Email Routing**:

1. **Destination Addresses** → **Add** → введи свой Gmail → подтверди код из письма
2. **Routing rules** → у строки `Catch-all address` справа три точки `...` → **Edit**
3. **Action: Send to a Worker** → выбери воркер `cloudflare_temp_email` → **Save**
4. Переключи Catch-all в **Active**

Если в выпадушке Action нет варианта `Send to a Worker` — сначала зайди в **Destination Workers** → **Create destination** → выбери воркер. Потом возвращайся к Routing rules → Catch-all.

### 7. Проверь почту

```powershell
$W = "https://<твой-worker>.workers.dev"
$r = Invoke-RestMethod -Method Post -Uri "$W/api/new_address" -ContentType "application/json" -Body '{"name":"test1"}'
$r
```

Должно вывести `address: tmptest1@твой.домен` и `jwt: ...`

Отправь любую почту на этот адрес. Через 20-30 сек:

```powershell
$JWT = $r.jwt
Invoke-RestMethod -Uri "$W/api/mails?limit=10" -Headers @{Authorization="Bearer $JWT"}
```

Если в `results` появилось письмо — Worker работает.

---

## Настройка авторега

После шагов выше у тебя есть три значения:
- `worker_url` — например `https://myrealagent-tempmail.vhhh.workers.dev`
- `domain` — например `myrealagent.ru`
- `admin_password` — что задал в `ADMIN_PASSWORDS`

Запускай:

```powershell
.\start.bat
```

В меню жми **1 — Настройка Cloudflare Worker**, введи три значения. После этого пункт меню «тестовый запрос» подтвердит что всё подключилось.

Теперь:
- **2** — попробуй одну регистрацию
- **3** — батч на 10 / 50 / 100 регистраций подряд
- **4** — смотри коды OTP когда AWS просит 2FA при логине

---

## Прокси / VPN

С российского IP AWS почти всегда даёт CAPTCHA или бан. Нужен зарубежный IP.

### Вариант 1 (проще всего): системный VPN

**Просто включи любой VPN с серверами США** на уровне системы и забудь. В конфиге прокси оставляй `use_proxy: false`, скрипт пойдёт через системный туннель.

Работает с любым нормальным VPN-клиентом: Proton, Mullvad, NordVPN, Outline, AmneziaVPN. Бесплатные расширения для Chrome НЕ подойдут — они VPN-ят только обычный Chrome, а Selenium запускает свой инстанс без расширений.

Проверено: достаточно просто включить VPN-США → регистрации проходят без CAPTCHA, ничего больше менять не надо.

### Вариант 2: SOCKS5-прокси (для батчей и ротации)

Если регишь массово или хочешь разные IP — купи SOCKS5 USA/EU-резидента (ASocks, ProxyEmpire, IPRoyal). Один прокси = один отпечаток, под батч в десятки регистраций удобнее пул.

В меню **7 → 3** включи прокси и введи URL:

```
socks5://username:password@host:port
```

Или через CLI:

```powershell
python menu.py --proxy on --proxy-url socks5://user:pass@host:port
```

Проверка отдельно:

```powershell
python scripts\check_proxy.py
```

### Когда какой вариант

| Сценарий | Что использовать |
|---|---|
| Одна-две регистрации для себя | системный VPN — проще нет ничего |
| Батч 10-50 на одном IP | системный VPN ок (если провайдер не блокит AWS) |
| Батч 50+ под продажу, разные fingerprints | SOCKS5 USA, желательно резиденты, с ротацией |

---

## Результаты

| Файл | Что внутри |
|---|---|
| `accounts.jsonl` | успешные регистрации (email, password, name, jwt_token, created_at) |
| `accounts_failed.jsonl` | провалы с полем `reason` (URL/exception) |

Формат — **JSONL** (одна запись на строку). Не ломается при параллельных записях.

---

## CLI-флаги (для ботов / ИИ / автоматизации)

`menu.py` с аргументами работает **без интерактивного режима**:

```powershell
# Конфигурация
python menu.py --set-worker https://x.workers.dev --set-domain my.ru --set-admin pwd
python menu.py --region usa --device desktop
python menu.py --proxy on --proxy-url socks5://u:p@host:port
python menu.py --proxy off
python menu.py --headless true

# Регистрация
python menu.py --run                       # одна
python menu.py --batch 50                  # 50 подряд
python menu.py --batch 10 --delay 60       # 10 с паузой 60 сек

# Просмотр писем
python menu.py --mail                              # последние 10 писем
python menu.py --mail tmpXXX@my.ru                 # для конкретного адреса
python menu.py --mail tmpXXX@my.ru --code-only     # ТОЛЬКО OTP в stdout

# Журналы
python menu.py --list                      # успешные (JSONL)
python menu.py --list --format json        # JSON-массив
python menu.py --list --format csv         # CSV
python menu.py --failed                    # провалы
python menu.py --clear accounts            # очистить успехи
python menu.py --clear failed              # очистить провалы
python menu.py --clear all                 # очистить оба

# Диагностика
python menu.py --status                    # вся конфигурация (JSON)
python menu.py --test-worker               # проверка связи с Worker

python menu.py --help                      # полный help
```

**Exit codes:** `0` — успех, `1` — нет результата, `2` — конфиг не задан, `3` — сетевая ошибка.

Шорткаты:

```powershell
# Достать последний код в буфер обмена
python menu.py --mail tmpXXX@my.ru --code-only | clip

# Батч + экспорт в CSV
python menu.py --batch 20 ; python menu.py --list --format csv > accounts.csv

# Health-check Worker (для cron)
python menu.py --test-worker
```

---

## Решение типичных проблем

См. [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).

Самые частые:
- **`ChromeDriver only supports Chrome version X`** — обнови `version_main=` в `src/runners/main.py` или перезапусти `start.bat`
- **OAuth `localhost:8976` не работает** — используй API-токен через env var, не `wrangler login`
- **`Invalid email` в стороннем сервисе при логине через Builder ID** — их фронт может резать `.ru`, входи сначала на `profile.aws.amazon.com`
- **AWS даёт CAPTCHA** — нужен SOCKS5-прокси

---

## Стоимость

| | |
|---|---|
| Домен `.ru` | ~150₽/год |
| Cloudflare (Workers + D1 + Email Routing) | бесплатно до 100k запросов/день |
| Прокси SOCKS5 (для масс-реги) | $3-5/мес |

Итого: 0₽ если для себя, ~300₽/мес при масс-реге.

---

## Лицензия

MIT.
