"""PM Claw skills registry."""

from __future__ import annotations

SKILL_REGISTRY: dict[str, dict] = {
    "digest": {
        "description": "RSS news digest",
        "usage": "/digest — collect and format RSS feed digest",
    },
    "ideas": {
        "description": "SCAMPER idea generation",
        "usage": "/ideas <topic> — brainstorm product ideas",
    },
    "competitor": {
        "description": "Competitor analysis",
        "usage": "/competitor <product> — mini competitor research",
    },
    "briefing": {
        "description": "Daily PM briefing",
        "usage": "/briefing <topic> — full daily briefing with news and ideas",
    },
}
