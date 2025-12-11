# modules import 
import os 

# defining constants 
SUCCESS = True
FAILED = False
NEEDS_INSTALL = -1 

# Limits
MAX_ATTEMPTS = 3 

# system 
UBUNTU_ROOT_PASS = '' # initial root pass

# Mysql
MYSQL_HOST  = 'localhost' 
MYSQL_ROOT_USER = 'root'


# Database 
DEFAULT_DATABASE = 'MediLink' 
DEFAULT_DATABASE_USER = 'medilink_admin'
# DEFAULT_DATABASE_USER = 'tanmay'


# Universal shared environment 
MYSQL_ENV  = os.environ.copy()  # copying the environment
MYSQL_ENV['MYSQL_PWD'] = ''   # initialize mysql root user pass
MYSQL_ENV['DB_USER_PWD'] = ''  # initial mysql database user pass 


