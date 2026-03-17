# Состояние проекта PM Claw

> Обновляется после каждой завершённой фичи (режим "Фича завершена").

## Стек

- Python 3.12
- OpenClaw framework
- python-telegram-bot==20.7 (подключён)
- python-dotenv — подключён
- pytest + ruff
- GitHub для VCS

## Структура

```
pm-claw/
├── CLAUDE.md
├── deploy.sh
├── requirements.txt
├── .env.example
├── src/
│   ├── main.py
│   ├── bot_runner.py        # точка входа для Telegram-бота
│   ├── bot/
│   │   ├── bot.py           # инициализация Application
│   │   └── handlers.py      # обработчик /start
│   ├── skills/
│   └── config/
├── tests/                   # 169 тестов, все проходят
└── .claude/
    ├── skills/              # test-all, deploy, project-snapshot
    ├── commands/            # commit-push-pr
    ├── agents/              # code-reviewer, test-writer
    └── hooks/               # auto-lint, block-dangerous
```

## MCP-серверы

- GitHub (HTTP) — настроен в ~/.claude.json
- Context7 (stdio) — настроен в ~/.claude.json

## Инфраструктура

- **Провайдер:** Hetzner Cloud
- **Сервер:** CX22 (2 vCPU, 4 GB RAM, 40 GB NVMe)
- **Локация:** Nuremberg (nbg1), Германия
- **ОС:** Ubuntu 24.04 LTS
- **IP:** 178.104.82.11
- **Пользователь:** deploy (sudo)
- **Firewall:** UFW (OpenSSH разрешён)
- **Софт:** Python 3.12.3, git 2.43.0, pip, venv
- **SSH-ключ:** ed25519, без passphrase
- **SSH-ключ деплоя:** C:\Users\Redmi\.ssh\id_ed25519_new (без passphrase)
- **SSH alias:** hetzner → deploy@178.104.82.11
- **Сервис:** pm-claw.service (systemd), запускает src/bot_runner.py
- **Деплой:** `bash deploy.sh` (DEPLOY_SERVER из .env)
- **Логи:** `journalctl -u pm-claw`

## Открытые issues

- #4 — Telegram briefing (scheduled)

## Бэклог

### Ближайшие
- Деплой PM Claw на сервер (Hetzner)
- Подключить PM Claw к OpenClaw Gateway
- Настроить Telegram-бота
- Добавить реальные LLM-вызовы в IdeaGeneratorSkill и CompetitorSkill
- Закрыть issue #4

### Среднесрочные
- GitHub Actions для CI
- Упаковать в OpenClaw plugin
- Новые skills (user research, metrics tracking)
- Heartbeat для автоматических брифингов

### Для роста навыков
- Merge-конфликты и разрешение
- Сложные рефакторинги с /rewind
- Worktrees для параллельной разработки
- CI/CD с Agent SDK

## История изменений

- **[дата старта]** — начальное состояние: 4 скилла, 146 тестов, 2 MCP-сервера
- **2026-03-17** — deploy.sh, systemd-сервис, docs/server-access.md
- **2026-03-17** — Telegram-бот: базовая инфраструктура, /start handler, деплой на Hetzner как systemd-сервис
