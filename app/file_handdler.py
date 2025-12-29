# for file handling
import json 
import pickle

# external
from app_utils import is_continue,gtpass ,MAX_ATTEMPTS
  
def json_handdler(mode:str,config_name:str ,config_dict:dict[str,str] = {}):
    '''
        Handdels config.json file creates if not present 
        [**must specify config_dict incase of update**]

        Args:
            Mode : [load/update] "load to get configrations_dict desired" OR "update to create or change the config_dict"
            Config_name : "config_name" the name for the cofig to load from the json file or name of config to update into json file 
            Config_dict :{"config_name":{"config1":"value1"}}  dictionary for json [**in case of mode = 'update' only**]
        Returns:
            Config_dict :{"config1":"value1"} "new_config_dict if updated or desired config_dict if loaded"
        Exceptions:
            RuntimeError : if any error during handling occured
        Examples:
            json_handdler(mode='update', config_name = 'USER_CONFIG', config_dict={"hello":"hello@123"}) 
    '''
    try : 
        # if load was requested
        if mode == 'load':
            
            with open('app_config.json' , 'r') as f :
                content_dict = json.load(f)
                config_dict = content_dict[config_name]  # extracts the desired config from the  parent dict
            return config_dict 
        # if update was requested and config_dict is provided 
        elif mode == 'update' and config_dict != {}:
            # if app_config.json exists 
            with open('app_config.json' , 'r+') as f :
                parent_dict = json.load(f)
                parent_dict[config_name] = config_dict  # updating the configrations desired

                # heading back to the start of file 
                f.seek(0)
                f.truncate()

                # updating configs back to file
                json.dump(parent_dict,f,indent=4)
            return config_dict # sending the dict back after updation for consistency
        
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
            with open('app_config.json','w') as f:
                parent_dict = {config_name:config_dict} # creating a json file 
                json.dump(parent_dict,f,indent=4)
            return config_dict

    except KeyError as e :
        raise RuntimeError("invalid Configrations requested make sure config_name is correctly given") 


def pwd_handdler(mode:str,user:str,pwd:str =''):
    '''
        Handdels pwd.dat file creates if not present 
        [**must specify pwd incase of update**]

        Args:
            Mode : [load/update] "load to get pwd_dict desired" OR "update to create or change the pwd_dict"
            User : "user" the name for the user whose pwd is to be loaded  or whose pwd is to be updated  
            Pwd  : pwd of the user to update in the file [**in case of update only**]
        Returns:
            pwd: "pwd_str" or "new_pwd_str if updated or desired pwd if loaded"
        Exceptions:
            RuntimeError : if any error during handling occured
        Examples:
            pwd_handdler(mode='update', user = 'user_name',pwd = 'pwd@123') 
    '''
    try : 
        # if load was requested  
        if mode == 'load':
            
            with open('pwd.dat' , 'rb') as f :
                pwd_dict  = pickle.load(f)
                pwd = pwd_dict[user]  # extracts the pwd for desired user  from the pwd_dict
            return pwd 
        # if update was requested and pwd is provided  
        elif mode == 'update' and pwd != '':
            # if app_config.json exists 
            with open('pwd.dat' , 'rb+') as f :
                pwd_dict = pickle.load(f)
                pwd_dict[user] = pwd  # updating the pwd for  desired user

                # heading back to the start of file 
                f.seek(0)
                f.truncate()

                # updating configs back to file
                pickle.dump(pwd_dict,f)
            return pwd # sending the pwd back after updation for consistency
        
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
            return pwd

    except KeyError as e :
        raise RuntimeError(f"invalid Configrations requested {e}") 

def session_handdler(mode:str,session_dict:dict[str,str] = {}) -> dict[str,str]:
    '''
        Handdels session.dat file creates if not present  
        [**must specify session_dict incase of update**]

        Args:
            Mode : [load/update] "load to get session_dict desired" OR "update to create or change the session_dict"
            session_dict : **{'host'='','user'='','pwd'='','db'=''}**  dict of configraions for saving in this session [**in case of update only**]
        Returns:
            dict[str,str]: "session_str" or "new_session_str if updated or desired session if loaded"
        Exceptions:
            RuntimeError : if any error during handling occured
        Examples:
            session_handdler(mode='update',session_dict = {host='localhost',user='current_user',pwd='current_user@123' , db='current_db') 
    '''
    try : 
        # if load was requested  
        if mode == 'load':
            
            with open('session.dat' , 'rb') as f :
                current_session_dict  = pickle.load(f)
            return current_session_dict 
         
        # if update was requested and session is provided  
        elif mode == 'update' and session_dict != {}:
            # if session.dat exists 
            with open('session.dat' , 'rb+') as f :

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
                    return session_dict # sending the session back after updation for consistency
                else : 
                    raise RuntimeError("Session Updation Failed | Previous Session State Restored")
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
            with open('session.dat','wb') as f:
                pickle.dump(session_dict,f)
            return session_dict

    except KeyError as e :
        raise RuntimeError("invalid Configrations requested make sure session_dict is correctly given") 

# if __name__ == "__main__":
#     try:
#         # pwd testing
#         pwd = pwd_handdler('load','root')
#         print(pwd)
#         print(pwd_handdler('update','testuser','Test.com@user'))
#         # session testing 
#         print(session_handdler('load'))
#         print(session_handdler('update',{'host':'localhost','user':'tanmay','pwd':'SecurePass@1201','db':'medilink'}))
#         # json testing 
#         print(json_handdler('load','APP_CONFIG'))
#         print(json_handdler('update','APP_CONFIG',{'APP_NAME':'MEDILINK','AUTHOR':'TANMAYSRI'}))
#     except Exception as e :
#         print("error occured :" , e)

