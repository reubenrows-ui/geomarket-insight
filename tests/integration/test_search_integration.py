from shared.config.settings import settings
from shared.clients.category_search import CategorySearchClient  # your wrapper
from shared.clients.gazetteer_search import GazetteerSearchClient

def main():
    cfg = settings
    cat = CategorySearchClient(project_id=cfg.PROJECT_ID, location=cfg.SEARCH_LOCATION)
    gaz = GazetteerSearchClient(project_id=cfg.PROJECT_ID, location=cfg.SEARCH_LOCATION)

    sample = "coffee near downtown cobourg"
    print(f"Query: {sample}")
    print("Categories →", cat.search(sample))
    print("Gazetteer →", gaz.search(sample))

if __name__ == "__main__":
    main()
