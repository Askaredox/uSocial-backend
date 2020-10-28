import boto3
import base64
import tempfile
import uuid
import creds

class Bucket:
    BUCKET_NAME = 'usocial'
    FOLDER_PUBS = 'pubs'

    def __init__(self):
        self.CLIENT = boto3.client(
            's3',
            aws_access_key_id = creds.bucket['access-key-id'],
            aws_secret_access_key = creds.bucket['secret-access-key']
        )

    def write_pub(self, imagen64, ext):
        file_content = base64.b64decode(imagen64)
        file_name = '{}.{}'.format(uuid.uuid4(), ext)
        file_path = '{}/{}'.format(self.FOLDER_PUBS, file_name)
        with tempfile.TemporaryFile(suffix = '.{}'.format(ext)) as f:
            f.write(file_content)
            f.seek(0)

            self.CLIENT.put_object(
                Body = f,
                Bucket = self.BUCKET_NAME,
                Key = file_path
            )
        return file_path

    def get_pub(self, ruta):
        get = self.CLIENT.get_object(
            Bucket = self.BUCKET_NAME,
            Key = ruta
        )
        content_bytes = get['Body'].read()
        base64_bytes = base64.b64encode(content_bytes)
        return {'base64':base64_bytes.decode('ascii'),'type':get['ContentType']}
        