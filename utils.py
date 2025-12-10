# imports 
import getpass 
import constants 

# checking if to continue or not 
def is_continue():
    attempt = 0
    while attempt < constants.MAX_ATTEMPTS  : 
        response = input('Do you want to continue (y/n) : ').strip().lower()
        if response == 'y'   :
            print('proceeding...')
            return constants.SUCCESS # true 
        elif response == 'n' : 
            print('Permission Denied By User ...')
            return constants.FAILED # false
        else : 
            print(f'Invalid Response Please Retry \n attempt : {attempt+1} / 3')
            attempt += 1 
    else : 
        print('No attempts Left....')
        return constants.FAILED # false


def escape_mysql_injectables(ipt : str) :
    '''
    Escapes injectable sequences to prevent SQL injection
    
    Args:
        ipt: String to be escaped (raw input)
        
    Returns:
        Escaped string safe for MySQL queries
    
    Note: Double quotes don't need escaping in MySQL single-quoted strings
    '''
    # Escape backslashes FIRST, then single quotes
    escaped_string = ipt.replace('\\', '\\\\').replace("'", "\\'")
    return escaped_string




def gtpass():
    '''
    Gets A  Password From The User Input Securely 

    Args:

        None 

    Return:

        Password : if password and confirm password match 
        0 : if Failed to match 
    '''
    attempt = 0 
    while attempt < constants.MAX_ATTEMPTS : 

        # NOTE Passowrd should not be taken directly in terminal (passowrd are visble in process list )
        # getting password
        password  = getpass.getpass('Please Enter Password : ')
        confirm_password  = getpass.getpass('Please Confirm Your Password : ')
        print('Passowrd Captured ')
        
        # password confirmed 
        if password == confirm_password :

            return password
        # password is not matched with confirm password 
        else : 
            print(f'Sorry Password Not Matched : Please Retry | Attempt {attempt +1 } / 3')
            attempt += 1 # updating attempts
    else : 
        print('Sorry No Attempts Left ')
        return 0 # failed 

