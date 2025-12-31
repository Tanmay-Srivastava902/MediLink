'''This Module Contains Functions To Freshly Setup The Environment For Our App'''
# importing  our all modules to work with 
# own app modules 
from handdlers.utils_handdler import  config_path
from handdlers.file_handdler import pwd_handdler , json_handdler , session_handdler 
from  handdlers.system_handdler import execute_cmd as sys_executor ,package_installer ,save_sudo_pwd , configure_server
from handdlers.mysql_handdler import save_root_pwd
# external python modules 
from os.path import isfile
import sys 
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

def check_files() -> bool:
    '''Creates all files that are required during setup Return True if Created Otherwise Raises RuntimeError'''
    try : # creating pwd file 
        print('Checking Required Files!')
        pwd_path = config_path('pwd.dat')
        session_path = config_path('session.dat')
        json_path = config_path('app_config.json')
        # checking existence of files
        if isfile(pwd_path) and isfile(session_path) and isfile(json_path) : 
            # file exists alredy 
            print("File Requirements Alredy Satisified !")
            return True # alredy stisfied
        else :
            print("Creating Required Files")
            while True : 
                if not isfile(pwd_path):
                    pwd_handdler('create') # creating pwd file 
                    # saving passwords after creation of file 
                    try:
                        print("Saving System Sudo Password")
                        save_sudo_pwd() # saving system root pwd
                        print("Saving Mysql Root Password")
                        save_root_pwd() #saving mysql root pwd
                    except RuntimeError as e : 
                        raise RuntimeError(f'Save Error:{e}')
                elif not isfile(session_path):
                    session_handdler('create') # creating session
                elif not isfile(json_path):
                    json_handdler('create')
                else: 
                    break  # all files are created

            print("Required Files Created Successfully")
            return True
    except RuntimeError as e : # stop execution 
        if 'Save Error' in str(e):
            raise RuntimeError(f'Error Occured :{e}')
        else:
            raise RuntimeError(f'Could Not Create Files : {e}')


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
# #         print(check_system())
#         # print(check_files())
#         print(session_handdler('update',{'host': 'localhost', 'user': 'tanmay', 'pwd': 'SecurePass@1201','db':'medilink'}))
#         print(session_handdler('load'))
        
# #         print(check_venv())
# #         print(check_server())  

#     except RuntimeError as e:
#         print(e)