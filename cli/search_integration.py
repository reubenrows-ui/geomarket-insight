from backend.config import get_config
from backend.category_search import CategorySearchClient  # your wrapper
from backend.gazetteer_search import GazetteerSearchClient

def main():
    cfg = get_config()
    cat = CategorySearchClient(project_id=cfg.PROJECT_ID, location=cfg.SEARCH_LOCATION)
    gaz = GazetteerSearchClient(project_id=cfg.PROJECT_ID, location=cfg.SEARCH_LOCATION)

    sample = "coffee near downtown cobourg"
    print(f"Query: {sample}")
    print("Categories →", cat.search(sample))
    print("Gazetteer →", gaz.search(sample))

if __name__ == "__main__":
    main()
