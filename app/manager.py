'''
    Contains Crud operations

'''
def connectdb():
    '''
        This will be used to connect to database with provided credentials from the config 
    '''
    # getting configs 
    import json 
    try:
        file = open("config.json")
        config_dict = json.load(file)
        con_dict = config_dict['CONNECTION_CONFIG'] 
        file.close() 
    except FileNotFoundError :
        raise RuntimeError(f'File config.json does not exists')


