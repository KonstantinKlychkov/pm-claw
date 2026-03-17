# Подключение к серверу PM Claw

## Данные сервера

- **IP:** 178.104.82.11
- **Пользователь:** deploy
- **Ключ:** ed25519 (без passphrase)

## 1. Проверка SSH-ключа

```powershell
# Убедись, что ключ существует
Test-Path ~/.ssh/id_ed25519

# Посмотреть fingerprint ключа
ssh-keygen -lf ~/.ssh/id_ed25519
```

Если ключа нет — значит он на другой машине или не был скопирован.

## 2. Подключение

```powershell
ssh deploy@178.104.82.11
```

При первом подключении SSH спросит подтверждение fingerprint сервера — ответь `yes`.

## 3. Если не работает

| Проблема | Что проверить |
|----------|---------------|
| `Connection timed out` | Сервер выключен или IP неверный. Проверь в Hetzner Cloud Console |
| `Connection refused` | SSH-сервер не запущен или порт закрыт. Проверь через Hetzner Console (rescue) |
| `Permission denied (publickey)` | Ключ не добавлен на сервер. Проверь `~/.ssh/id_ed25519` и что публичный ключ есть в `/home/deploy/.ssh/authorized_keys` на сервере |
| `Host key verification failed` | Сервер был пересоздан. Удали старую запись: `ssh-keygen -R 178.104.82.11` |

## 4. Проверка соединения без входа

```powershell
# Проверить доступность порта
Test-NetConnection 178.104.82.11 -Port 22

# Подключиться с verbose-логом для диагностики
ssh -v deploy@178.104.82.11
```
