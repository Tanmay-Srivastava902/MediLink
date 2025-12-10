# importing required libraries 
import setup  # setup file 
import utils # utility file 
import subprocess 
import os
import time 
import constants




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
        if is_auth == constants.SUCCESS: 
            print('Password Is Saved For Future Mysql Root Operations ..')
            return  constants.SUCCESS
        # Failed msg is returned 
        else : 
            print('Password Set Failed ......  ')
            return constants.FAILED
        
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
                constants.MYSQL_ROOT_ENV['MYSQL_PWD'] = rootpass
                return constants.SUCCESS

            # if query is failed  
            else : 
                
                print(f'password Set Failed..  \n {result.stderr} \n Exiting....')
                return constants.FAILED 
    # Unexpected Error Occured 
    else : 
        print(f'password Set Failed..  \n {result.stderr} \n Exiting....')
        return constants.FAILED 


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
    if constants.MYSQL_ROOT_ENV['MYSQL_PWD'] == '':
        print("password Is Not set... ") 

        is_set = set_mysql_root_pass()
        # password set failed 
        if is_set == constants.FAILED :  
            print("continuation may lead to crashes during root operation")
            if utils.is_continue() :
                return constants.FAILED # user still want to contiue
            else : 
                print('Exitting the program : User Choice ....')
                time.sleep(1)
                exit()

    result = subprocess.run(['mysql' , '-u' , 'root' , '-e' , query ] ,
                            capture_output=True,
                            text=True,
                            env=constants.MYSQL_ROOT_ENV) # getting password  form MYSQL_ROOT_ENV
    return result
    
    
def auth_user(user : str ) :

    '''
    Authenticates A Mysql User 

    Args:

        User : Takes Mysql Username 

    Return:

        Success : if auth Successful 
        Failed  : if auth denied
    '''

    attempt = 0 
    while attempt < constants.MAX_ATTEMPTS: 


        # Getting password 
        print(f"Getting password  for mysql user  {user}  ....")
        secure_pass = utils.gtpass()
        
        # failed to get password 
        if secure_pass == 0 : 
             print("Authentication Failed : Failed to get password ")
             return constants.FAILED 
 
       # creating a temporary environment ( book ) having different page for password we are using a secret book for exchage of passwords between python code and mysql server skipping the terminal 
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
            # Store verified password in global environment
            constants.MYSQL_ROOT_ENV['MYSQL_PWD'] = secure_pass
            return constants.SUCCESS  
        
        else :
            print(f'Authentication Failed : Invalid Credentials \n Retrying......  | Attempt {attempt+1}/3')
            attempt += 1

    # max attempt exceeded 
    else : 
        print(' Authentication Failed : No attempts Left ')
        return constants.FAILED 
    

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
        return constants.SUCCESS
    
    else : 
        print(f'User Cannot Be Created  \n {result.stderr}....')
        return constants.FAILED
    


if __name__ == "__main__" : 
    pass


