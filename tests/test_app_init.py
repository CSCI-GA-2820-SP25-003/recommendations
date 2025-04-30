import pytest


def test_app_init_fails(monkeypatch):
    """Test app exits if db.create_all() fails"""
    from service import create_app
    from service.models import db

    def fail_create_all():
        raise RuntimeError("Fake DB failure")

    monkeypatch.setattr(db, "create_all", fail_create_all)

    # 同时 mock drop_all、seed_data，避免副作用
    monkeypatch.setattr(db, "drop_all", lambda: None)
    monkeypatch.setattr("service.models.seed_data", lambda: None)

    with pytest.raises(SystemExit) as excinfo:
        create_app()
    assert excinfo.value.code == 4
