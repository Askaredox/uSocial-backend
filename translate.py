import boto3
import creds

class Translate:
    def __init__(self):
        self.translate = boto3.client(
            'translate',
            creds.admin['region'], 
            aws_access_key_id = creds.admin['access_key_id'],
            aws_secret_access_key = creds.admin['secret_access_key'], 
            use_ssl=True
        )
    def Traducir(self,Texto):
        result=self.translate.translate_text(Text=Texto, SourceLanguageCode= 'auto', TargetLanguageCode='es')
        return result.get('TranslatedText')

