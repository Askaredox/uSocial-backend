from flask import Flask, url_for, request, render_template
from flask_cors import CORS
from mongo import Mongo
from bucket import Bucket
import json
import time
import hashlib
##import simplejson as json
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origin": "*"}})
db = Mongo()


@app.route('/')
def todo():
    return 'hello world'

# usuarios


@app.route('/usuarios', methods=['GET'])
def getUsers():
    return json.dumps(db.get_users())


@app.route('/usuarios/new', methods=['POST'])
def newUser():
    if request.method == 'POST':
        content = request.get_json()
        obj = {
            'Nombre': content['Nombre'],
            'Usuario': content['Usuario'],
            'Contrasenia': hashlib.sha1(bytes((content['Contrasenia']), encoding="utf-8")).hexdigest(),
            'Foto': content['Foto'],
            'ModoBot': content['ModoBot'],
            'Amigos': content['Amigos'],
        }
        ret = db.Create_user(obj)
        return {"id": ret}


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        content = request.get_json()
        password = hashlib.sha1(
            bytes((content['Contrasenia']), encoding="utf-8")).hexdigest()
        content['Contrasenia'] = password
        ret = db.login(content)
        return {'acceso': ret}


@app.route('/usuarios/add', methods=['POST'])
def add_Friend():
    if request.method == 'POST':
        content = request.get_json()
        ret = db.add_Friend(content)
        if ret > 0:
            user = content['Amigo']
            amigo = content['Usuario']
            content['Usuario'] = user
            content['Amigo'] = amigo
            ret = ret+db.add_Friend(content)
        return {'modificados': ret}

# publicaciones


@app.route('/posts', methods=['GET'])
def getPosts():
    return json.dumps(db.get_posts())


@app.route('/posts/new', methods=['POST'])
def newPub():
    # time.strftime("%d/%m/%y")
    if request.method == 'POST':
        content = request.get_json()

        ruta = ''

        if(content['Image'] != ''):
            s3 = Bucket()
            ruta = s3.write_pub(content['Image'], content['Ext'])

        obj = {
            'Image': ruta,
            'Text': content['Text'],
            'Date': time.strftime("%d/%m/%y"),
            'Hour': time.strftime("%H:%M:%S"),
            'User': content['User'],
            'Tags': 'no todavia',
        }
        ret = db.create_post(obj)

        return {"id": ret}


@app.route('/posts/home', methods=['GET'])
def addTags():
    if request.method == 'GET':
        User = request.args.get('User')
        ret = db.get_Home(User)
        return json.dumps(ret)


@app.route('/posts/filtrar', methods=['GET'])
def Filtrar():
    if request.method == 'GET':
        Tag = request.args.get('Tag')
        User = request.args.get('User')
        ret = db.filter_Post(User, Tag)
        return json.dumps(ret)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=True)
