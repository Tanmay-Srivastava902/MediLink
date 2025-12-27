'''
    This Module Contains the Functions Required To For app configs 
'''
# importing modules 

# for path manuplation
import sys 
from pathlib import Path

# for mysql connection
from mysql.connector import connect , Error
from mysql.connector.errors import InterfaceError , ProgrammingError

# for file handling
import json 
import pickle

# changing the system path to use parent directory as base 
sys.path.append(str(Path(__file__).parent.parent))

#NOTE later move required utility to app_utils.py from parent and change the directory path for json back to the original
# imports form parent directory 
from utils import is_continue , gtpass
from constants import MAX_ATTEMPTS

def json_handdler(mode:str,config_name:str ,config_dict:dict[str,dict[str,str]] = {}):
    '''
        Handdels config.json file creates if not present 
        [**must specify config_dict incase of update**]

        Args:
            Mode : [load/update] "load to get configrations_dict desired" OR "update to create or change the config_dict"
            Config_name : "config_name" the name for the cofig to load from the json file or name of config to update into json file 
            Config_dict :{"config_name":{"config1":"value1"}}  dictionary for json [**in case of mode = 'update' only**]
        Returns:
            Config_dict :{"config_name":{"config1":"value1"}}  "new_config_dict if updated or desired config_dict if loaded"
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
                json.dump(parent_dict,f)
            return config_dict # sending the dict back after updation for consistency
        
        # if wrong mode is requested or no requied param is given 
        else :
            raise RuntimeError("Wrong Mode Requested or No Required Parameter  is Given * Make Sure config_dict is given in case of update")
        
    except (FileNotFoundError , EOFError) :

        error = "Config file is either corrupted/absent"
        # if we have to load 
        if mode == 'load' : 
            raise RuntimeError(error)
        # if mode = update
        else : 
            print(error + "creating it")
            with open('app_config.json','w') as f:
                parent_dict = {config_name:config_dict} # creating a json file 
                json.dump(parent_dict,f)
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

        error = "Pwd file is either corrupted/absent"
        # if we have to load 
        if mode == 'load' : 
            raise RuntimeError(error)
        # if mode = update
        else : 
            print(error + "creating it")
            with open('pwd.dat','wb') as f:
                pwd_dict = {user:pwd} # creating a json file 
                pickle.dump(pwd_dict,f)
            return pwd

    except KeyError as e :
        raise RuntimeError("invalid Configrations requested make sure pwd is correctly given") 

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

        error = "Session file is either corrupted/absent"
        # if we have to load 
        if mode == 'load' : 
            raise RuntimeError(error)
        # if mode = update
        else : 
            print(error + "creating it")
            with open('session.dat','wb') as f:
                pickle.dump(session_dict,f)
            return session_dict

    except KeyError as e :
        raise RuntimeError("invalid Configrations requested make sure session_dict is correctly given") 


def conn_handdler(host:str,user:str,pwd:str,db:str = ''):
    '''
        returns a mysql connection if sucess otherwise raise runtime error 
    '''
    try : 
         con = connect(host = host , user = user , password = pwd , database=db)
         return con
    
    except ProgrammingError as e:
        # Wrong user/password (Error 1045: Access denied)
        raise RuntimeError(f"Authentication Failed {e}")
    except InterfaceError as e:
        # # Can't connect to server (wrong host, server down)
        raise RuntimeError(f"Cannot connect to server: {e} ..")
    except Error as e:
        # Other MySQL errors
        print(f"MySQL Error: {e}")
        raise RuntimeError("Configs cannot be saved try running app_setup.py ..")


def execution_handdler(query:str,**kwargs: str):
    '''
        Executes a query and returns the all rows fetched or emptly list or error 

        Args:
            Query : query to be executed 
            Kwargs : **{'host'='','user'='','pwd'='','db'=""}** dictionary containing parameters for con_handler(**kwargs)
        Returns:
            list[Tupple]: Result of the query executed if any else empty list '[]'
        Exceptions:
            RuntimeError : If any problem if any error occured
    '''
    try :   
        conn = conn_handdler(**kwargs) # trying to connect
        cursor = conn.cursor()
        cursor.execute(query) # executing query
        output = cursor.fetchall() # fetching results 
        conn.commit() # commiting changes 
        conn.close() # closing connection
        return output
    # errors comming from conn_handdler
    except RuntimeError as e : 
        raise RuntimeError(f"Sorry Could Not Connect :{e}")
    # errors comming from cursor side while execution and fetching
    except Error as e :
        raise RuntimeError(f"Sorry Could Not Execute : {e}")  



def configure_app():
    '''
        Creates Necessory Files and Services Requierd To Run Our App

        :Args:
          None


    '''
    print("Proceed With Caution ! You Are About To Change App Configrations ")
    if is_continue():
    
        # getting config 
        for attempt in range(MAX_ATTEMPTS):

            print(f"Attempt Left: {MAX_ATTEMPTS-attempt}")
            
            host = input("Enter Host Name : ")
         
            # testing above credentials before proceeding
            try: 

                # user setup 
                print("Creating User For App \n[Select 'No' If You Alredy Have User 'medilink_admin' Created]\n[OR Select Yes If you have to change the default database user or do not have any existing user]")
                if is_continue():

                    # trying for root access to create user 
                    root_pwd = gtpass('root','mysql')

                    # root access granted 
                    conn = connect(host=host, user='root', password=root_pwd)
                    cursor = conn.cursor()

                    # creating user 
                    query = "CREATE USER %s@%s IDENTIFIED BY %s;"
                    user  = input("Enter Username For Mysql User : ")
                    pwd = gtpass(user,"mysql",3) # getting password 
                    cursor.execute(query, (user, host, pwd)) # user created successfully

                    # storing password for future use 
                    print("Root Password Is Being Saved For Future Use If Required")
                    if is_continue():
                        # if file already exists 
                        try : 
                            with open('app/pwd.dat','rb+') as file : 
                                # updating passowrds in configration file
                                pwd_dict = pickle.load(file)
                                pwd_dict["root"] = root_pwd
                                pwd_dict[user] = pwd  

                                # reset positions of the curesor 
                                file.seek(0)
                                file.truncate()

                                # updating the new passwords 
                                pickle.dump(pwd_dict,file)

                        # if file is to be created 
                        except (FileNotFoundError , EOFError , KeyError):

                            with open('app/pwd.dat' , 'wb') as file :
                                pwd_dict = {"root":root_pwd , user : pwd}
                                pickle.dump(pwd_dict,file)
                    else : 
                        print("You Have Enter Password Manually Each Time When Prompted")
                    conn.commit()
                    conn.close()

                else:

                    # proceeding with alredy existing user 
                    user = input("Enter Username : ")
                    pwd = gtpass(user,'mysql')

                # checking for database
                print("Creating Database For App [Select 'No' If Want To Use Existing Database ]")
                # user want to crate db
                if is_continue() : 
                    
                    # creating db

                    conn = connect(host=host)
                    db = input("Enter Database Name : ")  
                    query = 'CREATE DATABASE %s ; '

                    # creating root connection 
                    root_conn = connect(host=host , user = 'root' , )
                                  
                    conn = connect(host=host,user=user,password=pwd ,database = db )
                    conn.close()

                     # updating the pwd 
                    try : 
                            with open('app/pwd.dat','rb+') as file : 
                                # updating passowrds in configration file
                                pwd_dict = pickle.load(file)
                                pwd_dict[user] = pwd  

                                # reset positions of the curesor 
                                file.seek(0)
                                file.truncate()

                                # updating the new passwords 
                                pickle.dump(pwd_dict,file)

                        # if file is to be created 
                    except (FileNotFoundError , EOFError , KeyError):

                            with open('app/pwd.dat' , 'wb') as file :
                                pwd_dict = {user : pwd}
                                pickle.dump(pwd_dict,file)
                                
            
                    # updating config.json file 
                    with open('app/app_config.json' , 'w') as file :

                        config_dict  = {"CONNECTION_CONFIG":{ "host": host , "user" : user , "database" : db}}
                        json.dump(config_dict,file)
                        
                    print("configrations updated")
                    return config_dict
                
                # user want to configuere with existing  database 
                else :   

                    # connecting to database  
                    db = input("Enter Database Name : ")                        
                    conn = connect(host=host,user=user,password=pwd ,database = db )
                    conn.close()

                    # updating the pwd 
                    try : 
                            with open('app/pwd.dat','rb+') as file : 
                                # updating passowrds in configration file
                                pwd_dict = pickle.load(file)
                                pwd_dict[user] = pwd  

                                # reset positions of the curesor 
                                file.seek(0)
                                file.truncate()

                                # updating the new passwords 
                                pickle.dump(pwd_dict,file)

                        # if file is to be created 
                    except (FileNotFoundError , EOFError , KeyError):

                            with open('app/pwd.dat' , 'wb') as file :
                                pwd_dict = {user : pwd}
                                pickle.dump(pwd_dict,file)

                    # updating config.json file 
                    with open('app/app_config.json' , 'w') as file :

                        config_dict  = {"CONNECTION_CONFIG":{ "host": host , "user" : user , "password" : pwd , "database" : db}}
                        json.dump(config_dict,file)

                    print("configrations updated")
                    return config_dict

            except ProgrammingError as e:
                # Wrong user/password (Error 1045: Access denied)
                print(f"Authentication failed: {e}")
                # print("Wrong username or password. Please try again.")
                # sent to retry
            except InterfaceError as e:
                # Can't connect to server (wrong host, server down)
                print(f"Cannot connect to server: {e}")
                # print("Check if MySQL server is running and host is correct.")
                raise RuntimeError("Configs cannot be saved try running app_setup.py ..")
            except Error as e:
                # Other MySQL errors
                print(f"MySQL Error: {e}")
                raise RuntimeError("Configs cannot be saved try running app_setup.py ..")
        
        raise RuntimeError("Sorry No Attempt Left ... ")
    else :
        raise RuntimeError("Configs cannot be saved :Permittion Denied By User ")

# def load_config():
    
# main line segment 
if __name__ == "__main__":
    print("Testing Begins")
    try: 
        print(configure_app())
    except Exception as e :
        print(e)

