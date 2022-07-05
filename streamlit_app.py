import streamlit as st
import pandas as pd
from POI_QC_Tool import Verificator
import time
from name_service import NameService
from yard_api import YardResponses


title = st.title('POI Quality Check Tool')
st.sidebar.title('Description:')


st.sidebar.write(
    '''This tool works as a Quality Check of POI data, analyzing and identifying the errors present in the file and mapping it.


    Developed by:
    Alexandre Lombardo Montanha - GSA
    Local Intelligence Americas'''
)
 
file = st.file_uploader("Please insert a .csv POI file to be analyzed: ")

if file and file.type != 'text/csv':

    raise ValueError('File is not valid. Please insert a .csv file')

elif file and file.type == 'text/csv':
    
    df = pd.read_csv(file)
    st.dataframe(df.head(20))

    
    
        

    language_notation = st.text_input('Insert Language with Language Notation: ')

    country_code = st.text_input('Insert Country Code: ')
        
    output_file_name = st.text_input('Please insert the output file name ending with ".csv"')


    st.subheader('Field Mapping')

    
        
    poi_yes_no = st.radio(
        "Analyze poi_id?",
        (True,False), key='poi')
        
    poi_id = st.selectbox(
        label = 'POI ID',
        options = df.columns,
        disabled = not(bool(poi_yes_no)))
        
    company_name_yes_no = st.radio(
        "Analyze company name?",
        (True,False), key='company')
        
    company_name = st.selectbox(
        'COMPANY NAME',
        df.columns,
        disabled = not(bool(company_name_yes_no)))
        
    street_yes_no = st.radio(
        "Analyze street name?",
        (True,False),key='street')
        
    street = st.selectbox(
        'STREET',
        df.columns,
        disabled = not(bool(street_yes_no)))

    hsn_yes_no = st.radio(
        "Analyze hsn?",
        (True,False),key='hsn')
        
    hsn = st.selectbox(
        'HOUSE NUMBER',
        df.columns,
        disabled = not(bool(hsn_yes_no)))
    
    postal_code_yes_no = st.radio(
        "Analyze postal code?",
        (True,False),key='postal')
        
    postal_code = st.selectbox(
        'POSTAL CODE',
        df.columns,
        disabled = not(bool(postal_code_yes_no)))
        
    neighborhood_yes_no = st.radio(
        "Analyze neighborhood?",
        (True,False),key='neighborhood')
        
    neighborhood = st.selectbox(
        'NEIGHBORHOOD',
        df.columns,
        disabled = not(bool(neighborhood_yes_no)))
        
    city_yes_no = st.radio(
        "Analyze city name?",
        (True,False),key='city')
        
    city = st.selectbox(
        'CITY',
        df.columns,
        disabled = not(bool(city_yes_no)))

    state_yes_no = st.radio(
        "Analyze state?",
        (True,False),key='state')

    state = st.selectbox(
        'STATE',
        df.columns,
        disabled = not(bool(state_yes_no)))
    
    country_yes_no = st.radio(
        "Analyze country?",
        (True,False),key='country')
        
    country = st.selectbox(
        'COUNTRY',
        df.columns,
        disabled = not(bool(country_yes_no)))


    phone_yes_no = st.radio(
        "Analyze phone number?",
        (True,False),key='phone1')
        
    phone = st.selectbox(
        'PHONE NUMBER',
        df.columns,
        disabled = not(bool(phone_yes_no)))

    web_yes_no = st.radio(
        "Analyze web?",
        (True,False),key='web')

    web = st.selectbox(
        'WEBSITE',
        df.columns,
        disabled = not(bool(web_yes_no)))

    email_yes_no = st.radio(
        "Analyze email?",
        (True,False),key='email')

    email = st.selectbox(
        'EMAIL',
        df.columns,
        disabled = not(bool(email_yes_no)))
  
    catcode_yes_no = st.radio(
        "Analyze category code?",
        (True,False),key='catcode')
        
    catcode = st.selectbox(
        'CATEGORY CODE',
        df.columns,
        disabled = not(bool(catcode_yes_no)))

    catname_yes_no = st.radio(
        "Analyze category name?",
        (True,False),key='catname')
        
    catname = st.selectbox(
        'CATEGORY NAME',
        df.columns,
        disabled = not(bool(catname_yes_no)))

    subcatcode_yes_no = st.radio(
        "Analyze subcategory code?",
        (True,False),key='subcatcode')
        
    subcatcode = st.selectbox(
        'SUBCATEGORY CODE',
        df.columns,
        disabled = not(bool(subcatcode_yes_no)))

    subcatname_yes_no = st.radio(
        "Analyze subcategory name?",
        (True,False),key='subcatname')
        
    subcatname = st.selectbox(
        'SUBCATEGORY NAME',
        df.columns,
        disabled = not(bool(subcatname_yes_no)))

    language_yes_no = st.radio(
        "Analyze language?",
        (True,False),key='language')
        
    language = st.selectbox(
        'LANGUAGE CODE',
        df.columns,
        disabled = not(bool(language_yes_no)))
        
    source_yes_no = st.radio(
        "Analyze source name?",
        (True,False),key='source')
        
    source = st.selectbox(
        'SOURCE NAME',
        df.columns,
        disabled = not(bool(source_yes_no)))

    lat_long_yes_no = st.radio(
        "Analyze latitude and longitude?",
        (True,False),key='lat_long')
        
    latitude = st.selectbox(
        'LATITUDE',
        df.columns,
        disabled = not(bool(lat_long_yes_no)))
        
    longitude = st.selectbox(
        'LONGITUDE',
        df.columns,
        disabled = not(bool(lat_long_yes_no)))
        
    ta_reverse_yes_no = st.radio(
        "Analyze ta_reverse info?",
        (True,False),key='ta_reverse')
        
    ta_reverse = st.selectbox(
        'TA_REVERSE',
        df.columns,
        disabled = not(bool(ta_reverse_yes_no)))


    run_button = st.button('Run POI Verification Tool')

    st.write('All the columns are being analyzed and the file will be ready in a few minutes')
    

    if run_button:
        Verificator.Yard_API(language_notation,country_code)

    

        if poi_yes_no == True:    
            df['POI_ID_Verified'] = ''
            
        if company_name_yes_no == True:
            df['CompanyName_Verified'] = ''
            df['CompanyName_Capitalized'] = ''
            
        if street_yes_no == True:
            df['Street_Verified'] = ''
            
        if hsn_yes_no == True:
            df['HSN_Verified'] = ''
            
        if postal_code_yes_no == True:
            df['CEP_Verified'] = ''
            
        if neighborhood_yes_no == True:
            df['Neighborhood_Verified'] = ''
            
        if city_yes_no == True:
            df['City_Verified'] = ''
            
        if state_yes_no == True:
            df['State_Verified'] = ''
            
        if country_yes_no == True:
            df['Country_Verified'] = ''
            
        if phone_yes_no == True:
            df['Phone_Number_Verified'] = ''
            
        if web_yes_no == True:
            df['Web_Verified'] = ''
            
        if email_yes_no == True:
            df['Email_Verified'] = ''
            
        if catcode_yes_no == True:
            df['Gdf_FeatCode_Verified'] = ''
            
        if catname_yes_no == True:
            df['Gdf_FeatName_Verified'] = ''
            
        if subcatcode_yes_no == True:
            df['Gdf_SubCatCode_Verified'] = ''
            
        if subcatname_yes_no == True:
            df['Gdf_SubCatName_Verified'] = ''
        
        if language_yes_no == True:
            df['Language_Verified'] = ''
        
        if source_yes_no == True:
            df['Source_Verified'] = ''
            
        if lat_long_yes_no == True:
            df['Latitude_Verified'] = ''
            df['Longitude_Verified'] = ''
            
        if ta_reverse_yes_no == True:
            df['Ta_Reverse_Verified'] = ''
  
            
        my_bar = st.progress(0)
        message = st.empty()
        length = len(df) - 1
        start_time = time.time()
            
        for index,row in df.iterrows():
                
    
                 
            if poi_yes_no == True:
                
                Verificator.POI_ID_validation(df, index, row, poi_id)
                
            if company_name_yes_no == True:
                
                Verificator.CompanyName_validation(df, index, row,company_name)

            if street_yes_no == True:
                
                Verificator.STREET_Validation(df, index, row,language_notation,country_code,street)
                
            if hsn_yes_no == True:
                
                Verificator.HSN_validation(df,index, row,language_notation,country_code,hsn)
                    
            if postal_code_yes_no == True:
                
                Verificator.CEP_validation(df, index, row, language_notation, country_code,postal_code)
 
            if neighborhood_yes_no == True:
                
                Verificator.Neighborhood_validation(df, index, row,neighborhood)
                
            if city_yes_no == True:
                
                Verificator.City_validation(df, index, row, city)
                
            if state_yes_no == True:
                
                Verificator.State_validation(df, index, row, state)
                
            if country_yes_no == True:
                
                Verificator.country_validation(df,index, row, country_code, country)
                
            if phone_yes_no == True:
                
                Verificator.phone_validation(df,index, row, phone, language_notation, country_code)

            if web_yes_no == True:
                
                Verificator.web_validation(df, index, row, web)

            if email_yes_no == True:
                
                Verificator.email_validation(df, index, row, email)
                    
            if catcode_yes_no == True:
                
                Verificator.Gdf_FeatCode_validation(df, index, row,catcode)
                
            if catname_yes_no == True:
                
                Verificator.Gdf_FeatName_validation(df, index, row,catname,catcode)
                
            if subcatcode_yes_no == True:
                
                Verificator.Gdf_SubCatCode_validation(df, index, row, subcatcode,catcode)
                
            if subcatname_yes_no == True:
                
                Verificator.Gdf_SubCatName_validation(df, index, row,subcatname,subcatcode)
                
            if language_yes_no == True:
                
                Verificator.language_validation(df,index,row,language,language_notation)
                
            if source_yes_no == True:
                
                Verificator.Source_validation(df, index, row, source)
                
            if lat_long_yes_no == True:
                
                Verificator.LATITUDE_LONGITUDE_Validation(df, index, row, latitude, longitude)
                    
            if ta_reverse_yes_no == True:
                
                Verificator.ta_reverse_validation(df, index, row,ta_reverse)
                

            
                
                
            my_bar.progress(index/len(df))

            message.info(f'{index} of {length} rows were already analyzed!')

                            

        output_file = df.to_csv(index=False)
        my_bar.progress((index/len(df))+(1-index/len(df)))
        time_difference = (time.time() - start_time)/60
        #st.write("--- {} minutes ---".format(time_difference))
                  
        st.download_button(
            label="⬇️ Download data analyzed as CSV",
            data=output_file,
            file_name=output_file_name,
            mime='text/csv'
            )
