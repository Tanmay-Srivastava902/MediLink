# importing modules 
import getpass
import os


# definfing consts 
MAX_ATTEMPTS = 3
NEEDS_INSTALL = -1
FAILED = 0
SUCCESS = 1
SERVICE_TO_PACKAGE = {'apaceh2' : 'apache2' ,'mysql' : 'mysql-server'}  # for installing package currosponding service 



def is_continue() -> bool:
    '''
    Asks User If To continue Operation or not 

    Args:
        :None 
    
    Returns:

        :True: if user wants to proceed 
        :False: if user denies to proceed
    '''
    for attempt in range(MAX_ATTEMPTS):
        if attempt > 0:
            print(f'Attempts Left : {MAX_ATTEMPTS-attempt}')
        response = input('Do you want to continue (y/n) : ').strip().lower()
        if response == 'y'   :
            # print('proceeding...')
            return True 
        elif response == 'n' : 
            # print('Permission Denied By User ...')
            return False
        else : 
            print(f'Invalid Response Please Retry....')
            continue 
    else : 
        print('No attempts Left....')
        return False



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

        for attempt in range(MAX_ATTEMPTS):
            if attempt > 0:
                print(f'Attempts Left {MAX_ATTEMPTS-attempt}')
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
            raise RuntimeError('Sorry No Attempts Left ')
        
    #Hard security
    if security_level == 3:

        print('Important ! Passowrd Should Contain atleast 8 chrs\nMust Include One Capital Letter\nMust Include One Small Letter\nMust Include One Special Symbol[@/$/#/%/&]\nMust Include A Digit ')
        for attempt in range(MAX_ATTEMPTS):
            if attempt > 0:
                print(f'Attempts Left {MAX_ATTEMPTS-attempt}')
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
                    print("Captured Password : Requirements Satisfied")
                    return password 
                else :
                    print(f'Password Requirments Not Satisfied Please Retry...')
                    continue

            else : 
                print(f'Sorry Password Not Matched : Please Retry....') # we have alredy used one attempt by default
                continue
        else : 
            raise RuntimeError('Could Not Get The Password : No Attempts Left ')
            
    else :
        raise RuntimeError('Unknown Error Occured  Please Check Parameters first')



def config_path(file_name:str):
    '''Takes The file name [**with extension**] and returns the path correct path of the file  '''       
        # Get the absolute path to the config directory inside app
    config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config'))
    # Build the full path to a config file
    file_path = os.path.join(config_dir, file_name)

    return file_path