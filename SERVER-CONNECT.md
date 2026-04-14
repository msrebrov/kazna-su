# Подключение к VPS — КАЗНА

> **Среда:** Прод-среда — домен kazna.su размещён на Selectel VPS 45.80.129.53

---

## Данные сервера

| Параметр              | Значение              | Комментарий                       |
|-----------------------|-----------------------|-----------------------------------|
| Внешний IP            | 45.80.129.53          | Публичный адрес сервера           |
| ОС                    | Ubuntu 24.04.4 LTS    |                                   |

---

## Подключение SSH

### Быстрое подключение

```bash
ssh kazna-vps
```

SSH-конфиг уже добавлен в `~/.ssh/config`:

```
Host kazna-vps
    HostName 45.80.129.53
    User root
    IdentityFile ~/.ssh/avitoserm_vps
    IdentitiesOnly yes
```

---

## Деплой

Код доставляется автоматически через GitHub Actions при пуше в `main`.

```
Локальная машина  →  GitHub (github.com/msrebrov/kazna-su)  →  VPS (45.80.129.53)
     git push               автоматический деплой
```

### Что происходит автоматически:

1. GitHub получает пуш в `main`
2. Запускается GitHub Actions (`.github/workflows/deploy.yml`)
3. SSH на VPS → `cd /var/www/kazna.su && git fetch && git reset --hard origin/main`
4. Smoke test: `curl -sf https://kazna.su`

### Проверка на сервере

```bash
ssh kazna-vps "cd /var/www/kazna.su && git log --oneline -3"
```

---

## Nginx

- Конфиг: `/etc/nginx/sites-available/kazna.su`
- Root: `/var/www/kazna.su`
- SSL: Let's Encrypt (certbot), автопродление
- Сертификат: `/etc/letsencrypt/live/kazna.su/`

---

## GitHub Secrets

| Secret           | Значение        |
|------------------|-----------------|
| `SERVER_HOST`    | 45.80.129.53    |
| `SERVER_USER`    | root            |
| `SERVER_SSH_KEY` | приватный ключ  |
