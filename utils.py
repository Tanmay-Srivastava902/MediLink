# imports 
import getpass 
import constants as const 
import json
import pickle
import dbconfig
# from typing import Union
# NOTE * all functions are final is continue , gtpass, 
# checking if to continue or not 
def is_continue() -> bool:
    '''
    Asks User If To continue Operation or not 

    Args:
        :None 
    
    Returns:

        :True: if user wants to proceed 
        :False: if user denies to proceed
    '''
    for attempt in range(const.MAX_ATTEMPTS):
        print(f'Attempt {attempt+1}/{const.MAX_ATTEMPTS} ')
        response = input('Do you want to continue (y/n) : ').strip().lower()
        if response == 'y'   :
            print('proceeding...')
            return const.SUCCESS  
        elif response == 'n' : 
            print('Permission Denied By User ...')
            return const.FAILED 
        else : 
            print(f'Invalid Response Please Retry....')
            continue 
    else : 
        print('No attempts Left....')
        return const.FAILED 



def gtpass(user:str ,app:str, security_level:int = 1) -> str:
    '''
    Gets A  Password From The User Input Securely 

    Args:

        User: str Username 
        App: str  [mysql/system] name of service whom user belongs to 
        Security_level: integer[1,2,3] how much secure the password to take \n
            :1: Easy (No Confirm Password Prompt Appears)
            :2: Medium (Confirm Password Appears To Avoid Accidental Input...)
            :3: Hard (Confirm Password Prompt With Extra Validation If Required...)
            :Dafault: 1


    Return:
        str: password string 
        Empty str ('') when any error occured 
    '''
    # NOTE Password should not be taken directly in terminal (passwords are visible in process list)
            
    #Easy Security
    if security_level == 1:

        password  = getpass.getpass(f'Please Enter Password For {app} User "{user}" : ').strip()
        print('Password Captured..')
        return password
    #Medium Security
    if security_level == 2:

        for attempt in range(const.MAX_ATTEMPTS):

            print(f'Attempt {attempt+1}/{const.MAX_ATTEMPTS}')
            password  = getpass.getpass(f'Please Enter Password For {app} User "{user}" : ').strip()
            confirm_password  = getpass.getpass('Please Re-Enter Your Password : ')
            
            # Matching Passowrds
            if password == confirm_password :
                print('Password Captured')
                return password
            else : 
                print(f'Sorry Password Not Matched : Please Retry..')
                continue 
        else : 
            print('Sorry No Attempts Left ')
            return ''
        
    #Hard security
    if security_level == 3:

        print('Important ! Passowrd Should Contain atleast 8 chrs\nMust Include One Capital Letter\nMust Include One Small Letter\nMust Include One Special Symbol[@/$/#/%/&]\nMust Include A Digit ')
        for attempt in range(const.MAX_ATTEMPTS):
            
            print(f'Attempt {attempt+1}/{const.MAX_ATTEMPTS}')
            password  = getpass.getpass(f'Please Enter Password For {app} User "{user}" : ').strip()
            confirm_password  = getpass.getpass('Please Re-Enter Your Password : ')
            
            # Matching Passowrds
            if password == confirm_password :


                # Initialize Check Vars 
                have_capital=False
                have_small=False
                have_special_chr=False
                have_digit=False
                have_8chr =False
                
                # performing checks
                if len(password) >= 8:
                        have_8chr = True

                for chr in password:
                    if chr.islower():
                        have_small = True
                    elif chr.isupper():
                        have_capital = True
                    elif chr.isdigit():
                        have_digit = True
                    elif chr in ["@","$","%","&","#"]:
                        have_special_chr = True
                
                # if all checks cleared
                if have_8chr and have_capital and have_digit and have_small and have_special_chr  :
                    print("Captured Password : Rquirments Satisfied")
                    return password 
                else :
                    print(f'Password Requirments Not Satisfied Please Retry...')
                    continue

            else : 
                print(f'Sorry Password Not Matched : Please Retry....') # we have alredy used one attempt by default
                continue
        else : 
            print('Sorry No Attempts Left ')
            return ''
    else :
        print('Unknown Error Occured  Please Check Parameters first')
        return ''

# binary handling 
def create_pwd_file() -> None:
    '''
    Creates a pwd dictionary empty with root = 'blank_pass' and mdeilink_admin = 'blank_pass'
    Args:
        None 
    Returns:
        None

    '''
    pwd_dict = { "root":"","medilink_admin":""}
    with open('pwd.dat','wb') as f :
        pickle.dump(pwd_dict,f)

    



def update_pwd(user:str,new_pwd:str) -> None :
    '''
    Update the passowrd to given pwd for the given user 
    Args:
        user: name of user
        pwd : new
    Retuns:
        None 
    Raise:
        RuntimeError: if cannot update 
    '''
    # opening json  file to get path of pwd file 
    with open('config.json','r') as f :
        content = json.load(f)
        pwd_path = content['DEFAULT_CONFIG']['pwd_file_path']

    # gtting password from file 
    try : 
        with open(pwd_path,'rb+') as pwd_file :
            pwd_dict  = pickle.load(pwd_file) 

            # updating pwd in dict where 'user1':'pwd_for_user1'
            pwd_dict[user] = new_pwd

            # Go back to beginning and clear file
            pwd_file.seek(0) 
            pwd_file.truncate()
            
            # dumping back 
            pickle.dump(pwd_dict,pwd_file)
    except (FileNotFoundError, EOFError) as e :
        # creating paswd file if not found or empty/corrupted
        create_pwd_file()
        # then updating the passwrd 
        with open(pwd_path,'rb+') as pwd_file :
            pwd_dict  = pickle.load(pwd_file) 

            # updating pwd in dict where 'user1':'pwd_for_user1'
            pwd_dict[user] = new_pwd

            # Go back to beginning and clear file
            pwd_file.seek(0) 
            pwd_file.truncate()
            
            # dumping back 
            pickle.dump(pwd_dict,pwd_file)
    except Exception as e :
        raise RuntimeError(f"cannot update password \n{e}")

def load_pwd(user:str):
    '''
    Gives the password for the user asked 
    Args:
        user:usrename to get pwd for
    '''
    try:
        with open('pwd.dat' ,'rb') as f :
            pwd_dict = pickle.load(f)
            return pwd_dict[user] 

    except (KeyError, FileNotFoundError, EOFError) as e : 

         print(f'Passowrd not found for user "{user}" ')
         is_set = dbconfig.update_mysql_user_pass(user)
         if not is_set : 
              print(f' Error ! Password For {user} Cannot Be Saved ')
              return None
         
         # After updating, reload password
         with open('pwd.dat', 'rb') as f:
             pwd_dict = pickle.load(f)
             return pwd_dict[user] 
             


# json handling 

## Recovery Commands

# If you accidentally delete or corrupt config.json:
# ```python
# python -c "from utils import create_config; create_config()"

def create_config():
    '''
    Creates json file if not created
    Returns:
        bool : True If created False if cannot create


    '''
    # creating default content
    json_default_content = {
                    "DEFAULT_CONFIG":{

                        "pwd_file_path":"pwd.dat",
                        "session_file_path":"session.dat"
                                     },
                    "ROOT_CONFIG":{
                        "host":"localhost",
                        "user":"root",
                        "password":""

                    }
                            }
    try : 
        with open('config.json') as file : 
            json.dump(json_default_content,file)
        return True
    except Exception as e :
        print(f"could not create configration file\n{e} ")
        return False

def fetch_config(config_key:str) -> dict[str,str]:
    '''
    Returns the dict of the desired configration 
    
    Args:
        conifg_key: key of the dictionary which to load 
        eg - "DB_CONFIG" , "DEFAULT_CONFIG" etc
    Returns:
        config_dict: if key found 
    Raise:
        RuntimeError: if no key found 
    '''
    try : 

        with open('config.json' , 'r') as f :

            content = json.load(f)

            # getting the desired key 
            config_dict  = content[config_key]
            return config_dict  # sending the dict requested 

    except (FileNotFoundError, EOFError) as e :
        raise RuntimeError(f"'config.json' file  Doesnt Exists : \n{e} ")
    except KeyError as e :
        raise RuntimeError(f"Configration Doesnt Exists : \n{e} ")     
    except Exception as e :
        raise RuntimeError(f"cannot fetch configrations \n{e}") 


# session handling  
def update_session(user:str):

   
    try:
      
        with open('session.dat' , 'rb+') as f :
            # getting current session
            current_session = pickle.load(f)
            # getting confirmation
            print(f"current session is alredy set to '{current_session}' Changing it to '{user}' ")
            if is_continue(): 
                # reseting the cursor position 
                f.seek(0)
                f.truncate()
                # updating the session
                pickle.dump(user,f)
            else:
                raise RuntimeError('Permittion Denied By user')
            
    except FileNotFoundError as e:

        print("session not found creating..")
        # creating session
        with open('session.dat','wb') as f :
            pickle.dump(user,f) 
        return None

    except Exception as e:
        raise RuntimeError(f"Could Not Update Session\n{e} ")
        
        # updating session 
        

    

    

if __name__ == "__main__":

    print("Testing Begins..")

    # print(f"The Password Is : {gtpass("tanmay","mysql",3)}")
    
    # # testing functions;
    # with open('pwd.dat','rb') as pwd_file :
    #     pwd_dict  = pickle.load(pwd_file) 
    #     print("output before execution :" , pwd_dict)

        
    # update_pwd('root','SecurePass@1201')
    # # update_pwd('xyz','xyz@2222')

    # with open('pwd.dat','rb') as pwd_file :
    #     pwd_dict  = pickle.load(pwd_file) 
    #     print("output after executin" , pwd_dict)



    # testing fetch_config

    # Test error handling
    # try:
    #     print("CONFIG = " , fetch_config("Unknown"))
    # except RuntimeError as e:
    #     print("Expected error:", e)


    # # Test valid configs
    # print("CONFIG = " , fetch_config("DEFAULT_CONFIG"))
    # print("CONFIG = " , fetch_config("ROOT_CONFIG"))



    # testing update session

    # Test error handlinga
    # try:
    #     # with open('session.dat','rb') as f :
    #     #     session  = pickle.load(f) 
    #     #     print("output before execution :" , session)

    #     update_session('root')

    #     with open('session.dat','rb') as f :
    #         session  = pickle.load(f) 
    #         print("output after execution :" , session)


    # except RuntimeError as e:
    #     print("Expected error:", e)

    # # testing load pwd
    try:
        print("the passowrd is " , load_pwd('root'))
    except Exception as e :
        print(e)
            
    # update_pwd('tanmay', 'SecurePass@1201')
    # # Then check what was saved:
    # with open('pwd.dat', 'rb') as f:
    #     pwd_dict = pickle.load(f)
    #     print("Saved password for tanmay:", pwd_dict['tanmay'])