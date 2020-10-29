import boto3
import creds
from botocore.exceptions import ClientError
import json

class Cognito:
    def __init__(self):
        self.idp_client = boto3.client( 'cognito-idp',creds.admin['region'], aws_access_key_id = creds.admin['access_key_id'],aws_secret_access_key = creds.admin['secret_access_key'])
        
    def sign_up(self,User,Password):
        try:
            self.idp_client.sign_up(
                ClientId=creds.cognito['client_id'],
                Username= User,
                Password= Password,
            )
            response= self.confirm_sign_up(User)
        except ClientError as e:
            array={
                'status':500,
                'error': e.response['Error']['Code']
            }
            return  array
        
        return {  'status':200, 'response':response }


    def confirm_sign_up(self,User):
         
        try:
            response = self.idp_client.admin_confirm_sign_up(
                UserPoolId = creds.cognito['pool_id'],
                Username = User,
            )
        except ClientError as e:
            array={
                'status':500,
                'error': e.response['Error']['Code']
            }
            return  array
        return {  'status':200, 'response':response  }

    

    def login(self,Username,password):
        try:
            response=self.idp_client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': Username,
                    'PASSWORD': password
                },
                ClientId=creds.cognito['client_id']
            )
        except ClientError as e:
            array={
                'status':500,
                'error': e.response['Error']['Code']
            }
            return  array
        return {  'status':200, 'response':response['AuthenticationResult']['AccessToken']  }

    def Update_Username(self,Token,Username):
        try:
            response = self.idp_client.update_user_attributes(
                UserAttributes=[
                    {
                        'Name': 'USERNAME',
                        'Value': Username
                    },
                ],
                AccessToken=Token,
            )
        except ClientError as e:
            array={
                'status':500,
                'error': e.response['Error']['Code']
            }
            return  array
        return {  'status':200, 'response':response  }