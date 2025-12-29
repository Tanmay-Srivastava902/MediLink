'''
    This Module Contains the Functions For Operating With Mysql
'''
# importing modules 

# built in modules 
from mysql.connector import connect , Error
from mysql.connector.errors import InterfaceError , ProgrammingError 
# external modules 
from utils_handdler import MAX_ATTEMPTS , gtpass , is_continue
from file_handdler import pwd_handdler 

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
            params : tuple('value1','value2') value to be filled in placeholders '%s' in the query while execution
        Returns:
            list[tuple]: Result of the query executed if any else empty list '[]'
        Exceptions:
            RuntimeError : If any problem if any error occured
    '''
    try :   
        # creating cursor with buffered=True to avoid "Unread result found" error
        cursor  = conn.cursor(buffered=True) 

        if params : 
            cursor.execute(query,params) # executing query with parameters provided
        else :
            cursor.execute(query) # executing query without parameters
        output = cursor.fetchall() # fetching results 
        conn.commit()
        cursor.close() # close cursor after use
        return output
    
    # errors comming from cursor side while execution and fetching
    except Error as e :
        raise RuntimeError(f"Sorry Could Not Execute : {e}")  


def create_user() -> str:
    '''
    Creates A Mysql Use And Returns user If Created Else RuntimeError
    '''
    print("Creating Mysql User")

    for attempt in range(MAX_ATTEMPTS):

        print(f'Attempts Left : {MAX_ATTEMPTS-attempt}')

        # getting user details 
        hostname = input('Enter Hostname : ').strip()
        user  = input('Enter Username : ').strip()

        if user == '' or hostname == '' :
            print("Username or Hostname cannot Be Empty")
            continue # please retry 
        else:
            password  = gtpass(user,'mysql',3)


        # getting root password 
        try : 
            root_pwd = pwd_handdler('load','root')
        except RuntimeError as e: 
            print(f"No Saved Password Found For Mysql Root User")
            root_pwd = input("Enter Mysql Root password : ")
        
        # connecting to mysql 
        try : 
            conn = create_conn(host='localhost',user='root',pwd=root_pwd)
        except RuntimeError as e :
            print( e,'Please Retry')
            continue # retrying to connect 

        # saving root password 
        try :
            pwd_handdler('update','root',root_pwd) 
        except RuntimeError :
            print("Password Is Not Saved  For Root ! You May Need To Re-enter It in Future Again ")

        # preparing query 
        query = 'CREATE USER %s@%s IDENTIFIED BY %s ; '
        params = (user,hostname,password) 

        # executing query 
        try : 
            execute_cmd(conn,query,params)
            conn.close()

            # saving password 
            print(f"Saving password For '{user}' For Future")
            if is_continue() : 
                try : 
                    pwd_handdler('update',user,password)
                except RuntimeError :
                    print(f"Could Not save Password  ! You May Require To Re-enter In Future ")
                finally: 
                    # printing success msg 
                    print(f"Mysql User '{user}' Created Successfully")
                    return user
            else: 
                print("Mysql User Created Successfully ! Password Not Saved !You May Require To Re-enter In Future")
                return user

        except RuntimeError  as e : 
            # Check if user already exists (Error 1396)
            if "1396" in str(e):
                print(f"User '{user}'@'{hostname}' already exists. Please choose a different username or hostname.")
                continue  # retry with different credentials
            else:
                raise RuntimeError(f"Cannot Create User Failed To Execute {e}")
        

    raise RuntimeError('Could Not Create User Max Attempts Reached ')

def update_pwd(user:str,host:str) -> str:

    '''Updates Password Of Mysql User'''

    print(f"Changing Password For User {user}..")

    for attempt in range(MAX_ATTEMPTS):

        print(f'Attempts Left : {MAX_ATTEMPTS-attempt}')

        # getting user details 
        password  = gtpass(user,'mysql',3)

        # getting root password 
        try : 
            root_pwd = pwd_handdler('load','root')
        except RuntimeError as e: 
            print(f"No Saved Password Found For Mysql Root User")
            root_pwd = input("Enter Mysql Root password : ")
        
        # connecting to mysql 
        try : 
            conn = create_conn(host='localhost',user='root',pwd=root_pwd)
        except RuntimeError as e :
            print( e,'Please Retry')
            continue # retrying to connect 

        # saving root password 
        try :
            pwd_handdler('update','root',root_pwd) 
        except RuntimeError :
            print("Password Is Not Saved ! You May Need To Re-enter It in Future Again ")

        # preparing query 
        query = 'ALTER  USER %s@%s IDENTIFIED BY %s ; '
        params = (user,host,password) 
    
        execute_cmd(conn,query,params)
        conn.close()

        # saving password 
        print(f"Saving password For '{user}' For Future")
        if is_continue() : 
            try : 
                pwd_handdler('update',user,password)
            except RuntimeError :
                print(f"Could Not save Password  ! You May Require To Re-enter In Future ")
            finally: 
                # printing success msg 
                print(f"Password for Mysql User '{user}' Changed Successfully")
                return password
        else: 
            print(f"Password for Mysql User '{user}' Changed Successfully")
            return password
        

    raise RuntimeError('Could Not Create User Max Attempts Reached ')
        
        


# # main line segment 
# if __name__ == "__main__":
#     try:
#         pwd  = pwd_handdler('load','root')
#         print('Current root password is :' , pwd)
#         conn = create_conn('localhost','root',pwd)
#         res = execute_cmd(conn , 'SELECT user,host from mysql.user ;')
#         print("user table before " , res)
#         user = create_user()
#         print(res)
#         res = execute_cmd(conn , 'SELECT user,host from mysql.user ;')
#         print("user table after user creation " , res)
#         pwd = pwd_handdler('load',user)
#         print(f"password for new_user {user} is : " , pwd)
#         pwd = update_pwd(user,'localhost')
#         print(pwd)
#         pwd = pwd_handdler('load',user)
#         print(f"password for new_user {user} after updation is : " , pwd)

#     except Exception as e :
#         print("the error is :" , e )
