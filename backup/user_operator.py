'''This module handles all user operations on table basis'''
# from mysql_handdler import create_conn
# from file_handdler import session_handdler
# # table level operations
# def auth(id:int,pwd:str,name:str,table_name:str):
#     '''
#     Authenticates User From The Table given Ture if authorized else False Raises RuntimeError otherwise

#     Args:
#         Id: user id to authenticate
#         Pwd : password to authenticate
#         Name : name of user getting correct user to verify
#         Table_name: [**table_name of user table where the passowrd for users is stored**] 

#     '''
#     try :
#         query = f'SELECT user FROM {table_name} WHERE id = %s and user = '
        
            
# NOTE create seprate managemetn for patient an doctor  Operators should be specific to table names and they should have fixed coulnm names 