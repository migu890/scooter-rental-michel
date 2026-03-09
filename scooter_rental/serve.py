import os
from dotenv import load_dotenv
from waitress import serve

load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    serve(app, host=host, port=port)
