import os
import sys
import pathlib
import pytest

# Projektroot (Ordner mit wsgi.py) in sys.path einfügen
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Test-ENV setzen bevor create_app() importiert wird
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"


@pytest.fixture()
def app():
    from app import create_app
    from app.extensions import db

    app = create_app()
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()