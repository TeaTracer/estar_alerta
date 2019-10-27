import os
from encoder.server import main

if __name__ == "__main__":
    main(os.environ.get("ENCODER_HOST"), int(os.environ.get("ENCODER_PORT")))
