# for file handling
import json 
import pickle
import os
# external
from handdlers.utils_handdler import is_continue , config_path
  
def json_handdler(mode:str, config_name:str='',config_dict:dict[str,str] = {},load_all:bool = False ):
    '''
        Handdels config.json file creates if not present 
        [**must specify config_dict incase of update**]

        Args:
            Mode : [load/update/create] "load to get configrations_dict desired" OR "update to create or change the config_dict"
            Load_all: True for loading whole json else false[**use all in case of laoding whole json**] [**in case of load mode only**]
            Config_name : "config_name" the name for the cofig to load from the json file or name of config to update into json file [**in case of load/update only**] 
            Config_dict :{"config_name":{"config1":"value1"}}  dictionary for json [**in case of mode = 'update' only**]
        Returns:
            Config_dict :{"config1":"value1"} "new_config_dict if updated or desired config_dict if loaded"
        Exceptions:
            RuntimeError : if any error during handling occured
        Examples:
            json_handdler(mode='update', config_name = 'USER_CONFIG', config_dict={"hello":"hello@123"}) 
    '''
    json_path = config_path('app_config.json')
    try : 
        # if load was requested for whole json file 
        if mode == 'load'and load_all :
            with open(json_path,'r') as  f :
                config_dict =  json.load(f) 
            return config_dict
        # if load was requested for specific json config 
        elif mode == 'load' and not load_all:
            with open(json_path , 'r') as f :
                content_dict = json.load(f)
                config_dict = content_dict[config_name]  # extracts the desired config from the  parent dict
            return config_dict 
        # if update was requested and config_dict is provided 
        elif mode == 'update' and config_dict != {}:
            # if app_config.json exists 
            with open(json_path , 'r+') as f :
                parent_dict = json.load(f)
                parent_dict[config_name] = config_dict  # updating the configrations desired

                # heading back to the start of file 
                f.seek(0)
                f.truncate()

                # updating configs back to file
                json.dump(parent_dict,f,indent=4)
            return config_dict # sending the dict back after updation for consistency
        elif mode == 'create':
            # creating empty config file 
            with open(json_path,'w') as f:
                # default json data
                json_data = {
                                'APP_CONFIG':{
                                    'app_name':'MediLink',
                                    'app_admin':'medilink_admin',
                                    'app_desc':'an app for everyone',
                                    'app_tagline': 'Links Tech To Med',
                                    'app_db' : 'medilink',
                                    'host' : 'localhost',
                                    'author' : 'tanmaySrivastava'
                                    
                                },
                                'AUTHOR_CONFIG':{
                                    'name':'Tanmay Srivastava',
                                    'email': 'tscreateandcare+medilink@gmail.com',
                                    'designation':'Student Developer',
                                    'desc':'A Coding Entusiast',
                                    'phone':'+91 0000000000'
                                }
                            }   
                json.dump(json_data,f,indent=4)
            return {}
        # if wrong mode is requested or no requied param is given 
        else :
            raise RuntimeError("Wrong Mode Requested or No Required Parameter  is Given * Make Sure config_dict is given in case of update")
        
    except (FileNotFoundError , EOFError) :

        # if we have to load 
        if mode == 'load' : 
            raise RuntimeError("Configuration file 'app_config.json' is missing or corrupted. Please run 'python setup.py' to configure the application.")
        # if mode = update
        else : 
            print("Config file is missing, creating it...")
            with open(json_path,'w') as f:
                parent_dict = {config_name:config_dict} # creating a json file 
                json.dump(parent_dict,f,indent=4)
            return config_dict

    except KeyError as e :
        raise RuntimeError("invalid Configrations requested make sure config_name is correctly given") 


def pwd_handdler(mode:str,user:str='',pwd:str ='') -> str:
    '''
        Handdels pwd.dat file creates if not present 
        [**must specify pwd incase of update**]

        Args:
            Mode : [load/update/create] "load to get pwd_dict desired" OR "update to create or change the pwd_dict"
            User : "user" the name for the user whose pwd is to be loaded  or whose pwd is to be updated [**in case of load/update only**] 
            Pwd  : pwd of the user to update in the file [**in case of update only**]
        Returns:
            pwd: "pwd_str" or "new_pwd_str if updated or desired pwd if loaded"
        Exceptions:
            RuntimeError : if any error during handling occured
        Examples:
            pwd_handdler(mode='update', user = 'user_name',pwd = 'pwd@123') 
    '''
    pwd_path = config_path('pwd.dat')
    try : 
        # if load was requested  
        if mode == 'load':
            with open(pwd_path, 'rb') as f :
                pwd_dict  = pickle.load(f)
                pwd = pwd_dict[user]  # extracts the pwd for desired user  from the pwd_dict
            return pwd 
        # if update was requested and pwd is provided  
        elif mode == 'update' and pwd != '':
            os.chmod(pwd_path,0o600) # changing file permission back to writeable
            # if app_config.json exists 
            with open(pwd_path, 'rb+') as f :
                pwd_dict = pickle.load(f)
                pwd_dict[user] = pwd  # updating the pwd for  desired user

                # heading back to the start of file 
                f.seek(0)
                f.truncate()

                # updating configs back to file
                pickle.dump(pwd_dict,f)
            os.chmod(pwd_path,0o400) # read only
            return pwd # sending the pwd back after updation for consistency
        
        elif mode == 'create':
            # creating empty file for pwd 
            with open(pwd_path,'wb') as f :
                empty_pwd_data = {'sudo':'','root':''} # username:pwd
                pickle.dump(empty_pwd_data,f)
            os.chmod(pwd_path,0o400) # making file read only
            return ''


        # if wrong mode is requested or no requied param is given 
        else :
            raise RuntimeError("Wrong Mode Requested or No Required Parameter  is Given * Make Sure pwd is given in case of update")
        
    except (FileNotFoundError , EOFError) :

        # if we have to load 
        if mode == 'load' : 
            raise RuntimeError("Password file 'pwd.dat' is missing or corrupted. Please run 'python setup.py' to configure the application.")
        # if mode = update
        else : 
            print("Password file is missing, creating it...")
            with open('pwd.dat','wb') as f:
                pwd_dict = {user:pwd} # creating a json file 
                pickle.dump(pwd_dict,f)
            os.chmod(pwd_path,0o400) # making file read only             
            return pwd


    except KeyError as e :
        raise RuntimeError(f"invalid Configrations requested {e}") 

def session_handdler(mode:str,session_dict:dict[str,str] = {}) -> dict[str,str]:
    '''
        Handdels session.dat file creates if not present  
        [**must specify session_dict incase of update**]

        Args:
            Mode : [load/update/create] "load to get session_dict desired" OR "update to create or change the session_dict"
            session_dict : **{'host'='','user'='','pwd'='','db'=''}**  dict of configraions for saving in this session [**in case of update only**]
        Returns:
            dict[str,str]: "session_str" or "new_session_str if updated or desired session if loaded"
        Exceptions:
            RuntimeError : if any error during handling occured
        Examples:
            session_handdler(mode='update',session_dict = {host='localhost',user='current_user',pwd='current_user@123' , db='current_db') 
    '''
    session_path = config_path('session.dat')
    try : 
        # if load was requested  
        if mode == 'load':
            
            with open(session_path , 'rb') as f :
                current_session_dict  = pickle.load(f)
            return current_session_dict 
         
        # if update was requested and session is provided  
        elif mode == 'update' and session_dict != {}:

            os.chmod(session_path,0o600) # making file writeable           
            # if session.dat exists 
            with open(session_path , 'rb+') as f :

                current_session_dict = pickle.load(f)
                current_user = current_session_dict['user']
                
                print(f"Session Is Alredy Existing For Mysql User {current_user} | You Are About To Update It")
                # user want to update it 
                if is_continue():
                    # heading back to the start of file 
                    f.seek(0)
                    f.truncate()

                    # updating configs provided to the file 
                    pickle.dump(session_dict,f)                    
                else : 
                    raise RuntimeError("Session Updation Failed | Previous Session State Restored")
            
            os.chmod(session_path,0o400) # making file read only 
            return session_dict # sending the session back after updation for consistency
            
        elif mode == 'create':
            # creating empty session file 
            with open(session_path,'wb') as f :
                empty_session_data = {'host':'','user':'','pwd':'','db':''} # configname:value
                pickle.dump(empty_session_data,f)
            os.chmod(session_path,0o400) # making file read only 
            return empty_session_data
        # if wrong mode is requested or no requied param is given 
        else :
            raise RuntimeError("Wrong Mode Requested or No Required Parameter  is Given * Make Sure session_dict is given in case of update")
        
    except (FileNotFoundError , EOFError) :

        # if we have to load 
        if mode == 'load' : 
            raise RuntimeError("Session file 'session.dat' is missing or corrupted. Please run 'python setup.py' to configure the application.")
        # if mode = update
        else : 
            print("Session file is missing, creating it...")
            with open(session_path,'wb') as f:
                pickle.dump(session_dict,f)
            os.chmod(session_path,0o400) # making file read only 
            return session_dict

    except KeyError as e :
        raise RuntimeError("invalid Configrations requested make sure session_dict is correctly given") 

if __name__ == "__main__":
    try:
#         # pwd testing
#         # # pwd = pwd_handdler('load','root')
#         # pwd = pwd_handdler('load','root')
#         # print(pwd) 
#         # pwd = pwd_handdler('load','sudo')
#         # print(pwd)  
#         # pwd = pwd_handdler('load','admin')
#         # print(pwd)  
#         # print(pwd_handdler('update','testuser','Test.com@user'))
# #         # session testing 
# #         print(session_handdler('load'))
# #         print(session_handdler('update',{'host':'localhost','user':'tanmay','pwd':'SecurePass@1201','db':'medilink'}))
# #         # json testing 
        print(json_handdler('load' , load_all=True))
# #         print(json_handdler('update','APP_CONFIG',{'APP_NAME':'MEDILINK','AUTHOR':'TANMAYSRI'}))
#         # print(json_handdler('create'))
    except Exception as e :
        print("error occured :" , e)

