"""Reddit client construction.

The 2018 code hardcoded a script-app client id and username and read the
secret and password from the environment. All of those values now come from
the environment. The old variable names ``client_secret`` and
``reddit_password`` are still accepted.
"""

import os

import praw

_LEGACY_NAMES = {
    "client_secret": ("REDDIT_CLIENT_SECRET", "client_secret"),
    "password": ("REDDIT_PASSWORD", "reddit_password"),
}


def _first(*names):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def reddit_settings():
    return {
        "client_id": _first("REDDIT_CLIENT_ID"),
        "client_secret": _first(*_LEGACY_NAMES["client_secret"]),
        "username": _first("REDDIT_USERNAME"),
        "password": _first(*_LEGACY_NAMES["password"]),
        "user_agent": _first("REDDIT_USER_AGENT") or "karmamining comment scorer",
    }


def reddit_credentials_missing():
    labels = {
        "client_id": "REDDIT_CLIENT_ID",
        "client_secret": "REDDIT_CLIENT_SECRET (or client_secret)",
        "username": "REDDIT_USERNAME",
        "password": "REDDIT_PASSWORD (or reddit_password)",
    }
    settings = reddit_settings()
    return [labels[key] for key in labels if not settings[key]]


def reddit_client():
    missing = reddit_credentials_missing()
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            "Missing Reddit credentials: "
            f"{joined}. Copy .env.example and export the variables, "
            "or open post id 'demo' to score the bundled sample comments."
        )
    settings = reddit_settings()
    return praw.Reddit(
        client_id=settings["client_id"],
        client_secret=settings["client_secret"],
        username=settings["username"],
        password=settings["password"],
        user_agent=settings["user_agent"],
    )
