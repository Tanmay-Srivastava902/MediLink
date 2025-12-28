
"""
# # NOTE app configration remained

# def configure_app():
#     '''
#         Creates Necessory Files and Services Requierd To Run Our App

#         :Args:
#           None


#     '''
#     print("Proceed With Caution ! You Are About To Change App Configrations ")
#     if is_continue():
    
#         # getting config 
#         for attempt in range(MAX_ATTEMPTS):

#             print(f"Attempt Left: {MAX_ATTEMPTS-attempt}")
            
#             host = input("Enter Host Name : ")
         
#             # testing above credentials before proceeding
#             try: 

#                 # user setup 
#                 print("Creating User For App \n[Select 'No' If You Alredy Have User 'medilink_admin' Created]\n[OR Select Yes If you have to change the default database user or do not have any existing user]")
#                 if is_continue():

#                     # trying for root access to create user 
#                     root_pwd = gtpass('root','mysql')

#                     # root access granted 
#                     conn = connect(host=host, user='root', password=root_pwd)
#                     cursor = conn.cursor()

#                     # creating user 
#                     query = "CREATE USER %s@%s IDENTIFIED BY %s;"
#                     user  = input("Enter Username For Mysql User : ")
#                     pwd = gtpass(user,"mysql",3) # getting password 
#                     cursor.execute(query, (user, host, pwd)) # user created successfully

#                     # storing password for future use 
#                     print("Root Password Is Being Saved For Future Use If Required")
#                     if is_continue():
#                         # if file already exists 
#                         try : 
#                             with open('app/pwd.dat','rb+') as file : 
#                                 # updating passowrds in configration file
#                                 pwd_dict = pickle.load(file)
#                                 pwd_dict["root"] = root_pwd
#                                 pwd_dict[user] = pwd  

#                                 # reset positions of the curesor 
#                                 file.seek(0)
#                                 file.truncate()

#                                 # updating the new passwords 
#                                 pickle.dump(pwd_dict,file)

#                         # if file is to be created 
#                         except (FileNotFoundError , EOFError , KeyError):

#                             with open('app/pwd.dat' , 'wb') as file :
#                                 pwd_dict = {"root":root_pwd , user : pwd}
#                                 pickle.dump(pwd_dict,file)
#                     else : 
#                         print("You Have Enter Password Manually Each Time When Prompted")
#                     conn.commit()
#                     conn.close()

#                 else:

#                     # proceeding with alredy existing user 
#                     user = input("Enter Username : ")
#                     pwd = gtpass(user,'mysql')

#                 # checking for database
#                 print("Creating Database For App [Select 'No' If Want To Use Existing Database ]")
#                 # user want to crate db
#                 if is_continue() : 
                    
#                     # creating db

#                     conn = connect(host=host)
#                     db = input("Enter Database Name : ")  
#                     query = 'CREATE DATABASE %s ; '

#                     # creating root connection 
#                     root_conn = connect(host=host , user = 'root' , )
                                  
#                     conn = connect(host=host,user=user,password=pwd ,database = db )
#                     conn.close()

#                      # updating the pwd 
#                     try : 
#                             with open('app/pwd.dat','rb+') as file : 
#                                 # updating passowrds in configration file
#                                 pwd_dict = pickle.load(file)
#                                 pwd_dict[user] = pwd  

#                                 # reset positions of the curesor 
#                                 file.seek(0)
#                                 file.truncate()

#                                 # updating the new passwords 
#                                 pickle.dump(pwd_dict,file)

#                         # if file is to be created 
#                     except (FileNotFoundError , EOFError , KeyError):

#                             with open('app/pwd.dat' , 'wb') as file :
#                                 pwd_dict = {user : pwd}
#                                 pickle.dump(pwd_dict,file)
                                
            
#                     # updating config.json file 
#                     with open('app/app_config.json' , 'w') as file :

#                         config_dict  = {"CONNECTION_CONFIG":{ "host": host , "user" : user , "database" : db}}
#                         json.dump(config_dict,file)
                        
#                     print("configrations updated")
#                     return config_dict
                
#                 # user want to configuere with existing  database 
#                 else :   

#                     # connecting to database  
#                     db = input("Enter Database Name : ")                        
#                     conn = connect(host=host,user=user,password=pwd ,database = db )
#                     conn.close()

#                     # updating the pwd 
#                     try : 
#                             with open('app/pwd.dat','rb+') as file : 
#                                 # updating passowrds in configration file
#                                 pwd_dict = pickle.load(file)
#                                 pwd_dict[user] = pwd  

#                                 # reset positions of the curesor 
#                                 file.seek(0)
#                                 file.truncate()

#                                 # updating the new passwords 
#                                 pickle.dump(pwd_dict,file)

#                         # if file is to be created 
#                     except (FileNotFoundError , EOFError , KeyError):

#                             with open('app/pwd.dat' , 'wb') as file :
#                                 pwd_dict = {user : pwd}
#                                 pickle.dump(pwd_dict,file)

#                     # updating config.json file 
#                     with open('app/app_config.json' , 'w') as file :

#                         config_dict  = {"CONNECTION_CONFIG":{ "host": host , "user" : user , "password" : pwd , "database" : db}}
#                         json.dump(config_dict,file)

#                     print("configrations updated")
#                     return config_dict

#             except ProgrammingError as e:
#                 # Wrong user/password (Error 1045: Access denied)
#                 print(f"Authentication failed: {e}")
#                 # print("Wrong username or password. Please try again.")
#                 # sent to retry
#             except InterfaceError as e:
#                 # Can't connect to server (wrong host, server down)
#                 print(f"Cannot connect to server: {e}")
#                 # print("Check if MySQL server is running and host is correct.")
#                 raise RuntimeError("Configs cannot be saved try running app_setup.py ..")
#             except Error as e:
#                 # Other MySQL errors
#                 print(f"MySQL Error: {e}")
#                 raise RuntimeError("Configs cannot be saved try running app_setup.py ..")
        
#         raise RuntimeError("Sorry No Attempt Left ... ")
#     else :
#         raise RuntimeError("Configs cannot be saved :Permittion Denied By User ")
"""
# def load_config():
    