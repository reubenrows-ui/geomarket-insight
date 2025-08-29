from shared.config.settings import get_config

def main():
    cfg = get_config()
    print("✅ Environment OK")
    for k, v in cfg.model_dump().items():
        print(f"{k} = {v}")

if __name__ == "__main__":
    main()
