import requests
import pandas as pd
import json

class YardResponses:

    def __init__(self, language=None, country=None):

        self.status_code = self.get_yard_status()

        self.language = language
        self.country = country

        try:
            self.yard_version = self.get_yard_version()
            self.yard_tag_version = self.get_tag_version()

            self.yard_url = 'http://yard.tomtomgroup.com/yard-webservice/{}/references?'.format(self.yard_version)
        
        except:
            print('Problem with YARD API')

    def get_yard_info(self):

        bad_words_regex = self.get_regex_bad_words()
        prefix_regex = self.get_regex_prefix()
        allowed_char_regex = self.get_regex_allowed_char()

        return bad_words_regex, prefix_regex, allowed_char_regex

    def get_yard_status(self):

        yard_url = 'http://yard.tomtomgroup.com/yard-webservice/sysinfo'
        yard_status = False
        try:
            yard_response = requests.get(yard_url).status_code
            yard_status = True
        except:
            messagebox.showerror('Problem connecting to the YARD API', 'Please, make sure VPN is properly connected.')
        
        return yard_status

    def get_yard_version(self):

        yard_sysinfo_url = 'http://yard.tomtomgroup.com/yard-webservice/sysinfo'
        sysinfo_response = requests.get(yard_sysinfo_url).text

        start_index = sysinfo_response.find('Yapi: ')
        end_index   = sysinfo_response.find('TagService')

        list_version = sysinfo_response[start_index:end_index]
        list_version_formatted = list_version.replace('Yapi: ', '').replace('\n\t', '').replace('[', '').replace(']', '').split(',')

        current_yard_version = max(list_version_formatted)

        return current_yard_version

    def get_tag_version(self):

        # ** Master branch id to use on yard_taginfo_url: '233b38a4-f0bf-4289-bfdc-7f2a04fc4ab3'
        yard_taginfo_url = 'http://qasup-rprod-cpp-r2.flatns.net/ap-mediator-ws/branchids/233b38a4-f0bf-4289-bfdc-7f2a04fc4ab3/types/YARD_TAG/tag'
        yard_tag_response = requests.get(yard_taginfo_url).text
        yard_tag_json = json.loads(yard_tag_response)

        yard_tag_version = yard_tag_json['name']

        return yard_tag_version

    def get_regex_bad_words(self):

        #! It will be return a ReGex statement with bad words to be used in the processing part
        yard_method = 'String has invalid Name Part'
        specific_info = 'scopetype=LanguageNotation&scopeadminkey={}&referencetype={}&referencetagname={}'.format(self.language,yard_method, self.yard_tag_version)
        yard_call = '{}{}'.format(self.yard_url, specific_info)

        yard_bad_words_response = requests.get(yard_call).text
        yard_bad_words_json = json.loads(yard_bad_words_response)

        list_bad_words = yard_bad_words_json['features'][2]['properties']['Invalid Name Part']
        lowercase_list_bad_words = [element.lower() for element in list_bad_words]

        #bad_words_regex = '|'.join(lowercase_list_bad_words)

        return lowercase_list_bad_words 
    
    def get_regex_telephone_number(self):
        yard_method = 'Feature with Telephone Number has allowed Telephone Number syntax'
        specific_info = 'scopetype=Country&scopeadminkey={}&referencetype={}&referencetagname={}'.format(self.country,yard_method, self.yard_tag_version)
        yard_call = '{}{}'.format(self.yard_url, specific_info)
        
        yard_telephone_number_response = requests.get(yard_call).text
        yard_telephone_number_json = json.loads(yard_telephone_number_response)

        telephone_number_regex_list = yard_telephone_number_json['features'][2]['properties']['Telephone Number syntax']
        telephone_regex = ''.join(telephone_number_regex_list)
        
        return telephone_regex
    
    def get_regex_postal_code(self):
        yard_method = 'Feature with Postal Code Information has allowed Postal Code syntax'
        specific_info = 'scopetype=Country&scopeadminkey={}&referencetype={}&referencetagname={}'.format(self.country,yard_method, self.yard_tag_version)
        yard_call = '{}{}'.format(self.yard_url, specific_info)
        
        yard_postal_code_response = requests.get(yard_call).text
        yard_postal_code_json = json.loads(yard_postal_code_response)

        main_postal_regex = yard_postal_code_json['features'][2]['properties']['Composite Postal Code syntax'][5]['Main Postal Code'].replace('$','')
        separator_postal_regex = yard_postal_code_json['features'][2]['properties']['Composite Postal Code syntax'][5]['Main Sub Separator'].replace('^','').replace('$','')
        sub_postal_regex = yard_postal_code_json['features'][2]['properties']['Composite Postal Code syntax'][5]['Sub Postal Code'].replace('^','')
        
        
        total_postal_code = str(main_postal_regex)+str(separator_postal_regex)+str(sub_postal_regex)

        
        return total_postal_code
    
    def get_stn_allowed_preffix_suffix(self):

        #! It will be return a ReGex statement with allowed characters to be used in the processing part
        yard_method = 'Name has allowed normalized Name Component Type Prefix or Suffix'
        specific_info = 'scopetype=LanguageNotation&scopeadminkey={}&referencetype={}&referencetagname={}'.format(self.language,yard_method, self.yard_tag_version)
        yard_call = '{}{}'.format(self.yard_url, specific_info)

        yard_stn_allowed_preffix_suffix_response = requests.get(yard_call).text
        yard_stn_allowed_preffix_suffix_json = json.loads(yard_stn_allowed_preffix_suffix_response)

        list_stn_allowed_preffix_suffix = yard_stn_allowed_preffix_suffix_json['features'][2]['properties']['Composite Normalized Name']#['Output-Normalized value']
        list_normalized_values = [value['Output-Normalized value'] for value in list_stn_allowed_preffix_suffix]
        lowercase_normalized_values = [element.lower() for element in list_normalized_values]
        list_normalized_values.extend(lowercase_normalized_values)

        #stn_allowed_preffix_suffix_regex = '|'.join(lowercase_normalized_values)

        return list_normalized_values

    def get_notation_alphabet_value(self):
        
        yard_method = 'Country has House Number Range Notation Alphabet'
        specific_info = 'scopetype=Country&scopeadminkey={}&referencetype={}&referencetagname={}'.format(self.country,yard_method, self.yard_tag_version)
        yard_call = '{}{}'.format(self.yard_url, specific_info)
        
        yard_notation_alphabet_response = requests.get(yard_call).text
        yard_notation_alphabet_json = json.loads(yard_notation_alphabet_response)

        hsn_notation_alphabet_list = yard_notation_alphabet_json['features'][2]['properties']['Notation Alphabet']
        hsn_notation_alphabet = ''.join(hsn_notation_alphabet_list)
        
        return hsn_notation_alphabet
    
    def get_hsn_valid_characters(self, notation_code):
        
        yard_method = 'Notation Alphabet has allowed House Number Character'
        specific_info = 'scopetype=Notation Alphabet&scopeadminkey={}&referencetype={}&referencetagname={}'.format(notation_code,yard_method, self.yard_tag_version)
        yard_call = '{}{}'.format(self.yard_url, specific_info)
        
        yard_hsn_response = requests.get(yard_call).text
        yard_hsn_json = json.loads(yard_hsn_response)

        hsn_valid_characters_list = yard_hsn_json['features'][2]['properties']['Allowed House Number Character']
       #hsn_valid_characters = ''.join(hsn_valid_characters_list)
        
        return hsn_valid_characters_list

