# Подключение к VPS — {{ PROJECT_NAME }}

> **Среда:** {{ ENVIRONMENT }} — домен {{ DOMAIN }} размещён на {{ PROVIDER }} VPS {{ SERVER_IP }}

---

## Данные сервера

| Параметр              | Значение              | Комментарий                       |
|-----------------------|-----------------------|-----------------------------------|
| Внешний IP            | {{ SERVER_IP }}       | Публичный адрес сервера           |
| Внутренний IP         | {{ INTERNAL_IP }}     | Адрес в локальной сети провайдера |
| Шлюз                  | {{ GATEWAY_ID }}      | ID сетевого шлюза                 |
| Полоса                | {{ BANDWIDTH }}       | Пропускная способность канала     |
| Группа безопасности   | {{ SECURITY_GROUP }}  | Имя группы firewall-правил        |
| ОС                    | {{ OS_VERSION }}      | Например: Ubuntu 22.04 LTS       |

---

## Подключение SSH

### Быстрое подключение (через SSH-конфиг)

```bash
ssh {{ SSH_ALIAS }}
```

Для этого добавьте блок в `~/.ssh/config`:

```
Host {{ SSH_ALIAS }}
    HostName {{ SERVER_IP }}
    User {{ SSH_USER }}
    IdentityFile {{ SSH_KEY_PATH }}
    Port {{ SSH_PORT }}
```

### Прямое подключение

```bash
ssh -i {{ SSH_KEY_PATH }} -p {{ SSH_PORT }} {{ SSH_USER }}@{{ SERVER_IP }}
```

---

## Настройка SSH-ключа

### 1. Генерация ключа (если ещё нет)

```bash
ssh-keygen -t ed25519 -C "{{ KEY_COMMENT }}"
```

### 2. Публичный ключ для добавления на сервер

```
{{ PUBLIC_KEY }}
```

### 3. Способы добавления ключа на сервер

**Вариант А — через панель провайдера:**
Укажите публичный ключ при создании VPS в панели управления {{ PROVIDER }}.

**Вариант Б — вручную:**

```bash
# Подключитесь по паролю (если доступен)
ssh {{ SSH_USER }}@{{ SERVER_IP }}

# Добавьте ключ
echo "{{ PUBLIC_KEY }}" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

---

## Деплой

Код доставляется на сервер автоматически через GitHub. Ручной деплой на сервер не используется.

### Схема процесса

```
Локальная машина  →  GitHub ({{ REPO_URL }})  →  VPS ({{ SERVER_IP }})
     git push            автоматический деплой
```

### 1. Отправка кода в репозиторий

```bash
git add .
git commit -m "описание изменений"
git push origin {{ DEPLOY_BRANCH }}
```

### 2. Автоматический деплой на сервер

При пуше в ветку `{{ DEPLOY_BRANCH }}` срабатывает {{ DEPLOY_METHOD }} — {{ DEPLOY_TOOL_DESCRIPTION }}.

**Что происходит автоматически:**

1. GitHub получает пуш в `{{ DEPLOY_BRANCH }}`
2. Запускается {{ DEPLOY_METHOD }} ({{ DEPLOY_CONFIG_PATH }})
3. Код доставляется на VPS {{ SERVER_IP }}
4. {{ POST_DEPLOY_ACTIONS }}

### 3. Проверка статуса деплоя

```bash
# В GitHub — вкладка Actions (для GitHub Actions)
# или панель деплоев в настройках репозитория

# На сервере — проверить, что код обновился
ssh {{ SSH_ALIAS }} "cd {{ PROJECT_PATH }} && git log --oneline -3"
```

### 4. Откат при проблемах

```bash
# Откатить коммит локально и запушить
git revert HEAD
git push origin {{ DEPLOY_BRANCH }}

# Или на сервере вручную (экстренный вариант)
ssh {{ SSH_ALIAS }} "cd {{ PROJECT_PATH }} && git checkout HEAD~1"
```

---

## Проверка подключения

```bash
# Проверить доступность сервера
ping {{ SERVER_IP }}

# Проверить SSH-порт
nc -zv {{ SERVER_IP }} {{ SSH_PORT }}

# Подключиться и проверить систему
ssh {{ SSH_ALIAS }} "uname -a && uptime"
```

---

## Заполнение шаблона

Замените плейсхолдеры `{{ ... }}` значениями вашего проекта:

| Плейсхолдер           | Описание                                  | Пример                                     |
|------------------------|--------------------------------------------|---------------------------------------------|
| `PROJECT_NAME`         | Название проекта                          | ProAgents                                   |
| `ENVIRONMENT`          | Тип среды                                 | Прод-среда / Стейджинг / Дев               |
| `DOMAIN`               | Доменное имя                              | proagents.ru                                |
| `PROVIDER`             | Хостинг-провайдер                         | Selectel / Hetzner / DigitalOcean           |
| `SERVER_IP`            | Внешний IP-адрес сервера                  | 45.80.129.53                                |
| `INTERNAL_IP`          | Внутренний IP                             | 192.168.0.114                               |
| `GATEWAY_ID`           | Идентификатор шлюза                       | e40745a3-0e16-...                           |
| `BANDWIDTH`            | Пропускная способность                    | 3 Гбит/с                                    |
| `SECURITY_GROUP`       | Группа безопасности                       | default                                     |
| `OS_VERSION`           | Операционная система                      | Ubuntu 22.04 LTS                            |
| `SSH_ALIAS`            | Алиас в SSH-конфиге                       | proagents-vps                               |
| `SSH_USER`             | Пользователь для подключения              | root                                        |
| `SSH_KEY_PATH`         | Путь к приватному ключу                   | ~/.ssh/proagents_vps                        |
| `SSH_PORT`             | SSH-порт                                  | 22                                          |
| `KEY_COMMENT`          | Комментарий к ключу                       | proagents@selectel                          |
| `PUBLIC_KEY`           | Публичный SSH-ключ                        | ssh-ed25519 AAAAC3Nz...                     |
| `REPO_URL`             | URL репозитория на GitHub                 | github.com/team/project                     |
| `DEPLOY_BRANCH`        | Ветка, из которой идёт деплой            | main / production                           |
| `DEPLOY_METHOD`        | Способ автодеплоя                         | GitHub Actions / Webhook / CI/CD            |
| `DEPLOY_TOOL_DESCRIPTION` | Краткое описание механизма             | GitHub Actions выполняет SSH-деплой         |
| `DEPLOY_CONFIG_PATH`   | Путь к конфигу деплоя                     | .github/workflows/deploy.yml                |
| `POST_DEPLOY_ACTIONS`  | Действия после доставки кода              | Перезапуск сервиса, миграции, сброс кеша    |
| `PROJECT_PATH`         | Путь к проекту на сервере                 | /var/www/project                            |
