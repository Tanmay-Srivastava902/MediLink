# modules import 
import os 

# defining constants 
SUCCESS = 1
FAILED = 0 
NEEDS_INSTALL = -1 

# Limits
MAX_ATTEMPTS = 3 

# Mysql
MYSQL_HOST  = 'localhost' 
MYSQL_DEFAULT_USER = 'medilink_admin'
DEFAULT_DATABASE = 'MediLink' 
# Universal shared environment 
MYSQL_ROOT_ENV  = os.environ.copy()  # copying the environment
MYSQL_ROOT_ENV['MYSQL_PWD'] = ''  # initializing mysql_pswd variable