import os
os.environ['FINN_PREWARM']='false'
os.environ['FINN_WORKER']='false'
# Ordinary tests must never write to a user's newly configured hosted database.
os.environ['FINN_DATABASE_URL']=''
import pytest


@pytest.fixture(autouse=True)
def isolated_storage_for_every_test(tmp_path,monkeypatch):
    """A test without its own fixture must not touch the developer's cache."""
    from backend import store,repository,documents
    monkeypatch.setenv('FINN_DATABASE_URL','')
    for module in (store,repository,documents):monkeypatch.setattr(module,'DATA',tmp_path)
    store.init();repository.init()
