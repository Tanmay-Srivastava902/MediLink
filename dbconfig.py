# importing required libraries 
import setup  # setup file 
import utils # utility file 
import subprocess 
import os
import time 
import constants as const 




def set_mysql_root_pass():

    '''
    Sets the mysql root user password for security of database 
      
    Args:

        None 

    Return:

       Success: if password is updated 
       Failed: if password is not updated 
    '''
    print('Password Set Initiated..')
    # Logging In To Mysql With Root Account 
    result = setup.run_as_sudo(['mysql' ,'-e' , 'SELECT 1 ;' ])

    # Cannot Login To Root Account 
    if result.returncode == 1 :

        print('Mysql root user is already using a password ')

        # authenticating root user 
        is_auth =  auth_user('root') 
        # password is returned :  auth Successful 
        if is_auth == const.SUCCESS: 
            print('Password Is Saved For Future Mysql Root Operations ..')
            return  const.SUCCESS
        # Failed msg is returned 
        else : 
            print('Password Set Failed ......  ')
            return const.FAILED
        
    # Logged In To Root Account Directly 
    elif result.returncode == 0 :
            
            print(' Warning : password For Root User Is Not Set ...')
            print(' Important ! Changing Root Password..... \n Caution : if you forgot this password you will end up losing you mysql  ')
            # Getting password 
            rootpass = utils.gtpass()

            # Escape password for SQL to prevent injection
            escaped_pass = utils.escape_mysql_injectables(rootpass)
            
            # adding root password 
            query = f"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{escaped_pass}'; "
            result =  setup.run_as_sudo(['mysql' ,'-e' , query])
            # ex - sudo mysql -e 'alter user .... ;'

            # if query is Successful 
            if result.returncode == 0 :

                print('Root password is Changed Successfully')
                # updating the password to environment settings 
                const.MYSQL_ENV['MYSQL_PWD'] = rootpass
                return const.SUCCESS

            # if query is failed  
            else : 
                
                print(f'password Set Failed..  \n {result.stderr} \n Exiting....')
                return const.FAILED 
    # Unexpected Error Occured 
    else : 
        print(f'password Set Failed..  \n {result.stderr} \n Exiting....')
        return const.FAILED 


def mysql_root_operation(query : str):
    '''

    Executes the query as root user and return the result  

    set the password if not already then executes the query 

    Args:

        Query: mysql query to be executed as root 

    Return: 

        0: if forcefully continued 
        CompletedProcess[str]: subprocess.run() output 
    
    '''
    # password set required 
    if const.MYSQL_ENV['MYSQL_PWD'] == '':
        print("password Is Not set... ") 

        is_set = set_mysql_root_pass()
        # password set failed 
        if is_set == const.FAILED :  
            print("continuation may lead to crashes during root operation")
            if utils.is_continue() :
                return const.FAILED # user still want to contiue
            else : 
                print('Exitting the program : User Choice ....')
                time.sleep(1)
                exit()

    result = subprocess.run(['mysql' , '-u' , 'root' , '-e' , query ] ,
                            capture_output=True,
                            text=True,
                            env=const.MYSQL_ENV) # getting password  form MYSQL_ENV
    return result
    
    
def auth_user(user : str , Env_var: str = 'MYSQL_PWD'  ) :

    '''
    Authenticates A Mysql User 

    Args:

        User : Takes Mysql Username 
        Env_var : Takes Name Of Environment Variable Where To Save Verified Password  
            DEFAULT- MYSQL_PWD  (always update mysql root passowrd )

    Return:

        True : if auth Successful 
        False  : if auth denied
    '''

    attempt = 0 
    while attempt < const.MAX_ATTEMPTS: 


        # Getting password 
        print(f"Getting password  for mysql user  {user}  ....")
        secure_pass = utils.gtpass()
        
        # failed to get password 
        if secure_pass == 0 : 
             print("Authentication Failed : Failed to get password ")
             return const.FAILED 
 
       # creating a temporary environment for password testing 
        TEMP_ENV = os.environ.copy()
        TEMP_ENV['MYSQL_PWD'] = secure_pass

        # Logging in to authenticate 
        result  = subprocess.run(['mysql' , '-u' , user , '-e' , 'SELECT 1 ;'],
                                 capture_output=True,
                                 text=True,
                                 env=TEMP_ENV) # sending password through temporary  environment 
        # login Success
        if result.returncode == 0 :
            print('Authentication Successful....')
            # Store verified password in global environment as varibale Env_var 
            
            const.MYSQL_ENV[Env_var] = secure_pass
            return const.SUCCESS  
        
        else :
            print(f'Authentication Failed : Invalid Credentials \n Retrying......  | Attempt {attempt+1}/3')
            attempt += 1

    # max attempt exceeded 
    else : 
        print(' Authentication Failed : No attempts Left ')
        return const.FAILED 
    

def create_user() :
    '''
    Creates A MYSQL User 

    Args: 
        None 

    Return:

        None 
    
    '''
    print('Creating User ....')
    
    
    user = input("Please Enter Your Username : ")
    escaped_user = utils.escape_mysql_injectables(user)

    # getting secure password 
    password  = utils.gtpass()
    escaped_pass = utils.escape_mysql_injectables(password)

    # creating the user 
    query  = f"CREATE USER IF NOT EXISTS '{escaped_user}'@'localhost' IDENTIFIED BY '{escaped_pass}' ; " 
    result = mysql_root_operation(query)


    if result.returncode == 0 : 
        print('User Successfully created ')
        return const.SUCCESS
    
    else : 
        print(f'User Cannot Be Created  \n {result.stderr}....')
        return const.FAILED

