import pytest

from main import DEFAULT_DATA, create_app


@pytest.fixture(scope="session")
def app():
    application = create_app(data_file=DEFAULT_DATA)
    application.config.update(TESTING=True)
    return application


@pytest.fixture
def client(app):
    return app.test_client()
