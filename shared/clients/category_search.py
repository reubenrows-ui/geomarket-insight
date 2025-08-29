class CategorySearchClient:
    def __init__(self, project_id: str, location: str):
        self.project_id = project_id; self.location = location
    def search(self, query: str):
        return {"results": [], "query": query}
