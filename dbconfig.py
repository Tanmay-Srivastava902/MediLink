# importing required libraries 
import setup  # setup file 
import utils # utility file 
import subprocess 
import os
import time 
import constants as const 


# NOTE * auth_user is finalized  * set_mysql_root_pass is psudo finalized (only add  few ux changes) 
# TODO * find recursion approches 
#      * update ufnciton ot check for str "" in pwd not None 

def set_mysql_root_pass():

    '''
    Stores the mysql root user password for security of database 
      
    Args:

        None 

    Return:

       Success: if password is updated 
       Failed: if password is not updated 
    '''
    print('Password Set Initiated..')
    # Logging In To Mysql With Root Account 
    result = setup.run_as_sudo(['mysql' ,'-e' , 'SELECT 1 ;' ])
    if result == const.FAILED:
        print('Insufficient Permittion..')
        return const.FAILED

    # Cannot Login To Root Account 
    if result.returncode == 1 :
        print('Mysql root user is already using a password ')

        for attempt in range(const.MAX_ATTEMPTS):
            print(f'Attemt {attempt+1}/{const.MAX_ATTEMPTS}')
            pwd = utils.gtpass("root","Mysql") # getting pass
            is_auth =  auth_user("root",pwd)    # verifying 
            
            if is_auth == const.SUCCESS: 
                # update pwd 
                try:
                    utils.update_pwd('root',pwd)

                except Exception as e:
                    print(f"sorry could not set mysql root pass \n{e}")
            
                print('Password Is Saved For Future Mysql Root Operations ..')

                return  const.SUCCESS 
            else : 
                print('Retrying...')

        #no attemt left 
        print("No Attempt Left")
        return const.FAILED
        
    # Logged In To Root Account Directly 
    elif result.returncode == 0 :
            
            print(' Warning : password For Root User Is Not Set ...')
            print(' Important ! Changing Root Password..... \n Caution : if you forgot this password you will end up losing you mysql  ')
            # Getting password 
            rootpass = utils.gtpass("Root","Mysql",3)

            # Escape password for SQL to prevent injection
            escaped_pass = escape_mysql_injectables(rootpass)
            

            # adding root password 
            
            query = f"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{escaped_pass}'; "
            result =  setup.run_as_sudo(['mysql' ,'-e' , query])
            # ex - sudo mysql -e 'alter user .... ;'

            # if query is Successful
            if result == const.FAILED : 
                print('Sudo Permission Denied...')
                return const.FAILED 
            elif result.returncode == 0 :

                print('Root password is Changed Successfully')
                # updating the password to environment settings 
                const.MEDILINK_ENV['MYSQL_PWD'] = rootpass
                return const.SUCCESS

            # if query is failed  
            else : 
                
                print(f'password Set Failed..  \n {result.stderr}')
                return const.FAILED 
    # Unexpected Error Occured 
    else : 
        print(f'password Set Failed..  \n {result.stderr}')
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
    if const.MEDILINK_ENV['MYSQL_PWD'] == '':
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
                            env=const.MEDILINK_ENV) # getting password  form MEDILINK_ENV
    return result
    


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


    
def auth_user(user : str ,pwd : str) :

    '''
    Authenticates A Mysql User 

    Args:

        User : Takes Mysql Username 
        pwd : Password for the User

    Return:

        True : if auth Successful 
        False  : if auth denied
'''
    # creating a temporary environment for password testing 
    TEMP_ENV = os.environ.copy()
    TEMP_ENV['MYSQL_PWD'] = pwd

    # Logging in to authenticate 
    result  = subprocess.run(['mysql' , '-u' , user , '-e' , 'SELECT 1 ;'],
                                capture_output=True,
                                text=True,
                                env=TEMP_ENV) # sending password through temporary  environment 
    # login Success
    if result.returncode == 0 :
        print('Authentication Successful....')
        return const.SUCCESS  
    # login failed 
    else :
        error  = result.stderr 
        if "ERROR 2002" in error :
            print("Server Is Not Running.... ")
            if setup.mysql_config():
               # call the function itself (recursion) 
               # NOTE : all other ends of the functions should be blocked by return 
               return auth_user(user,pwd)
            else:
                print("Authentication Failed : Server Is Not Runnig")
                return const.FAILED
        else : 
            print("Authentication Failed : Invalid Credentials")
            return const.FAILED

def create_user() :
    '''
    Creates A MYSQL User 

    Args: 
        None 

    Return:

        None 
    
    '''
    print('Creating Mysql User ....')
    if not utils.is_continue(): 
        print("permittion Denied..")
        return const.FAILED
    
    user = input("Please Enter Username : ")
    escaped_user = escape_mysql_injectables(user)

    # getting secure password 
    password  = utils.gtpass(user,"Mysql",3)
    escaped_pass = escape_mysql_injectables(password)

    # creating the user 
    query  = f"CREATE USER IF NOT EXISTS '{escaped_user}'@'localhost' IDENTIFIED BY '{escaped_pass}' ; " 
    result = mysql_root_operation(query)

    if result == const.FAILED:
        print("Root Access Denied ")
        return const.FAILED
    elif result.returncode == 0 : 
        print('User Successfully created ')
        return const.SUCCESS
    
    else : 
        print(f'User Cannot Be Created  \n {result.stderr}....')
        return const.FAILED


def update_mysql_user_pass(user:str):
            '''
            Updates the user password in env

            Args:
                user : user to auth 

            
            Returns:
                True: if pass update sucessfull
                False: if pass update Failed  
            '''
            print(f'Updating Password.... ')
            for attempt in range(const.MAX_ATTEMPTS):
                print(f'Attempt {attempt+1}/{const.MAX_ATTEMPTS}')
                # Getting password 
                userpass = utils.gtpass(user,"Mysql")
                # verifying access
                is_auth = auth_user(user,userpass)

                if is_auth :
                    try :
                        utils.update_pwd(user,userpass)
                        print(f'Password Is Upadated Sucessfully...')
                        # # Creating A Password Veriable In environment[USERNAME_PWD] To store password of that user
                        # const.MEDILINK_ENV[user.upper()+"_PWD"] = userpass
                        return const.SUCCESS
                    except Exception as e :
                        print(f"password set failed \n{e}")
                        return const.FAILED
                
                else:
                     print("Retrying....  ")
                     continue

            # if auth is failed  
            else : 

                print(f'password Set Failed.. \n Exiting....')
                return const.FAILED 
if __name__ == "__main__":
    #  create_user()
    mysql_root_operation("select user from ")