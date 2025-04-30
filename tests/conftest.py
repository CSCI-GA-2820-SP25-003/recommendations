import pytest
from service import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = False  # 让 Flask 处理异常而不是直接抛出

    with app.app_context():
        with app.test_client() as client:
            yield client
