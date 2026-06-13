from src.database.models import Base


def test_required_sqlite_tables_are_declared():
    tables = set(Base.metadata.tables)
    assert {"trends", "creator_memory", "viral_predictions", "publish_packages"}.issubset(tables)
