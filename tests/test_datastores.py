# tests/test_datastores.py
import types
from tools.create_datastore import create_or_replace_datastore

class FakeOp:
    def result(self, timeout=None): return types.SimpleNamespace(name="projects/p/locations/l/collections/c/dataStores/ds")

class FakeClient:
    def __init__(self, exists=False): self.exists = exists
    def get_data_store(self, name): 
        if self.exists: return types.SimpleNamespace(name=name)
        from google.api_core import exceptions
        raise exceptions.NotFound("nope")
    def delete_data_store(self, name): return FakeOp()
    def create_data_store(self, parent, data_store, data_store_id): return FakeOp()

def test_create_when_absent():
    ds = create_or_replace_datastore("p","global","c","ds",display_name="DS",client=FakeClient(False))
    assert "dataStores/ds" in ds.name

def test_overwrite_when_present():
    ds = create_or_replace_datastore("p","global","c","ds",display_name="DS",client=FakeClient(True), overwrite=True)
    assert "dataStores/ds" in ds.name
