import os
from encoder.server import main

if __name__ == "__main__":
    actions = bool(int(os.environ.get("ACTIONS", "1")))
    main(os.environ.get("ENCODER_HOST", "0.0.0.0"), int(os.environ.get("ENCODER_PORT", 8080)), actions=actions)
