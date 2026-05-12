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
        # Executa o script de deploy
        result = subprocess.run(
            ["/var/www/atlas/restart_atlas.sh"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True  # Retorna strings ao invés de bytes
        )
        return jsonify({"status": "ok", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": f"error {str(e.stdout)}, {str(e.stderr)}", "output": e.stdout}), 500