import boto3
import base64
import tempfile
import uuid
import creds

class Bucket:
    """Clase para acceso fácil al cliente de S3 de AWS"""
    BUCKET_NAME = 'usocial'
    FOLDER_USUARIO = 'foto-usuario'
    FOLDER_POSTS = 'pubs'

    def __init__(self):
        self.CLIENT = boto3.client(
            's3',
            aws_access_key_id = creds.bucket['access-key-id'],
            aws_secret_access_key = creds.bucket['secret-access-key'],
        )

    def write_user(self, user, image64, ext):
        """Guardar imagen de profesor en bucket"""
        file_content = base64.b64decode(image64)
        file_name = '{}-{}.{}'.format(user, uuid.uuid4(), ext)
        file_path = '{}/{}'.format(self.FOLDER_USUARIO, file_name)

        with tempfile.TemporaryFile(suffix='.{}'.format(ext)) as f:
            f.write(file_content)
            f.seek(0)

            self.CLIENT.put_object(
                Body = f,
                Bucket = self.BUCKET_NAME,
                Key = file_path
            )

        return file_path

    def write_post(self, fecha,hora, image64, ext):
        """Guardar imagen de estudiante en bucket"""
        file_content = base64.b64decode(image64)
        fecha = fecha.replace('/','')
        hora= hora.replace(':','')
        file_name = '{}-{}.{}'.format(fecha+hora, uuid.uuid4(), ext)
        file_path = '{}/{}'.format(self.FOLDER_POSTS, file_name)
        
        f = tempfile.TemporaryFile(dir = 'tmp')
        f.write(file_content)
        f.seek(0)

        self.CLIENT.put_object(
            Body = f,
            Bucket = self.BUCKET_NAME,
            Key = file_path,
            ContentType = 'image/{}'.format(ext)
        )

        f.close()
        
        return file_path
    
    def get_image64(self, image_path):
        get = self.CLIENT.get_object(
            Bucket = self.BUCKET_NAME,
            Key = image_path
        )
        content_bytes = get['Body'].read()
        base64_bytes = base64.b64encode(content_bytes)
        return {'base64': base64_bytes.decode('ascii'),'type':get['ContentType']}
