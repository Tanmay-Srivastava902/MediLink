# imports 
from mysql import connector  
from mysql.connector import Error # to use  Exception.errno --> "erro code"
import setup 
import utils 
import pickle
import dbconfig         
import constants as const 
from time import sleep as wait


# assigning values of contents form josn


#NOTE * connect_db is done for now there is no need to go beyond this 
def reconnect(user:str = ''):
    '''
    Opens A Connection To The Mysql Server To Access Mysql Shell Securely 

    Args:
        User: username whose account is to be used to access the mysql shell
        Default: current user will be used 

    Returns:
        PooledMysqlConnection: connection handle for the pooled connection\n
        Failed: connection Failed due to unexpected error
    
    Exit:
        If User Choose To quit After Encountering An Error

    '''

    # cheking the default parameter user 
    if user  == '':
        user = const.CURRENT_USER
        # no user is in session curently 
        if user  == '':
            print("Sorry Current User Is Not Set ..")
            if set_current_user() : 
                print("Current User Set Successfull")
                user = const.CURRENT_USER
            else:
                print("Could Not Connect | User Is Not Specified")
                return const.FAILED
        

    # # name of the key in the env in which the passowrd is going to store
    # pwd_var  = user.upper() + "_PWD" 
    # #eg- USERNAME_PWD



    # Checking for pwd existance of the user provided 
    try : 
        # const.MEDILINK_ENV[pwd_var]  # foud password 
        with open('pwd.dat' ,'rb') as f :
            pwd_dict = pickle.load(f)
            pwd = pwd_dict[user] # getting password for user to connect

    # password for this user doesnot exists in var 
    except (KeyError, FileNotFoundError, EOFError) as e : 

         print(f'Passowrd not found for user "{user}" ')
         is_set = dbconfig.update_mysql_user_pass(user)
         if not is_set : 
              print(f' Error ! Password For {user} Cannot Be Saved ')
              return const.FAILED
         
         # After updating, reload password
         with open('pwd.dat', 'rb') as f:
             pwd_dict = pickle.load(f)
             pwd = pwd_dict[user] 

    # tryng to connect          
    try : 
        connection = connector.connect(
                                    host=const.MYSQL_HOST,
                                    user=user,
                                    password=pwd,   
                                    # EX - password = const.MEDILINK['MYSQL_PWD'] if pwd_var  = 'MYSQL_PWD' 
                                    )
        return connection #  returning the connection obj
        
    except connector.Error as e :
        print(f"Connection Failed :\n {e}")
        return const.FAILED 
    except Exception as e : 
         print(f"Connection Failed due to genral error :\n {e}")
         return const.FAILED 
    
#TODO * create this funciton 
# def set_current_db() -> bool:
#     '''
#     Updates the current database variable globally

#     Args:
#         None
#     Returns:
#         Success: if set
#         Failed: cannot set 
#     '''
#     # getting databses that exists 
#     print(f'Warning ! if  skipped  default database {const.DEFAULT_DB} will be used..')
#     print("do you want to change databse...")

    

#     db = input('Please Enter the name of mysql database to begin with : ')
#     pass

def set_current_user() -> bool : 
    '''
    Updates the current Mysql user variable globally

    Args:
        None
    Returns:
        Success: if set
        Failed: cannot set 
    '''
    # alredy a current user is existing 
    if const.CURRENT_USER != '' :
        print(f"Current User is alredy set to {const.CURRENT_USER} \n changing current user....")
        # change current user is requested
        if utils.is_continue():

            user = input("Enter the name of the user: ").strip()
            escaped_user = dbconfig.escape_mysql_injectables(user)
            # validating user 
            query  = f'SELECT user FROM mysql.user where user = "{escaped_user}";'
            result = executer(query,'root')

            # cannot execute query 
            if result == const.FAILED:
                print("Cannot Set User...")
                return const.FAILED
            # user is not in mysql.user 
            elif len(result) == '':
                print(f"Mysql User '{user}' Does Not Exists ....")
                # creating user
                if dbconfig.create_user():
                    return set_current_user() # recursing after setting
                else: 
                    print('cannot Set User')
                    return const.FAILED
            # user in mysql.user
            else: 
                #changing the user
                const.CURRENT_USER = user 
                print(f"Current User Has Successfully changed to{const.CURRENT_USER} ...")
                return const.SUCCESS
        else: 
            print("Cannot Change User  : Permission Denied By User ")
            print(f"Current User is : {const.CURRENT_USER}")
            return const.FAILED
    # no current user is set 
    else : 
            
            #TODO * chek this out once 
            user = input("Enter the name of the user : ").strip()
            escaped_user = dbconfig.escape_mysql_injectables(user)
            # validating user 
            query  = f'SELECT user FROM mysql.user where user = "{escaped_user}";'
            result = executer(query,'root')

            # cannot execute query 
            if result == const.FAILED:
                print("Cannot Set User...")
                return const.FAILED
            # user is not in mysql.user 
            elif len(result) == 0:
                print(f"Mysql User '{user}' Does Not Exists ....")
                # creating user
                if dbconfig.create_user():
                    return set_current_user() # recursing after setting
                else: 
                    print('cannot Set User')
                    return const.FAILED
            # user in mysql.user
            else: 
                #changing the user
                const.CURRENT_USER = user 
                print(f"Current User Has Successfully set to{const.CURRENT_USER} ...")
                return const.SUCCESS


                
#TODO to create this function    
# def db_default_config():
#     '''
#     Set The Database Default Configrations

#     '''
#     #  # server check
#     #  if setup.mysql_config() == const.FAILED:
#     #       print('Sorry Server Setup Failed...')
#     # check if databse exists 

#     # create database 
#     query = 'CREATE DATABASE MediLink ;'
#     pass


#TODO create these functions  

def init_db():
  pass    


def executer(query:str ,user:str = const.CURRENT_USER):
    '''
    Takes Query and user , execute query and returns the cursor object 
    
    Args:
        Query: mysql query that is to be executed 
        User: username of  mysql user whose account is to be used for execution of this query\n
        Default_user:  CURRENT_USER
  

    Returns:
        result: result of the query after execution
    '''
    # creating connection 
    con = reconnect(user)
    if con == const.FAILED:
        return const.FAILED
    else:
    
    # creat:ing cursor  
        cursor  = con.cursor()
    
    # execution of query 
    #TODO * handle the error (42000) 1064 wrong syntax
    try : 
        
        cursor.execute(query) 
        return cursor.fetchall()
    except Error as e :
        # error code 
        code = e.errno 
        # we can fix automatically 
        if code in const.CAN_BE_SKIPPED:
            return cursor.fetchall()
        if code in const.NEED_CREATION:
            # TODO : * create a creator functions for this table , database
            return const.FAILED
        if code in const.CRITICAL:
            print(f"An Error Has occured : \n{e}")
            return const.FAILED
        else :
            print(f"An Unknown Error Occured \n{e}")
            return const.FAILED
        




# main line segment 
if __name__ == "__main__" :
    # testing 
    print(reconnect())