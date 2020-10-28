from flask import Flask,url_for, request, render_template
import hashlib 
from mongo import Mongo
from flask_cors import CORS
import json
import random
import time
from cognito import Cognito
from bucket import Bucket
from rekog import Rekog
##import simplejson as json
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origin": "*"}})
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
        res = service_cognito.login(content['Usuario'],content['Contrasenia'])
        if res['status']==200:
            res2= db.login({'Usuario': content['Usuario']})

            if res2['status']==200:
                res2['datos']['Token']=res['response']
                s3= Bucket()
                res2['datos']['Foto']= s3.get_image64(res2['datos']['Foto'])
                array={
                    'status':200,
                    'response':{
                        'datos':res2['datos']
                    }
                }
                return str(array)

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
            'Hour': time.strftime("%H:%M:%S") ,
            'User': content['User'],
            'Tags': tags,
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

@app.route('/tags',methods=['POST'])
def getTags():
    content = request.get_json()
    ruta = content['Ruta']
    rek = Rekog()
    return rek.get_tags(ruta)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)