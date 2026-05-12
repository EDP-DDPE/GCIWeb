import logging
import os
from main import create_app

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = create_app()

if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", 8000))

    print("Iniciando Atlas...")
    app.run(debug=True, host=host, port=port, use_reloader=False)
    print(f"Flask app running on http://{host}:{port}")
    