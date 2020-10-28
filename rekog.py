from bucket import Bucket
import boto3
import creds

class Rekog:
    def __init__(self):
        self.CLIENT = boto3.client(
            'rekognition',
            aws_access_key_id = creds.rekog['access-key-id'],
            aws_secret_access_key = creds.rekog['secret-access-key'],
            region_name = creds.rekog['region']
        )

    def get_tags(self, ruta):
        tags=[]
        response = self.CLIENT.detect_labels(
            Image ={
                'S3Object':{
                    'Bucket': Bucket.BUCKET_NAME,
                    'Name': ruta
                }
            },
            MaxLabels=10,
            MinConfidence=90
        )
        for label in response['Labels']:
            tags.append(label['Name'])
        return tags



