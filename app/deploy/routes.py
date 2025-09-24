import os
import subprocess
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

deploy_bp = Blueprint("deploy", __name__)

if not load_dotenv():
    print("Não foi possível carregar o .env no routes do Deploy.")
# Defina uma chave secreta só sua (coloque no .env)
SECRET_KEY = os.getenv("DEPLOY_KEY")


@deploy_bp.route("/deploy", methods=["POST"])
def deploy():
    key = request.headers.get("X-DEPLOY-KEY")
    if key != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Rodar o script de deploy
        output = subprocess.check_output(
            [
                "/bin/bash", "-c",
                """
                cd /var/www/atlas/GCIWeb &&
                git fetch --all &&
                git reset --hard origin/main &&
                source /var/www/atlas/venv/bin/activate &&
                pip install -r requirements.txt &&
                sudo systemctl restart atlas
                """
            ],
            stderr=subprocess.STDOUT
        )
        return jsonify({"status": "ok", "output": output.decode("utf-8")})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "output": e.output.decode("utf-8")}), 500