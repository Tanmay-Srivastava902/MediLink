# imports 
from mysql import connector  
import setup 
import utils 
import dbconfig
import constants as const 
from time import sleep as wait

def set_db_user_pass():
            '''
            Updates the DB_USER_PWD In The Env 

            Args:
                
                None 
            
            Returns:
                True: if pass update sucessfull
                False: if pass update Failed  
            '''

            print(' Warning : password For Database Default User Is Not Set ...')
            print(f' Important ! Getting Password For Database User {const.DEFAULT_DATABASE_USER} \n ')
            # Getting password 
            userpass = utils.gtpass()

            # adding passowrd for db_user 
            is_auth = dbconfig.auth_user(
                                        user = const.DEFAULT_DATABASE_USER,
                                        Env_var= "DB_USER_PWD"  
                                        )
            # if auth is Successful 
            if is_auth :

                print('User Password Is Stored Sucessfully')
                # updating the password to environment settings 
                const.MYSQL_ENV['DB_USER_PWD'] = userpass
                return const.SUCCESS

            # if auth is failed  
            else : 

                print(f'password Set Failed.. \n Exiting....')
                return const.FAILED if utils.is_continue() else exit(0)
            
def executer(query:str ,user:str):
    '''
    Takes Query and user , execute query and returns 
    
    :Args
    
    :param query: mysql query that is to be executed 
    :type query: str
    :param user: mysql user whose account is to be used for execution of this query 
    :type user: str

    Returns:

        res : after execution result of the query 
    '''
    # creating connection 
    con = connect_db("db_user")
    cursor = con.cursor()
    output = cursor.execute(query)
    print(output)


def create_default_db(name:str):
    # checking if alredy exists 
    query = 'show databases;'
    pass 
def db_admin_operation():
     pass


def connect_db(role : str):
    '''
    Opens a MySQL database connection b/w python and mysql
    
    Automatically sets MySQL root password if not already configured.
    
    Args:
        role:

            root_user- gets  access mysql root shell\n
            db_user- gets access specific database realted features 
    Returns:

        connection object: MySQL connection if successful
        const.FAILED: If connection fails (and user chooses to continue)
        
    Exits:
        Program exits if connection fails and user chooses not to continue
    '''    
    
        
    print('Getting Mysql Root Password....')

    if const.MYSQL_ENV['MYSQL_PWD'] == '' : 
        print('Unable To Find Mysql Root  Password..')
        is_set = dbconfig.set_mysql_root_pass()
        if  is_set == const.FAILED :
            return const.FAILED if utils.is_continue() else exit(0)
    print('Connecting To Database Please Wait...')
    wait(2)

    try : 

        if role == 'root_user':
            conn = connector.connect(
                                    host=const.MYSQL_HOST,
                                    user=const.MYSQL_ROOT_USER,
                                    password=const.MYSQL_ENV['MYSQL_PWD'],
                                    )
        elif role == 'db_user':
            conn = connector.connect(
                                    host=const.MYSQL_HOST,
                                    user=const.DEFAULT_DATABASE_USER,
                                    password=const.MYSQL_ENV['DB_USER_PWD'],
                                    database=const.DEFAULT_DATABASE
                                    )
        else :
            print(f'Unknown Role Defined Cannot Access {role} Exitting..')
            return const.FAILED if utils.is_continue() else exit(0) # if user sitll wan't to continue
        
        # establish connection no error 
        print('Connection Established..')
        return  conn
    
    except connector.Error  as e : 
        print(f'Connection Failed... \n {e}\nCaution: Continuation may leads to Error....')
        return const.FAILED if utils.is_continue() else exit(0) # if user sitll wan't to continue


# main line segment 
if __name__ == "__main__" :
    # # testing 
    # is_set  = set_db_user_pass()
    # if is_set :
    #      con = connect_db('db_user')
    #      print(con)
    #      con.close()
    # else : 
    #      print('falied to set ')
    # # con.close()
    executer("select 1 ;" , 'tanmay')
