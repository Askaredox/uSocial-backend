from flask import Flask, url_for, request, render_template
import hashlib
from mongo import Mongo
from flask_cors import CORS
import json
import random
import time
from cognito import Cognito
from bucket import Bucket
from rekog import Rekog
from translate import Translate
##import simplejson as json
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origin": "*"}})
db = Mongo()


@app.route('/')
def todo():
    return 'hello-world'

# usuarios


@app.route('/usuarios', methods=['GET'])
def getUsers():
    return json.dumps(db.get_users())


@app.route('/people', methods=['GET'])
def getPeople():
    return json.dumps(db.get_people())


@app.route('/usuarios/new', methods=['POST'])
def newUser():
    if request.method == 'POST':
        content = request.get_json()
        if not db.exist_user(content['Usuario']):
            if(content['Contrasenia'] == content['Confirmacion']):
                obj = {
                    'Nombre': content['Nombre'],
                    'Usuario': content['Usuario'],
                    'Contrasenia': hashlib.sha1(bytes((content['Contrasenia']), encoding="utf-8")).hexdigest(),
                    'Foto': content['Foto'],
                    'ModoBot': content['ModoBot'],
                    'Amigos': content['Amigos'],
                }
                service_cognito = Cognito()
                response = service_cognito.sign_up(
                    obj['Usuario'], content['Contrasenia'])
                if response['status'] == 200:
                    s3 = Bucket()
                    if obj['Foto']['base64'] and obj['Foto']['ext']:
                        obj['Foto'] = s3.write_user(
                            obj['Usuario'], content['Foto']['base64'], content['Foto']['ext'])
                    else:
                        obj['Foto'] = ''
                    ret = db.Create_user(obj)
                    return {"status": 200, "id": ret}
                return response
            else:
                return {'status': 1, 'error': 'Contrasenias no coinciden'}
        else:
            return {'status': 2, 'error': 'Usuario no disponible'}


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        content = request.get_json()
        service_cognito = Cognito()
        res = service_cognito.login(content['Usuario'], content['Contrasenia'])
        if res['status'] == 200:
            return str(res['response'])
        else:
            return {'status': 1, 'error': 'Contraseña y/o usuario incorrecto'}


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


@app.route('/usuarios/modify', methods=['PUT'])
def update():
    if request.method=='PUT':
        content = request.get_json()
        obj={}
        obj['Nombre']=content['Nombre']
        obj['ModoBot']=content['ModoBot']
        if content['Foto']['base64'] and content['Foto']['ext']:
            antiguo= db.login({'Usuario':content['Usuario']})['datos']
            antiguo= antiguo['Foto']
            s3= Bucket()

            #obj['Foto']="foto-usuario/Guiss097-3f399b3f-2f89-487a-a3e9-bd371f315a82.jpg"
            if antiguo:
                s3.delete_picture(antiguo)
            obj['Foto']=s3.write_user(content['Usuario'],content['Foto']['base64'],content['Foto']['ext'])
        else:
            obj['Foto']=""

        ret = db.update_user(content['Usuario'],obj)
        return  {'modificados':ret}
        
# publicaciones


@app.route('/posts', methods=['GET'])
def getPosts():
    return json.dumps(db.get_posts())


@app.route('/posts/new', methods=['POST'])
def newPub():
    # time.strftime("%d/%m/%y")
    if request.method == 'POST':
        content = request.get_json()
        s3 = Bucket()
        rek = Rekog()
        ruta = ''
        tags = []
        if(content['Image']):
            ruta = s3.write_post(content['Image'], content['Ext'])
            tags = rek.get_tags(ruta)

        obj = {
            'Image': ruta,
            'Text': content['Text'],
            'Date': time.strftime("%d/%m/%y"),
            'Hour': time.strftime("%H:%M:%S"),
            'User': content['User'],
            'Tags': tags,
        }
        ret = db.Create_post(obj)
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


@app.route('/tags', methods=['POST'])
def getTags():
    content = request.get_json()
    ruta = content['Ruta']
    rek = Rekog()
    return rek.get_tags(ruta)

@app.route('/posts/traducir', methods=['POST'])
def translate():
    if request.method=='POST':
        content = request.get_json()
        trans= Translate()
        return {'Traduccion':trans.Traducir(content['Text'])}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)
"""
{
    "Usuario":"Andy",
    "Contrasenia":"Tacos123!",
    "Confirmacion":"Tacos123!",
    "Nombre":"andres",
    "ModoBot":false,
    "Amigos":[],
    "Foto":{"base64":"","Ext":""}
}
"""
