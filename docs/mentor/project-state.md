# Состояние проекта PM Claw

> Обновляется после каждой завершённой фичи (режим "Фича завершена").

## Стек

- Python 3.12
- OpenClaw framework
- Telegram Bot API (python-telegram-bot) — пока не подключен
- pytest + ruff
- GitHub для VCS

## Структура

```
pm-claw/
├── CLAUDE.md
├── src/skills/
│   ├── digest_skill.py      # DigestSkill (RSS)
│   ├── idea_generator.py    # IdeaGeneratorSkill (SCAMPER)
│   ├── competitor_skill.py  # CompetitorSkill
│   └── briefing_skill.py    # BriefingSkill
├── tests/                   # 146 тестов, все проходят
├── .claude/
│   ├── skills/              # test-all, digest-test
│   ├── commands/            # commit-push-pr
│   ├── agents/              # code-reviewer, test-writer
│   ├── hooks/               # auto_lint.py (PostToolUse), block_dangerous.py (PreToolUse)
│   ├── rules/               # testing.md
│   └── settings.json
└── docs/
    ├── ideas/
    └── pipeline.md
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

## Открытые issues

- #4 — Telegram briefing (scheduled)
- #5 — Competitor research (реализован, можно закрыть)

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
