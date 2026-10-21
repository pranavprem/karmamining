from reddit_client import reddit_credentials_missing, reddit_settings


def test_missing_credentials_are_named(monkeypatch):
    for name in (
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_USERNAME",
        "REDDIT_PASSWORD",
        "client_secret",
        "reddit_password",
    ):
        monkeypatch.delenv(name, raising=False)
    missing = reddit_credentials_missing()
    assert any("REDDIT_CLIENT_ID" in item for item in missing)
    assert any("REDDIT_PASSWORD" in item for item in missing)


def test_legacy_secret_names_still_count(monkeypatch):
    monkeypatch.setenv("REDDIT_CLIENT_ID", "id")
    monkeypatch.setenv("client_secret", "secret")
    monkeypatch.setenv("REDDIT_USERNAME", "user")
    monkeypatch.setenv("reddit_password", "pw")
    assert reddit_credentials_missing() == []
    settings = reddit_settings()
    assert settings["client_secret"] == "secret"
    assert settings["password"] == "pw"
