import requests
import json
import pandas as pd

def get_authorization_code():

                # Required user input
                tenant = "374f8026-7b54-4a3a-b87d-328fa26ec10d" #374f8026-7b54-4a3a-b87d-328fa26ec10d
                app_secret = 'XZc7Q~hvltOaw6gOec3ltFFOWwTpxnyyEFzvQ'
                client_id = "8044e0e5-d854-4015-a22e-c63e949953a7"
                names_service_client_id = "29b57d83-d820-4fc5-8471-f7da1812493b" 

                template_authz_url = ('https://login.microsoftonline.com/{}/oauth2/token?')

                # Build the URL to request the authorization code
                authorization_url = template_authz_url.format(tenant)

                # Make authorization request
                body = {
                    "grant_type":"client_credentials",
                    "client_id": client_id,
                    "client_secret": app_secret,
                    "resource": str(names_service_client_id)
                    }
                response = requests.post(authorization_url, data = body)
                response = json.loads(response.text)
                access_token = response["access_token"]
                return response

class NameService:      
        
        def NameServiceVerification(df, index, row,language_notation,country_code,street):

                response = get_authorization_code()
                
                df = df.fillna('')                  

                name_service_url  = 'http://names-stage.speechdev.tomtom.com/name'

                header = { 'Authorization' : 'Bearer ' + response['access_token'] }

                data= {"nameText":df.loc[index,street],
                        "languageCode":language_notation.split('.')[0],
                        "notationAlphabet":language_notation.split('.')[1],
                        "adminArea":country_code,
                        "nameStream":"ACI",
                        "projectName": "SN_NORMALIZER"}
                
                name_service_response = requests.post(name_service_url, json=data, headers=header)
                
                json = name_service_response.json()
                
                if df.loc[index,street] == '':

                    df.loc[index,'Street_Verified'] = "Null Value"
                    
                elif json['confidence'] == 1.0:
                    
                    df.loc[index,'Street_Verified'] = "SN exists in TT Database"
                    
                else:
                    
                    df.loc[index,'Street_Verified'] = "SN NOT in TT Database"


                #return df.loc[index,'Street_Verified']

