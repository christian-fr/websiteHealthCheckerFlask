import os
import secrets
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, render_template, request, json, send_from_directory
from werkzeug.utils import secure_filename, redirect
from tempfile import TemporaryDirectory
import time
import random
from string import hexdigits
import json

app = Flask(__name__)
app.debug = True
app.config['upload_dir'] = TemporaryDirectory()
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = secrets.token_hex(16)

# ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'xml']
ALLOWED_EXTENSIONS = ['xml']
URL_DICT = None
URL_LIST = None
CONFIG_FILE = Path(r'./db/config.json')


def check_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.parent.mkdir(exist_ok=True, parents=True)
        sample_config = {'URL': ['https://www.dzhw.eu', 'https://presentation.dzhw.eu']}
        CONFIG_FILE.write_text(json.dumps(sample_config))


def randstr(n, alphabet=hexdigits):
    return "".join([random.choice(alphabet) for _ in range(n)])


def valid_filename(filename):
    return os.path.splitext(filename)[1].lower().lstrip('.') in ALLOWED_EXTENSIONS


def delete_url_index(index: int) -> None:
    global URL_LIST
    tmp_list = urls_list()
    tmp_list.pop(index)
    URL_LIST = tmp_list


def upload_dir():
    p = Path(app.config['upload_dir'].name)
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)

    return p


def urls_dict():
    global URL_DICT
    # review simple file dict - might be cleared when app is reinitialized

    if URL_DICT is None:
        URL_DICT = {}

    return URL_DICT


def urls_list():
    global URL_LIST
    # review simple file dict - might be cleared when app is reinitialized

    if URL_LIST is None:
        URL_LIST = []

    return URL_LIST


@app.route('/')
def index():
    return redirect('/health')


# @app.route('/upload', methods=['GET'])
# def upload():
#    uploaded_files = list(file_dict().values())
#    return render_template('upload.html', uploaded_files=uploaded_files)

def load_config():
    u_list = json.loads(CONFIG_FILE.read_text('utf-8'))['URL']
    [urls_list().append(url) for url in u_list if url not in urls_list()]
    return urls_list()


def write_config():
    config_data = {'URL': urls_list()}
    CONFIG_FILE.write_text(data=json.dumps(config_data), encoding='utf-8')


@app.route('/health', methods=['GET'])
def health():
    url_list = load_config()
    return render_template('health.html', url_list=url_list)


@app.route('/health', methods=['POST'])
def add_url():
    pass
    if 'url' in request.form:
        url = request.form['url']
        url_parsed = urlparse(url.encode('utf-8'))
        if url_parsed.scheme in [b'https', b'http'] and url_parsed.hostname is not None:
            if url not in urls_list():
                urls_list().append(url)
                write_config()
    if 'delete_url' in request.form:
        delete_url_index(int(request.form.get('delete_url')))
        write_config()
    return redirect('/health')


@app.route('/api/process/<file_id>', methods=['GET'])
def process_file(file_id):
    if file_id not in urls_dict():
        return app.response_class(
            response=json.dumps({'msg': 'file id not registered'}),
            status=400,
            mimetype='application/json'
        )
    else:
        file_meta = urls_dict()[file_id]

    filename = file_meta['internal_filename']

    if not Path(upload_dir(), filename).exists():
        return app.response_class(
            response=json.dumps({'msg': 'file does not exist'}),
            status=400,
            mimetype='application/json'
        )

    # magic
    internal_filename = urls_dict()[file_id]['internal_filename']
    file_data = Path(upload_dir(), internal_filename).read_text(encoding='utf-8')
    processed_filename = 'processed_' + internal_filename
    Path(upload_dir(), processed_filename).write_text(file_data.replace('x', 'y'))
    time.sleep(1)

    return app.response_class(
        response=json.dumps({'msg': 'success'}),
        status=200,
        mimetype='application/json'
    )


@app.route('/file/<string:filename>')
def get_image(filename):
    return send_from_directory(upload_dir(), path=filename, as_attachment=False)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return app.response_class(
            response=json.dumps({'msg': 'no file selected'}),
            status=400,
            mimetype='application/json'
        )

    file = request.files['file']
    if file is None or not valid_filename(file.filename):
        return app.response_class(
            response=json.dumps({'msg': 'invalid file'}),
            status=400,
            mimetype='application/json'
        )

    file_id = randstr(20)
    internal_filename = secure_filename(os.path.join(file_id, os.path.splitext(file.filename)[1]))
    file.save(Path(upload_dir(), internal_filename))
    urls_dict()[file_id] = {'file_id': file_id, 'filename': file.filename, 'internal_filename': internal_filename}

    return app.response_class(
        response=json.dumps(urls_dict()[file_id]),
        status=200,
        mimetype='application/json'
    )


# @app.route('/api/add_url', methods=['POST'])

def main():
    try:
        check_config()
        app.run()
    finally:
        if 'upload_dir' in app.config:
            app.config['upload_dir'].cleanup()

check_config()

if __name__ == '__main__':
    main()
