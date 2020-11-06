import pymongo
import json
from bucket import Bucket
from bson.objectid import ObjectId


class Mongo:
    def __init__(self):
        client = pymongo.MongoClient("mongodb://172.19.0.3:27017/")['uSocial']
        self.Usuarios = client['User']
        self.Posts = client['Post']
        self.Chat = client['Chat']
        self.Casos = client['Casos']

# usuarios
    def get_users(self):
        ret = []
        for x in self.Usuarios.find():
            ret.append(self.__as_user(x))
        return ret

    def __as_user(self, obj):
        return {
            'Id': str(obj['_id']),
            'Nombre': obj['Nombre'],
            'Usuario': obj['Usuario'],
            'Contrasenia': obj['Contrasenia'],
            'Foto': obj['Foto'],
            'ModoBot': obj['ModoBot'],
            'Amigos': obj['Amigos'],
        }

    def get_people(self):
        ret = []
        for x in self.Usuarios.find():
            ret.append(self.__as_people(x))
        return ret

    def __as_people(self, obj):
        return{
            'Id': str(obj['_id']),
            'Usuario': obj['Usuario'],
            'Foto': obj['Foto'],
        }
        pass

    # crear usuario
    def Create_user(self, obj):
        user = obj['Usuario']
        if not self.exist_user(user):
            ret = self.Usuarios.insert_one(obj)
            return str(ret.inserted_id)
        return '-1'

    def exist_user(self, us):
        obj = self.Usuarios.find_one({'Usuario': us})
        if(obj):
            return True
        return False
    # login user

    def login(self, obj):
        obj = self.Usuarios.find_one(obj)
        if(obj):
            return {'status': 200, 'datos': self.__as_user(obj)}
        return {'status': 500, 'error': 'no encontrado'}

    # aggregar amigos a lista
    def add_Friend(self, objeto):
        obj = self.Usuarios.find_one({'Usuario': objeto['Usuario']})
        amigo = objeto['Amigo']

        if(obj):
            amigos = self.__as_user(obj)['Amigos']

            if not str(amigo) in amigos:

                amigos.append(amigo)

                resultado = self.Usuarios.update_one(
                    {
                        'Usuario': objeto['Usuario']
                    },
                    {
                        '$set': {
                            "Amigos": amigos,
                        }
                    })
                return resultado.modified_count
            return -1
        return -1  # no existe el usuario

# update user
    def update_user(self, user, new):
        cant = 0
        if new['Nombre']:
            resultado = self.Usuarios.update_one(
                {
                    'Usuario': user
                },
                {
                    '$set': {
                        "Nombre": new["Nombre"],
                        "ModoBot": new["ModoBot"]
                    }
                })
            cant = cant + resultado.modified_count
        if new['Foto']:
            resultado = self.Usuarios.update_one(
                {
                    'Usuario': user
                },
                {
                    '$set': {
                        "Foto": new["Foto"],
                        "ModoBot": new["ModoBot"]
                    }
                })
            cant = cant + resultado.modified_count
        else:
            resultado = self.Usuarios.update_one(
                {
                    'Usuario': user
                },
                {
                    '$set': {
                        "ModoBot": new["ModoBot"]
                    }
                })
            cant = cant + resultado.modified_count
        return cant
# posts

    def get_posts(self):
        ret = []
        for x in self.Posts.find():
            ret.append(self.__as_post(x))
        return ret

    def __as_post(self, obj):
        s3 = Bucket()
        img = s3.get_image64(obj['Image']) if obj['Image'] != '' else None
        return {
            'Id': str(obj['_id']),
            'Image': img,
            'Text': obj['Text'],
            'Date': obj['Date'],
            'Hour': obj['Hour'],
            'User': obj['User'],
            'Tags': obj['Tags'],
        }

    # crear post
    def Create_post(self, obj):
        ret = self.Posts.insert_one(obj)
        return str(ret.inserted_id)

    # obtener posts para el home de cada usuario
    def get_Home(self, user):
        # ubicar usuario y obtener lista de amigos
        ret = []
        obj = self.Usuarios.find_one({'Usuario': user})
        for post in self.Posts.find({"User": user}):
            ret.append(self.__as_post(post))

        if(obj):
            amigos = self.__as_user(obj)['Amigos']
            for amigo in amigos:
                # obtener post de esos amigos
                for post in self.Posts.find({"User": amigo}):
                    ret.append(self.__as_post(post))
            return ret
        return ret  # no existe el usuario

    # filtrar todos los posts con un tag especifico

    def filter_Post(self, user, tag):
        # obtener las publicaciones para ese usuario de sus amigos
        filtradas = []
        posts = []
        posts = self.get_Home(user)

        # filtrar por medio de sus tags
        for post in posts:
            if tag in post['Tags']:
                filtradas.append(post)
        return filtradas

    # obtener tags para filtrar

    def getTags(self, user):
        # obtener las publicaciones para ese usuario de sus amigos
        tags = []
        posts = []
        posts = self.get_Home(user)

        for post in posts:
            for tag in post['Tags']:
                if not tag in tags:
                    tags.append(tag)
        return tags

    def get_chat(self, id1, id2):
        mensajes = []
        obj = self.find_chat(id1, id2)
        if(obj != None):
            return {"id": str(obj['_id']), "chat": obj["chat"]}
        else:
            res = self.Chat.insert_one({
                "id1": id1,
                "id2": id2,
                "chat": []
            })
            return {"id": str(res.inserted_id), "chat": []}

    def send_chat(self, room, id, mess):
        self.Chat.find_one_and_update(
            {'_id': ObjectId(room)},
            {
                '$push': {
                    'chat': {
                        'id': id,
                        'mensaje': mess
                    }
                }
            }
        )
        return {"ok": True}

    def find_chat(self, id1, id2):
        obj = self.Chat.find_one({"id1": id1, "id2": id2})
        if(obj != None):
            return obj
        obj = self.Chat.find_one({"id1": id2, "id2": id1})
        return obj

    def is_bot(self, id):
        obj = self.Usuarios.find_one({'_id': ObjectId(id)})
        return obj['ModoBot']

    def bot_data(self, user, bot, data: str):
        res = self.Casos.find_one({'user': user, 'bot': bot})
        tipo_info = data.lower()
        if(res == None):
            tipo = 1 if tipo_info == 'casos' else 2 if tipo_info == 'grafica de casos' or tipo_info == 'grafica' else 0
            if tipo == 1:
                self.Casos.insert_one({
                    'user': user,
                    'bot': bot,
                    'Info_Tipo': tipo,
                    'Pais': '',
                    'Fecha': '',
                    'Tipo': 0,
                    'Data': 1
                })
            elif tipo == 2:
                self.Casos.insert_one({
                    'user': user,
                    'bot': bot,
                    'Info_Tipo': tipo,
                    'Pais': '',
                    'Rango': '',
                    'Data': 1
                })
            else:
                return {'ready':False, 'resp': 'Repita los datos, por favor'}
            return {'ready':False, 'resp': '¿País?'}
        else:
            if res['Info_Tipo'] == 1:
                if res['Data'] == 1:
                    self.Casos.find_one_and_update(
                        {'_id': res['_id']},
                        {
                            '$set':{
                                'Data':2,
                                'Pais':tipo_info.title()
                            }
                        }
                    )
                    return {'ready':False, 'resp': '¿Fecha?'}
                elif res['Data'] == 2:
                    self.Casos.find_one_and_update(
                        {'_id': res['_id']},
                        {
                            '$set':{
                                'Data':3,
                                'Fecha':tipo_info
                            }
                        }
                    )
                    return {'ready':False, 'resp': '¿Tipo de casos (confirmados, recuperados, muertes o todos)?'}
                else:
                    self.Casos.find_one_and_delete({'_id': res['_id']})
                    return {
                        'ready':True, 
                        'data':{
                            'Info_Tipo': res['Info_Tipo'],
                            'Pais': res['Pais'],
                            'Fecha': res['Fecha'],
                            'Tipo': self.get_tipo(tipo_info),
                        }
                    }
            else:
                if res['Data'] == 1:
                    self.Casos.find_one_and_update(
                        {'_id': res['_id']},
                        {
                            '$set':{
                                'Data':2,
                                'Pais':tipo_info.title()
                            }
                        }
                    )
                    return {'ready':False, 'resp': '¿Rango de fechas?'}
                else:
                    self.Casos.find_one_and_delete({'_id': res['_id']})
                    return {
                        'ready':True, 
                        'data':{
                            'Info_Tipo': res['Info_Tipo'],
                            'Pais': res['Pais'],
                            'Rango': tipo_info,
                        }
                    }

    def get_tipo(self, dato:str):
        data = dato.lower()
        return 1 if data == 'confirmados' else 2 if data=='recuperados' else 3 if data == 'muertes' else 4
        pass