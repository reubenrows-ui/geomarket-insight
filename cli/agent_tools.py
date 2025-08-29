import argparse
import os
from google.cloud import discoveryengine_v1 as de
from tools.datastores import create_or_replace_datastore

def main():
    p = argparse.ArgumentParser("Vertex AI Search – datastore setup")
    p.add_argument("--project", default=os.getenv("PROJECT_ID"), required=False)
    p.add_argument("--location", default=os.getenv("SEARCH_LOCATION", "global"))
    p.add_argument("--collection_id", default=os.getenv("COLLECTION_ID", "default_collection"))
    p.add_argument("--data_store_id", default=os.getenv("DATA_STORE_ID"))
    p.add_argument("--display_name", default=os.getenv("DATA_STORE_DISPLAY_NAME"))
    p.add_argument("--no-overwrite", action="store_true")
    args = p.parse_args()

    if not all([args.project, args.data_store_id, args.display_name]):
        p.error("Missing required values (project, data_store_id, display_name).")

    ds = create_or_replace_datastore(
        project_id=args.project,
        location=args.location,
        collection_id=args.collection_id,
        data_store_id=args.data_store_id,
        display_name=args.display_name,
        industry_vertical=de.IndustryVertical.GENERIC,
        solution_types=(de.SolutionType.SOLUTION_TYPE_SEARCH,),
        content_config=de.DataStore.ContentConfig.NO_CONTENT,
        overwrite=not args.no_overwrite,
    )
    print("Created DataStore:", ds.name)

if __name__ == "__main__":
    main()
