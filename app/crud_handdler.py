'''This Module Handdles Database Crud Operations'''
# importing modules required 
from mysql_handdler import execute_cmd
from utils_handdler import is_continue
# NOTE for select queries multiple run create a file for sving current select query and execute everytime reuired
# DDL Commands
def create(conn,obj_type:str,obj_name:str,struct:str='',db='') -> bool:
    '''
    Creates An Entity In The  Mysql Server

    Args:
        Conn: MysqlConnectionAbstract the connection object
        Obj_type: [table/db] what to create 
        Obj_name: [table_name/db_name] name of entity
        Struct:  structure of table [**in case of table only**]
        Db : database to execute query [**in case of table creation only**]
    Returns: 
        True: If Created 
    Exceptions:
        RuntimeError: Unable to Create
    '''

    # preparing query 
    if obj_type == 'db':

        query = f'CREATE DATABASE {obj_name};'

    elif obj_type == 'table' and struct != '' : 

        # creating table
        query = f'CREATE TABLE {obj_name}({struct}) ;'

    elif obj_type == 'table' and struct == '' :

        # no sturcutre is given in table mode
        raise RuntimeError("No Structure for Table is Provided")
    
    else : 

        raise RuntimeError("Invalid Obj_type Given Please Choose From [table/db]")
    
    try :
        # executing command
        execute_cmd(conn,query)
        # object created successfully 
        print("Object Created Successfully")
        return True
    except RuntimeError as e :
        raise RuntimeError(f"Object Could Not Be Created : {e}")

# NOTE most flexible function in this module
def alter(  conn, operation:str, entity_type:str, 
            old_table_name:str, new_table_name:str='',
            old_column_name:str = '',new_column_config:str= '',
            constraint_config:str =''
         ):
    '''
    Alters The Table Structure 

    Args:
        Conn: MysqlConnectionAbstract the connection object
        Old_Table_name : Actual name of the table
        Operation: [add/drop/modify/rename]
        Entity_type: [column/constraint/table]
        New_table_name : [**in case of rename only**]
        Old_column_name : name of column[**in case of rename only**]
        New_colum_config : 'new_colum_name data_type' in case of add/modify or 'new_column_name' in case of rename else 'new_datatype in case of modify
        Is_constraint: True If [add/drop] a constraint else false
        Constraint_Config : 'constraint_name operation' [**Only if Is_constraint is True**] [**'constraint_name' only in case of drop only**]
    Returns:
        True: if Altered
    Exceptions:
        RuntimeError: if any faliure occures
    '''
    # getting query for operations 
    # constraint operations
    if entity_type.lower() == 'constraint' :
        if operation == 'add' : 
            # adding constraint 
            query =  query = f' ALTER TABLE {old_table_name} ADD CONSTRAINT {constraint_config};'
        elif operation == 'drop' :
            # dropping constraints
            query =  query = f' ALTER TABLE {old_table_name} DROP CONSTRAINT {constraint_config};'
        else : 
            raise RuntimeError(f"Invalild operation {operation} for constraint only [add/drop] is available to choose ")
    # column operations
    elif entity_type.lower() == 'column' : 
        if operation == 'add':
            # adding column 
            query = f' ALTER TABLE {old_table_name} ADD COLUMN {new_column_config};'
        elif operation == 'drop':
            # dropping column 
            query = f' ALTER TABLE {old_table_name} DROP COLUMN {old_column_name};'
        elif operation == 'modify':
            # modifying column 
            query = f' ALTER TABLE {old_table_name} MODIFY COLUMN {old_column_name} {new_column_config};'
        elif operation == 'rename':
            # renaming column 
            query = f' ALTER TABLE {old_table_name} RENAME COLUMN {old_column_name} TO {new_column_config};'
        else : 
            raise RuntimeError(f"Invalild operation {operation} for column only [add/drop/modify/rename] is available to choose ")
    # table operations
    elif entity_type == 'table' :
        if operation == 'rename':
            # renaming column 
            query = f'ALTER TABLE {old_table_name} RENAME TO {new_table_name};'
        else : 
            raise RuntimeError(f"Invalild operation {operation} for table only rename is vaild")
    # invalid operations
    else : 
        raise RuntimeError(f"Invalild entity_type  {entity_type} only [constraint/column/table] is available to choose ")
    
     
    try :
        # executing command
        execute_cmd(conn,query)
        # object created successfully 
        print(f"Table Altered Successfully ! {entity_type} {operation}ed ")
        return True
    except RuntimeError as e :
        raise RuntimeError(f"Could Not Alter Table : {e}")


def drop(conn,obj_type:str,obj_name:str) -> bool:
    '''
    Drops An Entity In The  Mysql Server

    Args:
        Conn: MysqlConnectionAbstract the connection object
        Obj_type: [table/db] what to create 
        Obj_name: [table_name/db_name] name of entity
    Returns: 
        True: If Dropped 
    Exceptions:
        RuntimeError: Unable to Drop
    '''
    print(f"Warining ! You Are About TO Drop {obj_type} '{obj_name}'")
    # confirming deletion
    if not is_continue():
        raise RuntimeError(f"User Denied TO Drop {obj_type} '{obj_name}'")
    
    # preparing query 
    if obj_type == 'db':

        query = f'DROP DATABASE {obj_name};'

    elif obj_type == 'table': 

        # creating table
        query = f'DROP TABLE {obj_name} ;'
    
    else : 

        raise RuntimeError("Invalid Obj_type Given Please Choose From [table/db]")
    
    try :
        # executing command
        execute_cmd(conn,query)
        # object created successfully 
        print("Object Dropped Successfully")
        return True
    except RuntimeError as e :
        raise RuntimeError(f"Object Could Not Be Dropped : {e}")
    
    
# DML commands
def insert(conn ,table_name:str,params:tuple,column_order:tuple):
    '''
    Updates An Entity In The Table

    Args:
        Conn: MysqlConnectionAbstract the connection object
        Table_name:  name of table
        Coumn_order: (clumn2,column3,colum5) order of columns in which vaues are to inserted
        Params: tuple of parameters to insert into placeholders
    Returns: 
        True: If Updated 
    Exceptions:
        RuntimeError: Unable to Update

    '''
    try :
        values = ','.join(['%s'] * len(params)) # (%s,%s) add placeholders %s as value according to the length of parameters given
        query = f'INSERT INTO {table_name} {column_order} VALUES ({values}) ;'
        execute_cmd(conn,query,params)
         # object updated successfully 
        print("Inserted Successfully")
        return True
    except RuntimeError as e :
        raise RuntimeError(f"Could Not Insert : {e}")

def update(conn ,table_name:str, set_clause:str,condition:str,params:tuple):
    '''
    Updates An Entity In The Table

    Args:
        Conn: MysqlConnectionAbstract the connection object
        Table_name:  name of table
        Set_clause: 'column1 = 'value1',column2 = 'value2'' string conaining colum names and values to set during update 
        Condition: condition for where clause [**always use %s for values**] 
        Params: tuple of parameters to insert into placeholders
    Returns: 
        True: If Updated 
    Exceptions:
        RuntimeError: Unable to Update

    '''
    try : 
        query = f'UPDATE {table_name} SET {set_clause} WHERE {condition};'
        execute_cmd(conn,query,params)
         # object updated successfully 
        print("Table Updated Successfully")
        return True
    except RuntimeError as e :
        raise RuntimeError(f"Table Could Not Be Updated : {e}")


def delete(conn ,table_name:str, condition:str,params:tuple ):
    '''
    Deletes An Entity In The Table

    Args:
        Conn: MysqlConnectionAbstract the connection object
        Table_name: name of table
        Params: tuple of parameters to insert into placeholders
        Conditions: condition for where clause
        [**always use %s in condition for where clause**]
    Returns: 
        True: If Deleted 
    Exceptions:
        RuntimeError: Unable to Delete

    '''
    try : 
        query = f'DELETE FROM {table_name}  WHERE {condition};'
        execute_cmd(conn,query,params)
         # object updated successfully 
        print("Deleted Successfully")
        return True
    except RuntimeError as e :
        raise RuntimeError(f"Could Not Delete: {e}")
