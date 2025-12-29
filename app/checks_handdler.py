'''This Module Contains Functions To Freshly Setup The Environment For Our App'''
# importing  our all modules to work with 

# own app modules 
from utils_handdler import gtpass , MAX_ATTEMPTS
from file_handdler import pwd_handdler
from  system_handdler import execute_cmd as sys_executor ,package_installer ,service_manager , configure_server

# external python modules 
from mysql.connector import connect 
import pickle
import json
from os.path import isfile
from subprocess import run
import sys 
from mysql.connector import connect , Error 
from mysql.connector.errors import InterfaceError , ProgrammingError 

def check_system()-> bool:
    '''Checks System And Compatibility For Our App Rturns True If Conpatible else Raise RuntimeError'''
    print('Checking Your System !')
    # getting platform 
    from platform import system as get_current_os
    # windows found 
    if get_current_os().lower() == 'windows' :
        raise RuntimeError('Inappropriate System  Detected \'Windows OS\': This App Is Ment Only For Linux Operating System \'Ubuntu\'')
    else: 
        # linux system found 
        with open('/etc/os-release') as f :
            current_os_details = f.read().lower()
            # found ubunutu
            if 'ubuntu' in current_os_details : 
                print('Ubuntu System Detected')
                return True 
            # other linux systems or Mac os 
            else: 
                raise RuntimeError('Inappropriate Linux Disto Detected :This App Is Ment Only For \'Ubuntu\' Distro')

def check_files()-> bool:
    '''Creates all files that are required during setup Return True if Created Otherwise Raises RuntimeError'''
    try : # creating pwd file 
        print('Checking Required Files!')

        # checking existence of files
        if isfile('pwd.dat') and isfile('session.dat') and isfile('app_config.json') : 
            # file exists alredy 
            print("File Requirements Alredy Satisified")
            return True # alredy stisfied
            

        # creating empty file for pwd 
        with open('pwd.dat','wb') as f :
            empty_pwd_data = {'sudo':'','root':'','admin':''} # username:pwd
            pickle.dump(empty_pwd_data,f)

        # creating empty session file 
        with open('session.dat','wb') as f :
            empty_session_data = {'host':'','user':'','pwd':'','db':''} # configname:value
            pickle.dump(empty_session_data,f)

        # creating empty config file 
        with open('app_config.json','w') as f:
            # default json data
            json_data = {
                            'APP_CONFIG':{
                                'app_name':'MediLink',
                                'app_admin':'medilink_admin',
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
            json.dump(json_data,f)
    except Exception as e : # stop execution 
        raise RuntimeError(f'Could Not Create Files : {e}')

    # filling empty files with genral configrations
    try : 
        print('Adding Genral Configurations To Files ')
        print('Don\'t Worry ! If Failed You Will Be Asked For Them Whenever needed In Future')
        # trying to save mysql root pwd
        try : 
            # system root pwd
            for attempt in range(MAX_ATTEMPTS):
                print(f'Attempt Left {MAX_ATTEMPTS-attempt}')

                sudo_pwd = gtpass('sudo','system')
                # verifying pwd
                res  = run(
                                    ['sudo' ,'-S','su'],  # adding sudo to the command 
                                    input=sudo_pwd + '\n', # sending password 
                                    capture_output=True,
                                    text=True
                            )
                # verified
                if res.returncode == 0: 
                    # saving sudo password 
                    pwd_handdler('update','sudo',sudo_pwd) 
                    print('Saved Sudo Passowrd')
                    break

                elif res.returncode == 1: # command failed to execute
                    print(f'Sorry, wrong password. Please try again.')
                    continue
                    # sent to retry
                else : 
                    raise RuntimeError('Unknown Error') # getting out 
                
            # end of attempts
            print('Sorry Max Attempt Reached')
            raise RuntimeError('Max Attempt Reached')
        
        except RuntimeError :
            print('Cannot Save Password For System \'Sudo\' User !')
        
        # trying to save  mysql sudo pwd 
        try : 
            # mysql root pwd
            for attempt in range(MAX_ATTEMPTS):
                print(f'Attempt Left {MAX_ATTEMPTS-attempt}')
                host = input('Enter hostname genrally use \'localhost\' : ').lower()
                root_pwd = gtpass('root','mysql')
                # verifying pwd
                try : 
                    conn = connect(host = host , user = 'root' , password = root_pwd)
                    print('Saved Mysql Root Passowrd')
                    break 
                except ProgrammingError as e:
                    # Wrong user/password (Error 1045: Access denied)
                    print(f'Authentication Failed : Wrong password Please Try Again..')
                    continue # sending to retry 

                except InterfaceError as e:
                    # # Can't connect to server (wrong host, server down)
                    print(f'Cannot connect to server: {e} ..')
                    # starting server properly 
                    service_manager('mysql','restart') 
                    continue # trying again if server started 
                                    
                except Error as e:
                    # Other MySQL errors
                    print(f'MySQL Error: {e}')
                    raise RuntimeError('Unexpected Error')
            # end of attempts
            print('Sorry Max Attempt Reached')
            raise RuntimeError('Max Attempt Reached')
        
        except RuntimeError :
            print('Cannot Save Password For Mysql \'Root\' User ! ')
        
        return True 
    except RuntimeError as e :
        raise RuntimeError(e)

def check_venv() -> bool: 
    '''Checks The Status Of  Venve Activate/Create if not activated/exists  Returns True If Suceed Otherwise Raises RuntimeError'''
    print("Checking Virtual Environment")
    cur_py_path  = sys.executable
    # checking for venv existence 
    if 'MediLink/bin'  in cur_py_path :
        # venv is alredy active 
        print("Alredy Using MediLink Virtual Environment")
        return True 
    else:
        # if venv exists
        if isfile('MediLink/bin/activate') :
            # activating wihout any error  as if it exists it must get activated 
            sys_executor(['source','Medilink/bin/activate'])
            print("Virtual Environment Activated Successfully")
            return True
        # if venv does not exists 
        else : 
            # creating venv 
            res = sys_executor(['python3','-m','venv','MediLink'])
            # venv created 
            if res.returncode == 0 :
                return check_venv() # calling again to reactivate it 
            # venv package does not exists 
            elif res.returncode == 1 : 
                # installing venv package
                package_installer('system','python3-venv')
                # if installed 
                return  check_venv() # calling again to reactivate it 
                # here if not installed then we got an error and execution stops we do not have to do anything 

            else : 
                raise RuntimeError(f"Unknown Error Could Not Create Venv : {res.stderr}")
            
def check_server() -> bool:
    '''Checks The Mysql Server Returns True If Setup Success Else Raises RuntimeError '''
    #NOTE Apache Can Be Mannaged Later If Required
    print("Checking Servers")
    # mysql server 
    try: 
        configure_server('mysql')
        print("Server Configured Properly")
        return True 
    except RuntimeError as e :
        raise RuntimeError(f"Could Not Configure Mysql server : {e}")
    
        


# if __name__ == "__main__":
#     try :
#         print(check_system())
#         print(check_files())
#         print(check_venv())
#         print(check_server())  

#     except RuntimeError as e:
#         print(e)