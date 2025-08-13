from flask import render_template

import os

from forms2 import *
from db import *

app.secret_key = 'sua_chave_secreta_aqui'

# Configurações de upload
UPLOAD_FOLDER = 'temp_uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_to_onedrive(file_path, filename, folder_path="Documentos"):
    """Faz upload do arquivo para OneDrive"""
    pass


@app.route('/')
def index():
    return render_template('home.html')


if __name__ == '__main__':
    init_database()
    app.run(debug=True)