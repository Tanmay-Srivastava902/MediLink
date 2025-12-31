'''handdles initial setup of the App'''
from handdlers.file_handdler import json_handdler , pwd_handdler , session_handdler
from handdlers.checks_handdler import check_system , check_server,check_files,check_venv
from handdlers.mysql_handdler import create_user , create_conn,change_pwd , grant_privileges
from handdlers.crud_handdler import create , alter
import math 
def install_app() -> bool:

    # getting app configrations
    app_config = json_handdler('load','APP_CONFIG')
    author_config = json_handdler('load','AUTHOR_CONFIG')
    # printing welcome line
    main_line = f"Wlelcome To {app_config['app_name']} ! {app_config['app_tagline']}"
    print(main_line)
    # printing by line 
    by_line = f"By {author_config['name']}"
    indent = math.floor(len(main_line) - len(by_line))
    print(' ' * indent + by_line)

    try:
        print("Checking For Dependencies")
        # configuring system 
        check_system()
        # checking files
        check_files()
        # checking veirtual environment
        check_venv()
        # checking mysql server
        check_server()
        # all checks done 
        print("Completed Initial Checks")
    except RuntimeError as e : 
        raise RuntimeError(f"Checks Failed ! {e}")

  
    # settting up app configrations
    try: 
        # getting credentials 
        host = app_config['host']
        root_pwd = pwd_handdler('load','root')

        # creating connection with mysql server as root user
        print("Connecting To Mysql Server !")
        root_conn = create_conn(host,'root',root_pwd)
        print("Connected ")

        # creating database
        print("Creating App Database")
        create(root_conn,'db',app_config['app_db'])
        print("Database Created ")

        # creating app admin 
        print("Creating App Admin")
        create_user(root_conn,app_config['app_admin'],app_config['host'])
        print("User Created ")

        # setting password for app admin 
        print("Important ! Setting Admin Password ")
        change_pwd(root_conn,app_config['app_admin'],app_config['host'])
        print("Password Changed And Saved ")

        # getting all  privileges on admin
        obj_name = f'{app_config['app_db']}.*'
        grant_privileges(root_conn,app_config['app_admin'],app_config['host'],['ALL PRIVILEGES'],obj_name)
        
        # closing root connection from here
        root_conn.commit()
        root_conn.close()

        # creating connection from mysql server as database admin wiht app database
        admin_pwd = pwd_handdler('load',app_config['app_admin']) 
        admin_conn  = create_conn(app_config['host'],app_config['app_admin'],admin_pwd,app_config['app_db'])
        print("Swithed To Admin Account")

        # updating session to use current configs
        print("Saving Crrent Session State")
        session_dict = {"host":app_config['host'],"user":app_config['app_admin'],"pwd":admin_pwd,'db':app_config['app_db']}
        session_handdler('update',session_dict)
        print("Session Saved")




        # creating tables
        print("Creating Requred Tables In App Database")

        # getting table config
        table_config = json_handdler('load' ,"TABLE_CONFIG")

        # getting table info 
        table_info  = table_config['table_info'] # getting list containing table struct and table name 
        table_info = list(table_info) # converting it to list for covinience
        # now table_info  = [[table_name,table_struct],[table_name,table_struct]]

        for table in table_info: 

            # table  = [table_name,table_struct]
            table_name = table[0]
            table_struct = table[-1]

            # creating table
            create(admin_conn,'table',table_name,table_struct)
            print(f"Created Table {table_name}")
        
        # creating 
        print("Tables Created")


        # modifying Tables Structure adding foreign keys
        fk_info = table_config['foreign_key_info']
        fk_info = list(fk_info) # converting it to list for covinience
        # now table_info  = [[table_name,fk_config1,fk_config2],[table_name,fk_config1 , fk_config2]]

        for fk in fk_info: 
            # fk = [table_name,fk_config1,fk_config2]
            fk = list(fk)
            table_name = fk[0] # got table name 
            # got all forign key configs 
            fk_config_list= fk[1:] 
            # got constraint config list = [fk_config1 ,fk_config2] all the rest configs remains
            for fk_config in fk_config_list : 
                # creating constraints
                alter(admin_conn,'add','constraint',old_table_name=table_name,constraint_config=fk_config)
                
            print(f"Foreign Keys Added TO Table {table_name}")
        
        print("Modifications Made Successfully")





        

        print("App Initialized Successfully")
        return True
    except RuntimeError as e : 
        raise RuntimeError(f"Initialization Failed ! Error : {e} ")

if __name__ == "__main__":
    
    try : 
        print(install_app())
    except RuntimeError as e : 
        print(f"Error is : {e}")



    

        

    
    