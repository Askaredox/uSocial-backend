from flask import Flask,url_for, request, render_template
import hashlib 
from mongo import Mongo
from flask_cors import CORS
import json
import random
import time
from cognito import Cognito
from bucket import Bucket
##import simplejson as json
app = Flask(__name__)
cors = CORS(app, resources={r"/": {"origin": "*"}})
db = Mongo()

@app.route('/')
def todo():
    return 'hello-world'

#usuarios
@app.route('/usuarios',methods=['GET'])
def getUsers():
    return json.dumps(db.get_users())

@app.route('/usuarios/new',methods=['POST'])
def newUser():
    if request.method == 'POST':
        content = request.get_json()
        if not db.exist_user(content['Usuario']):
            if(content['Contrasenia']== content['Confirmacion']):
                obj = {
                'Nombre': content['Nombre'],
                'Usuario': content['Usuario'],
                'Contrasenia': hashlib.sha1(bytes((content['Contrasenia']), encoding = "utf-8")).hexdigest(),
                'Foto': content['Foto'],
                'ModoBot': content['ModoBot'],
                'Amigos': content['Amigos'],
                }
                service_cognito= Cognito()
                response=service_cognito.sign_up(obj['Usuario'],content['Contrasenia'])
                if response['status']==200: 
                    s3= Bucket()
                    obj['Foto']=s3.write_user(obj['Usuario'],content['Foto']['base64'],content['Foto']['ext'])
                    ret = db.Create_user(obj)
                    return {"status": 200 ,"id":ret}
                return  response
            else:
                return {'status':500, 'error':'Contrasenias no coinciden'}
        else:
            return {'status':500, 'error':'Usuario no disponible'}
    

@app.route('/login',methods=['POST'])
def login():
    if request.method == 'POST':
        content = request.get_json()
        service_cognito = Cognito()
        return str(service_cognito.login(content['Usuario'],content['Contrasenia']))

@app.route('/usuarios/add',methods=['POST'])
def add_Friend():
    if request.method == 'POST':
        content = request.get_json()
        ret = db.add_Friend(content)
        if ret > 0:
            user= content['Amigo']
            amigo= content['Usuario']
            content['Usuario']=user
            content['Amigo']= amigo
            ret= ret+db.add_Friend(content)
        return {'modificados':ret}

#publicaciones

@app.route('/posts',methods=['GET'])
def getPosts():
    return json.dumps(db.get_posts())

@app.route('/posts/new',methods=['POST'])
def newPub():
    #time.strftime("%d/%m/%y")
    if request.method == 'POST':
        content = request.get_json()
        obj = {
            'Image': content['Image'],
            'Text': content['Text'],
            'Date': time.strftime("%d/%m/%y"),
            'Hour': time.strftime("%H:%M:%S") ,
            'User': content['User'],
            'Tags': ['aun no'],
        }
        ret = db.Create_post(obj)
        return {"id": ret}

@app.route('/posts/home', methods=['GET'])
def addTags():
    if request.method == 'GET':
        User =  request.args.get('User')  
        ret = db.get_Home(User) 
        return json.dumps(ret)

@app.route('/posts/filtrar', methods=['GET'])
def Filtrar():
    if request.method == 'GET':
        Tag =  request.args.get('Tag') 
        User =  request.args.get('User') 
        ret = db.filter_Post(User,Tag)
        return json.dumps(ret)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)