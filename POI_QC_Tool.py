import pandas as pd
import re
import numpy as np
import datetime
import geopandas as gpd
import glob
from name_service import NameService
import requests
import json
from yard_api import YardResponses

#NAME LIBRARY API
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

class Verificator:

    def Yard_API(language, country):
        response = YardResponses(language, country)
        telefone_regex = response.get_regex_telephone_number()
        global telefone
        telefone = re.compile(telefone_regex)
        global notation_code
        notation_code = response.get_notation_alphabet_value()
        global hsn_characters
        hsn_characters = response.get_hsn_valid_characters(notation_code)
        global postal_regex
        postal_regex = response.get_regex_postal_code()
        return telefone, notation_code, hsn_characters,postal_regex
           
    def POI_ID_validation(file, index,row,poi_id):
        
        

        file[poi_id] = file[poi_id].astype(float)

        file.sort_values(by=[poi_id], na_position='first', inplace=True)
        
        last_row = file.iloc[-1]
        
        
        
        if file.loc[index,poi_id] == last_row[poi_id]:
                
            file.loc[index,'POI_ID_Verified'] = 'Repeated'
                
        elif pd.isna(row[poi_id]):
                
            file.loc[index,'POI_ID_Verified'] = 'Null Value'
            
        else:
                
            file.loc[index,'POI_ID_Verified'] = 'Correct'
            
        last_row = row    


    ##############################################################


    '''Cria uma coluna com o nome do Company Name com todas as primeiras letras das palavras em Maiusculo, 
      Ex: agencia de turismo --> Agencia De Turismo

    Após isso,substitui as preposicoes com inicio maiusculo por inicio minusculo, Ex: De ---> de

    Por fim, compara a coluna original com a coluna normalizada e na coluna de verificação, se tiverem iguais está Correto,
    se não, está Incorreto
    '''
    def CompanyName_validation(file, index,row,company_name):
        


        numeros = re.compile(r'^[0-9]+$') # identifica se a linha possui só numeros, pq se possuir tá errado

        file[company_name] = file[company_name].astype(str)
        file['CompanyName_Verified'] = file['CompanyName_Verified'].astype(str)


        if pd.isna(file.loc[index,company_name]) == True or row[company_name] == 'nan':
            file.loc[index,'CompanyName_Verified'] = "Null Value" 

        elif numeros.match(str(row[company_name])):
            file.loc[index,'CompanyName_Verified'] = 'Incorrect'

        else:
            file.loc[index,'CompanyName_Capitalized'] = file.loc[index,company_name].title()

            
            file.loc[index,'CompanyName_Capitalized'] = file.loc[index,'CompanyName_Capitalized'].replace(" Ii "," II ")
            file.loc[index,'CompanyName_Capitalized'] = file.loc[index,'CompanyName_Capitalized'].replace(" Iii "," III ")
            file.loc[index,'CompanyName_Capitalized'] = file.loc[index,'CompanyName_Capitalized'].replace(" Vi "," VI ")
            file.loc[index,'CompanyName_Capitalized'] = file.loc[index,'CompanyName_Capitalized'].replace(" Xi "," XI ")
            file.loc[index,'CompanyName_Capitalized'] = file.loc[index,'CompanyName_Capitalized'].replace(" Xv "," XV ")
            file.loc[index,'CompanyName_Capitalized'] = file.loc[index,'CompanyName_Capitalized'].replace(" Iv "," IV ")
            file.loc[index,'CompanyName_Capitalized'] = file.loc[index,'CompanyName_Capitalized'].replace(" Xxiii "," XXIII ")
                
            if file.loc[index,'CompanyName_Capitalized'].split(' ')[-1] in ('Ii','Iii','Vi','Xi','Iv','Xx', 'Xxiii','Xv'):
                    
                file.loc[index,'CompanyName_Capitalized'] = file.loc[index,'CompanyName_Capitalized'].replace(file.loc[index,'CompanyName_Capitalized'].split(' ')[-1],file.loc[index,'CompanyName_Capitalized'].split(' ')[-1].upper())

            if file.loc[index,'CompanyName_Capitalized'] == file.loc[index,company_name]:
                file.loc[index,'CompanyName_Verified'] = 'Correct'

            else:
                file.loc[index,'CompanyName_Verified'] = 'Incorrect'
                    
        file.drop('CompanyName_Capitalized', axis=1, inplace=True)

    ####################################################################

    def STREET_Validation(file, index, row,language_notation,country_code,street):

        if pd.isna(file.loc[index,street]) == True or row[street] == 'nan':
            file.loc[index,street] = ''
                
            file.loc[index,'Street_Verified'] = "Null Value"

        else:

        
            response = get_authorization_code()
                            

            name_service_url  = 'http://names-stage.speechdev.tomtom.com/name'

            header = { 'Authorization' : 'Bearer ' + response['access_token'] }

            data= {"nameText":file.loc[index,street],
                    "languageCode":language_notation.split('.')[0],
                    "notationAlphabet":language_notation.split('.')[1],
                    "adminArea":country_code,
                    "nameStream":"ACI",
                    "projectName": "SN_NORMALIZER"}
                    
            name_service_response = requests.post(name_service_url, json=data, headers=header)
                    
            json = name_service_response.json()
                                            
            if json['confidence'] == 1.0:
                        
                file.loc[index,'Street_Verified'] = "SN exists in TT Database"
                        
            else:
                        
                file.loc[index,'Street_Verified'] = "SN NOT in TT Database"
 

    #############################################################################

    def HSN_validation(file,index,row,language_notation,country_code,hsn):
        split_hsn = []
        file[hsn] = file[hsn].astype(str)
        
        if pd.isna(row[hsn]) == True or row[hsn] == 'nan':
                
            file.loc[index,'HSN_Verified'] = 'Null Value'
    
        elif ' ' in file.loc[index,hsn]:
            
            split_hsn.append(file.loc[index,hsn].split(' '))
            for i in split_hsn[0]:
                for regex in hsn_characters:
                    if re.findall(regex, str(i)):
                        if i == split_hsn[-1][-1]:
                            file.loc[index,'HSN_Verified'] = 'Allowed HSN Characters'
                            break
                        else:
                            pass
                        if regex == hsn_characters[-1] and  file.loc[index,'HSN_Verified'] == '':
                            file.loc[index,'HSN_Verified'] = 'Not according to HSN Characters'
                        else:
                            pass
                    else:
                        file.loc[index,'HSN_Verified'] = 'Not according to HSN Characters'
                
        else:

            for regex in hsn_characters:
                if re.findall(regex, file.loc[index,hsn]):
                    file.loc[index,'HSN_Verified'] = 'Allowed HSN Characters'
                    continue
                
                elif regex == hsn_characters[-1] and  file.loc[index,'HSN_Verified'] == '':
                    file.loc[index,'HSN_Verified'] = 'Not according to HSN Characters'
            
                else:
                    pass

    ############################################################################

    def CEP_validation(file,index, row,language_notation,country_code,postal_code):
        
        

        if pd.isna(file.loc[index,postal_code]) == True or row[postal_code] == 'nan':

            file.loc[index,postal_code] = ''
                
            file.loc[index,'CEP_Verified'] = "Null Value"

        else:            
            
            numeros = re.compile(postal_regex)
             
                
            if numeros.match(str(row[postal_code])):
                file.loc[index,'CEP_Verified'] = 'Correct'
                                
            else:
                file.loc[index,'CEP_Verified'] = 'Incorrect'

    #############################################################################

    '''Cria uma coluna com o nome do Neighborhood com todas as primeiras letras das palavras em Maiusculo, 
      Ex: agencia de turismo --> Agencia De Turismo

    Após isso,substitui as preposicoes com inicio maiusculo por inicio minusculo, Ex: De ---> de

    Por fim, compara a coluna original com a coluna normalizada e na coluna de verificação, se tiverem iguais está Correto,
    se não, está Incorreto
    '''
    def Neighborhood_validation(file,index, row,neighborhood):
        
        
        file['Neighborhood_Capitalized'] = ''

        numeros = re.compile(r'^[0-9]+$') # identifica se a linha possui só numeros, pq se possuir tá errado

        file[neighborhood] = file[neighborhood].astype(str)
        file['Neighborhood_Verified'] = file['Neighborhood_Verified'].astype(str)
        file['Neighborhood_Capitalized'] = file['Neighborhood_Capitalized'].astype(str)


        if pd.isna(file.loc[index,neighborhood]) == True or row[neighborhood] == 'nan':
            file.loc[index,neighborhood] = ''
            file.loc[index,'Neighborhood_Verified'] = "Null Value" 

        elif numeros.match(str(row[neighborhood])):
            file.loc[index,'Neighborhood_Verified'] = 'Incorrect'

        else:
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,neighborhood].title()

            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" De "," de ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Da "," da ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Do "," do ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Dos "," dos ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Das "," das ")    
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Em "," em ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" No "," no ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Na "," na ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Nos "," nos ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Nas "," nas ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" O "," o ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" A "," a ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" E "," e ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Por "," por ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Pelo "," pelo ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Ii "," II ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Iii "," III ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Vi "," VI ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Xi "," XI ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Xv "," XV ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Iv "," IV ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" Xxiii "," XXIII ")
            file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(" D'"," d'")
                
                
            if file.loc[index,'Neighborhood_Capitalized'].split(' ')[-1] in ('Ii','Iii','Vi','Xi','Iv','Xx', 'Xxiii','Xv'):
                file.loc[index,'Neighborhood_Capitalized'] = file.loc[index,'Neighborhood_Capitalized'].replace(file.loc[index,'Neighborhood_Capitalized'].split(' ')[-1],file.loc[index,'Neighborhood_Capitalized'].split(' ')[-1].upper())
            if file.loc[index,'Neighborhood_Capitalized'] == file.loc[index,neighborhood]:
                file.loc[index,'Neighborhood_Verified'] = 'Correct'

            else:
                file.loc[index,'Neighborhood_Verified'] = 'Incorrect'
                    
        file.drop('Neighborhood_Capitalized', axis=1, inplace=True)

    #############################################################################

    '''Cria uma coluna com o nome do City com todas as primeiras letras das palavras em Maiusculo, 
      Ex: agencia de turismo --> Agencia De Turismo

    Após isso,substitui as preposicoes com inicio maiusculo por inicio minusculo, Ex: De ---> de

    Por fim, compara a coluna original com a coluna normalizada e na coluna de verificação, se tiverem iguais está Correto,
    se não, está Incorreto
    '''
    def City_validation(file, index, row, city):
        
        file['City_Capitalized'] = ''

        numeros = re.compile(r'^[0-9]+$') # identifica se a linha possui só numeros, pq se possuir tá errado

        file[city] = file[city].astype(str)
        file['City_Verified'] = file['City_Verified'].astype(str)
        file['City_Capitalized'] = file['City_Capitalized'].astype(str)


        if pd.isna(file.loc[index,city]) == True or row[city] == 'nan':
            file.loc[index,city] = ''
            file.loc[index,'City_Verified'] = "Null Value" 

        elif numeros.match(str(row[city])):
            file.loc[index,'City_Verified'] = 'Incorrect'

        else:
            file.loc[index,'City_Capitalized'] = file.loc[index,city].title()

            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" De "," de ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Da "," da ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Do "," do ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Dos "," dos ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Das "," das ")    
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Em "," em ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" No "," no ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Na "," na ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Nos "," nos ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Nas "," nas ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" O "," o ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" A "," a ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" E "," e ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Por "," por ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Pelo "," pelo ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" D'"," d'")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Ii "," II ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Iii "," III ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Vi "," VI ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Xi "," XI ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Xv "," XV ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Iv "," IV ")
            file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(" Xxiii "," XXIII ")
                
            if file.loc[index,'City_Capitalized'].split(' ')[-1] in ('Ii','Iii','Vi','Xi','Iv','Xx', 'Xxiii','Xv'):
                file.loc[index,'City_Capitalized'] = file.loc[index,'City_Capitalized'].replace(file.loc[index,'City_Capitalized'].split(' ')[-1],file.loc[index,'City_Capitalized'].split(' ')[-1].upper())

            if file.loc[index,'City_Capitalized'] == file.loc[index,city]:
                file.loc[index,'City_Verified'] = 'Correct'

            else:
                file.loc[index,'City_Verified'] = 'Incorrect'
                    
        file.drop('City_Capitalized', axis=1, inplace=True)

    #############################################################################

    def State_validation(file, index, row,state):
                
        state_regex = re.compile(r"^[A-Z]{2}$")
        
        
        if pd.isna(file.loc[index,state]) == True or row[state] == 'nan':
            file.loc[index,'State_Verified'] = "Null Value"
            
        elif state_regex.match(row[state]):
            file.loc[index,'State_Verified'] = 'Correct'
                  
        else:
            file.loc[index,'State_Verified'] = 'Incorrect'

    #############################################################################

    def country_validation(file, index, row, country_code, country):
        
        

        if pd.isna(row[country]) == True or row[country] == 'nan':
                
                file.loc[index,'Country_Verified'] = 'Null Value'
                
        elif row[country] == country_code:
            
            file.loc[index,'Country_Verified'] = 'Correct'
            
        else:
            
            file.loc[index,'Country_Verified'] = 'Incorrect'
                

    #############################################################################


    def phone_validation(file,index, row, phone, language_notation, country_code):

        if pd.isna(row[phone]) == True or row[phone] == 'nan':
                
            file.loc[index,'Phone_Number_Verified'] = 'Null Value'

        else:    
        
            if telefone.match(str(row[phone])):#telefone.match(row['PHONE_NUMBER_1']):
                    
                file.loc[index,'Phone_Number_Verified'] = 'Correct'
                    
                               
            else:
                    
                file.loc[index,'Phone_Number_Verified'] = 'Incorrect'
                

    ##################################################################################################


    def web_validation(file, index, row, web):
        
        
        web_regex = re.compile("^(www\w{0,1}\.)+(\w{1,})+(\.\w{1,3})(\.\w{1,2})?$")
        
 

        if pd.isna(row[web]) == True or row[web] == 'nan':
                
                file.loc[index,'Web_Verified'] = 'Null Value'

        elif web_regex.match(str(row[web])):
                    
                file.loc[index,'Web_Verified'] = 'Correct'
                                                   
        else:
                    
            file.loc[index,'Web_Verified'] = 'Incorrect'

    ##########################################################################################

    def email_validation(file, index, row, email):
                 
        email_regex = re.compile(r"^\w{1,}(-)?(\.)?\w{0,}@\w{1,}(-)?(\w{1,})?(\.\w{2,3})(\.\w{2})?$")
                       
        if pd.isna(row[email]) == True or row[email] == 'nan':
                
                file.loc[index,'Email_Verified'] = 'Null Value'

        elif email_regex.match(str(row[email])):
                    
                file.loc[index,'Email_Verified'] = 'Correct'
                                                   
        else:
                    
            file.loc[index,'Email_Verified'] = 'Incorrect'


    ###########################################################################################

    def Gdf_FeatCode_validation(file,index,row,catcode):
        
        Cat_SubCat = pd.read_excel(r'Lists\Categories_Subcategories.xlsx')
        file[catcode] = file[catcode].astype(str)
        Cat_SubCat['CAT_CODE'] = Cat_SubCat['CAT_CODE'].astype(str)
                
        
        status = False
        if pd.isna(row[catcode]) == True or row[catcode] == 'nan':
                
            file.loc[index,'Gdf_FeatCode_Verified'] = 'Null Value'
            status = True
                
        else:
            for i,cat in Cat_SubCat.iterrows():
                
                if status == True: continue
                
                if (file.loc[index,catcode]).split('.')[0] == cat['CAT_CODE']:
                    
                    file.loc[index,'Gdf_FeatCode_Verified'] = 'Correct'
                    status = True


                elif status == False and Cat_SubCat['CAT_CODE'].iloc[-1]:
                    
                    file.loc[index,'Gdf_FeatCode_Verified'] = 'Incorrect'

    ############################################################################################

    def Gdf_FeatName_validation(file,index,row,catname,catcode):
        
        Cat_SubCat = pd.read_excel(r'Lists\Categories_Subcategories.xlsx')
        
        file[catname] = file[catname].astype(str)
        
        Cat_SubCat['CAT_NAME'] = Cat_SubCat['CAT_NAME'].astype(str)
        
        file[catcode] = file[catcode].astype(str)
        
        Cat_SubCat['CAT_CODE'] = Cat_SubCat['CAT_CODE'].astype(str)
                
       
        status = False
        if pd.isna(row[catname]) == True or row[catname] == 'nan':
                
            file.loc[index,'Gdf_FeatName_Verified'] = 'Null Value'
            status = True
                
        else:
            for i,cat in Cat_SubCat.iterrows():
                if status == True: continue
                    
                if file.loc[index,catname] == Cat_SubCat.loc[i,'CAT_NAME'] and (file.loc[index,catcode]).split('.')[0] == Cat_SubCat.loc[i,'CAT_CODE']:
                        
                    file.loc[index,'Gdf_FeatName_Verified'] = 'Correct'
                    
                    status = True
                        

                elif status == False and Cat_SubCat.loc[i,'CAT_NAME'] == Cat_SubCat['CAT_NAME'].iloc[-1]:
                    file.loc[index,'Gdf_FeatName_Verified'] = 'Incorrect'


    ################################################################################################

    def Gdf_SubCatCode_validation(file,index,row,subcatcode,catcode):
        
        Cat_SubCat = pd.read_excel(r'Lists\Categories_Subcategories.xlsx')
       
        
        file[catcode] = file[catcode].astype(str)
        Cat_SubCat['CAT_CODE'] = Cat_SubCat['CAT_CODE'].astype(str)
        file[subcatcode] = file[subcatcode].astype(str)
        Cat_SubCat['SUBCAT_CODE'] = Cat_SubCat['SUBCAT_CODE'].astype(str)
        subcat_list = Cat_SubCat['SUBCAT_CODE'].tolist()
        subcat_list_corrected = [i.replace('.0','') for i in subcat_list]
        status = False

        if pd.isna(row[subcatcode]) == True or row[subcatcode] == 'nan':
                
            file.loc[index,'Gdf_SubCatCode_Verified'] = 'Null Value'
            
            status = True
            pass
                        

        elif file.loc[index,subcatcode].split('.')[0] in subcat_list_corrected and (file.loc[index,subcatcode]).split('.')[0][:4] == file.loc[index,catcode].split('.')[0]:
                                
            file.loc[index,'Gdf_SubCatCode_Verified'] = 'Correct'
            
            status = True
            
          
        elif status == False:
                            
            file.loc[index,'Gdf_SubCatCode_Verified'] = 'Incorrect'

    ##############################################################################################

    def Gdf_SubCatName_validation(file,index,row,subcatname,subcatcode):
        
        Cat_SubCat = pd.read_excel(r'Lists\Categories_Subcategories.xlsx')
        
        file[subcatcode] = file[subcatcode].astype(str)
        Cat_SubCat['SUBCAT_CODE'] = Cat_SubCat['SUBCAT_CODE'].astype(str)
        file[subcatname] = file[subcatname].astype(str)
                
        status = False
        if pd.isna(row[subcatname]) == True or row[subcatname] == 'nan':
                
            file.loc[index,'Gdf_SubCatName_Verified'] = 'Null Value'
            status = True
                
        else:
            for i,cat in Cat_SubCat.iterrows():
                
                if status == True: continue

                if file.loc[index,subcatname] == Cat_SubCat.loc[i,'SUBCAT_NAME'] and (file.loc[index,subcatcode]).split('.')[0] == Cat_SubCat.loc[i,'SUBCAT_CODE'].split('.')[0]:
                        
                    file.loc[index,'Gdf_SubCatName_Verified'] = 'Correct'
                    status = True
                        

                elif status == False and Cat_SubCat.loc[i,'SUBCAT_CODE'] == Cat_SubCat['SUBCAT_CODE'].iloc[-1]:
                    file.loc[index,'Gdf_SubCatName_Verified'] = 'Incorrect'

    ##################################################################################################

    def language_validation(file,index,row,language,language_notation):
        
        
        for index,row in file.iterrows():
            
            if pd.isna(row[language]) == True or row[language] == 'nan':
                
                file.loc[index,'Language_Verified'] = 'Null Value'
            
            elif row[language] == language_notation.split('.')[0]:
                
                file.loc[index,'Language_Verified'] = 'Correct'
                
            else:
                file.loc[index,'Language_Verified'] = 'Incorrect'

    #################################################################################################

    '''Cria uma coluna com o nome do Source com todas as primeiras letras das palavras em Maiusculo, 
      Ex: agencia de turismo --> Agencia De Turismo

    Após isso,substitui as preposicoes com inicio maiusculo por inicio minusculo, Ex: De ---> de

    Por fim, compara a coluna original com a coluna normalizada e na coluna de verificação, se tiverem iguais está Correto,
    se não, está Incorreto
    '''
    def Source_validation(file, index, row, source):
        
        file['Source_Capitalized'] = ''

        numeros = re.compile(r'^[0-9]+$') # identifica se a linha possui só numeros, pq se possuir tá errado

        file[source] = file[source].astype(str)
        file['Source_Verified'] = file['Source_Verified'].astype(str)

        if pd.isna(file.loc[index,source]) == True or file.loc[index,source] == 'nan':
            
            file.loc[index,'Source_Verified'] = "Null Value"
            
            pass

        elif numeros.match(str(row[source])):
            
            file.loc[index,'Source_Verified'] = 'Incorrect'
            
            pass

        else:
            file.loc[index,'Source_Capitalized'] = file.loc[index,source].title()

            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" De "," de ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Da "," da ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Do "," do ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Dos "," dos ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Das "," das ")    
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Em "," em ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" No "," no ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Na "," na ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Nos "," nos ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Nas "," nas ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" O "," o ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" A "," a ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" E "," e ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Por "," por ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Pelo "," pelo ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" D'"," d'")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Ii "," II ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Iii "," III ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Vi "," VI ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Xi "," XI ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Xv "," XV ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Iv "," IV ")
            file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(" Xxiii "," XXIII ")

            if file.loc[index,'Source_Capitalized'].split(' ')[-1] in ('Ii','Iii','Vi','Xi','Iv','Xx', 'Xxiii','Xv'):

                file.loc[index,'Source_Capitalized'] = file.loc[index,'Source_Capitalized'].replace(file.loc[index,'Source_Capitalized'].split(' ')[-1],file.loc[index,'Source_Capitalized'].split(' ')[-1].upper())

            if file.loc[index,'Source_Capitalized'] == file.loc[index,source]:

                file.loc[index,'Source_Verified'] = 'Correct'

            else:
                file.loc[index,'Source_Verified'] = 'Incorrect'
                    
        file.drop('Source_Capitalized', axis=1, inplace=True)
        
    ###############################################################################################

    def LATITUDE_LONGITUDE_Validation(file, index, row, latitude, longitude):
        
        LAT_LONG_BadPrecision = re.compile(r'^(-)?[0-9]{1,2}.[0-9]{0,4}$')    
        LAT_LONG = re.compile(r'^(-)?[0-9]{1,2}.[0-9]{5,}$')
              

        if pd.isna(row[longitude]) == True or row[longitude] == 'nan':

                file.loc[index,'Longitude_Verified'] = 'Null Value'

        elif LAT_LONG_BadPrecision.match(str(row[longitude])):

                file.loc[index,'Longitude_Verified'] = 'Longitude with low precision'         
                    
        elif LAT_LONG.match(str(row[longitude])):

                file.loc[index,'Longitude_Verified'] = 'Correct'

        else:

                file.loc[index,'Longitude_Verified'] = 'Incorrect'
 
        if pd.isna(row[latitude]) == True or row[latitude] == 'nan':

            file.loc[index,'Latitude_Verified'] = 'Null Value'

        elif LAT_LONG_BadPrecision.match(str(row[latitude])):

            file.loc[index,'Latitude_Verified'] = 'Latitude with low precision' 
                    
        elif LAT_LONG.match(str(row[latitude])):
            
            file.loc[index,'Latitude_Verified'] = 'Correct'

        else:

            file.loc[index,'Latitude_Verified'] = 'Incorrect'

    ######################################################################################################

    def ta_reverse_validation(file, index, row,ta_reverse):
        
        file[ta_reverse] = file[ta_reverse].astype(str)
        
        
        ano = str(datetime.date.today().year)[-2:]
        
        file.loc[index,ta_reverse] = file.loc[index,ta_reverse].split('.')[0]
        
        if file.loc[index,ta_reverse] == ano:
            
            file.loc[index,'Ta_Reverse_Verified'] = 'Correct'

        elif pd.isna(file.loc[index,ta_reverse]) == True or file.loc[index,ta_reverse] == 'nan':

            file.loc[index,'Ta_Reverse_Verified'] = 'Null Value'

        else:
            
            file.loc[index,'Ta_Reverse_Verified'] = 'Incorrect'

    #######################################################################################################
