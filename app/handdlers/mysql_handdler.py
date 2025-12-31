'''
    This Module Contains the Functions For Operating With Mysql
'''
# importing modules 

# built in modules 
from mysql.connector import connect , Error
from mysql.connector.errors import InterfaceError , ProgrammingError 
# external modules 
from handdlers.utils_handdler import MAX_ATTEMPTS , gtpass , is_continue
from handdlers.file_handdler import pwd_handdler
from handdlers.system_handdler import service_manager
def save_root_pwd() -> bool:
    '''This function updates the mysql root pwd in the file'''
     # trying to save  mysql sudo pwd 
    try : 
        # mysql root pwd
        for attempt in range(MAX_ATTEMPTS):
            if attempt > 0:
                print(f'Attempt Left {MAX_ATTEMPTS-attempt}')
            host = input('Enter hostname genrally use \'localhost\' : ').lower()
            root_pwd = gtpass('root','mysql')
            # verifying pwd
            try : 
                connect(host = host , user = 'root' , password = root_pwd)
                pwd_handdler('update','root',root_pwd)
                print('Saved Mysql Root Passowrd')
                return True
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
                raise RuntimeError(f'Unexpected Error : {e}')
        else: 
            # end of attempts
            print('Sorry Max Attempt Reached')
            raise RuntimeError('Max Attempt Reached')
    
    except RuntimeError as e :
        raise RuntimeError(f'Cannot Save Password For Mysql Root! {e} ')


def create_conn(host:str,user:str,pwd:str,db:str = ''):
    '''
        returns a mysql connection if sucess otherwise raise runtime error 
    '''
    try : 
         con = connect(host = host , user = user , password = pwd , database=db)
         return con
    
    except ProgrammingError as e:
        # Wrong user/password (Error 1045: Access denied)
        raise RuntimeError(f"Authentication Failed {e}")
    except InterfaceError as e:
        # # Can't connect to server (wrong host, server down)
        raise RuntimeError(f"Cannot connect to server: {e} ..")
    except Error as e:
        # Other MySQL errors
        print(f"MySQL Error: {e}")
        raise RuntimeError("Configs cannot be saved try running app_setup.py ..")


def execute_cmd(conn,query:str,params:tuple = ()) -> list[tuple[str]]:
    '''
        Executes a query and returns the all rows fetched or emptly list or error 
        [**kwargs needed only when root_access is set to false**]

        Args:
            conn : mysql connection object by which we have to execute the query 
            Query : query to be executed
            params : tuple('value1','value2') value to be filled in placeholders %s in the query while execution
        Returns:
            list[tuple]: Result of the query executed if any else empty list '[]'
        Exceptions:
            RuntimeError : If any problem if any error occured
    '''
    try:
        # creating cursor with buffered=True to avoid "Unread result found" error
        cursor = conn.cursor(buffered=True)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Only fetch results for SELECT/SHOW/DESCRIBE/EXPLAIN queries
        query_type = query.strip().split()[0].lower()
        if query_type in ("select", "show", "describe", "explain"):
            output = cursor.fetchall()
        else:
            output = []

        cursor.close()  # close cursor after use
        return output

    # errors coming from cursor side while execution and fetching
    except Error as e:
        raise RuntimeError(f"Sorry Could Not Execute : {e}")


def create_user(root_conn,user:str,host:str,with_pwd:bool = False , pwd:str = '') -> bool:
    '''
    Creates A Mysql Use And Returns user If Created Else RuntimeError
    
    Args:
        Root_onn : mysql connection object as root user
        User : username
        Hostname : hostname 
        With_pwd : True if want to create user with pwd else False
        Pwd : password of user [**If with_pwd is set to True]
    '''

    print(f"Creating Mysql User '{user}'")
    try :
        # creating user without pwd
        if not with_pwd :

            # preparing query 
            query = "CREATE USER  %s@%s;"
            params = (user,host)
            
            # executing query 
            execute_cmd(root_conn,query,params)
            # success 
            print(f"Mysql User '{user}' Created Successfully ! Don't Forget To Add Pwd Later")
            return True
        # creating user with pwd
        else : 
            # preparing query 
            query = "CREATE USER %s@%s IDENTIFIED BY %s ; "
            params = (user,host,pwd) 

        
            # executing query 
            execute_cmd(root_conn,query,params)

            # saving password 
            print(f"Saving password For '{user}' For Future")
            if is_continue() : 
                try : 
                    pwd_handdler('update',user,pwd)
                except RuntimeError :
                    print(f"Could Not save Password  ! You May Require To Re-enter In Future ")
                finally: 
                    # printing success msg 
                    print(f"Mysql User '{user}' Created Successfully")
                    return True
            else: 
                print("Mysql User Created Successfully ! Password Not Saved !You May Require To Re-enter In Future")
                return True
    except RuntimeError  as e : 
            # Check if user already exists (Error 1396)
            if "1396" in str(e):
                print(f"User {user} Already Exists")
                return True
            else:
                raise RuntimeError(f"Cannot Create User Failed To Execute {e}")
            

    
def grant_privileges(root_conn , user:str ,host:str,privilege_list:list[str],obj_name:str) -> bool:
    '''
    Updates given Privileges for the given user returns True if updated Else Raise a RuntimeError

    Args:
        Root_conn: mysql connection object as root user [**root is required here**]
        User: mysql username 
        Host: mysql hostname usually 'localhost'
        Privilege_list: list of priveleges to grant ['All Privileges'] or ['privilege1','prevelege2']
        obj_name: 'db_name' in case of table and 'db_name.table_name' in case of table 
    Returns:
        True: if done 
    Raises: 
        RuntimeError: in case of exception
    '''
    # preparing query 
    privileges = ','.join(privilege_list)
    query = f"GRANT {privileges.upper()} ON {obj_name} TO %s@%s;"
    params = (user,host)
    flush_query = 'FLUSH PRIVILEGES;'
    # executing query 
    try:
        print(f"Granting Privileges To Mysql User '{user}'")
        # exceuting query 
        execute_cmd(root_conn,query,params) 
        # flushing priviliges 
        execute_cmd(root_conn,flush_query)
        # privileges granted
        print("Privileges Granted")
        return True
    except RuntimeError as e : 
        raise RuntimeError(f"Could Not Grant Privileges : {e}")
    
def change_pwd(root_conn , user:str,host:str) -> bool:

    '''Updates Password Of Mysql User And Returns True
        Args:
        Root_conn: mysql connection object as root user [**root is required here**]
        User: mysql username 
        Host: mysql hostname usually 'localhost'
        Pwd : passowrd 
    Returns:
        True: if done 
    Raises: 
        RuntimeError: in case of exception
    '''

    print(f"Changing Password For User {user}..")
    try:
        for attempt in range(MAX_ATTEMPTS):
            if attempt > 0 : 
                print(f"Attempts Left {MAX_ATTEMPTS-attempt}")

            pwd = gtpass(user,'mysql',3)
            # preparing query 
            query = "ALTER  USER %s@%s IDENTIFIED BY %s ; "
            params = (user,host,pwd) 

            execute_cmd(root_conn,query,params)
            # saving password 
            print(f"Saving password For '{user}' For Future")
            if is_continue() : 
                try : 
                    pwd_handdler('update',user,pwd)
                except RuntimeError :
                    print(f"Could Not save Password  ! You May Require To Re-enter In Future ")
                    return True
                finally: 
                    # printing success msg 
                    print(f"Password for Mysql User '{user}' Changed Successfully")
                    return True
            else: 
                print(f"Password for Mysql User '{user}' Changed Successfully")
                return True
        else:
            raise RuntimeError("Max Attempts Reached") 
         
    except RuntimeError as e :
        raise RuntimeError(f"Password Change Error : {e}")

        
        


# # # main line segment 
# if __name__ == "__main__":
#     try:
#         print(save_root_pwd())
#         pwd  = pwd_handdler('load','root')
#         print('Current root password is :' , pwd)
# #         conn = create_conn('localhost','root',pwd)
# #         res = execute_cmd(conn , 'SELECT user,host from mysql.user ;')
# #         print("user table before " , res)
# #         user = create_user()
# #         print(res)
# #         res = execute_cmd(conn , 'SELECT user,host from mysql.user ;')
# #         print("user table after user creation " , res)
# #         pwd = pwd_handdler('load',user)
# #         print(f"password for new_user {user} is : " , pwd)
# #         pwd = update_pwd(user,'localhost')
# #         print(pwd)
# #         pwd = pwd_handdler('load',user)
# #         print(f"password for new_user {user} after updation is : " , pwd)

#     except Exception as e :
#         print("the error is :" , e )
