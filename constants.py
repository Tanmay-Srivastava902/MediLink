# modules import 
import os 

# defining constants 
SUCCESS = True
FAILED = False
NEEDS_INSTALL = -1 
ATTEMPTS_EXCEEDED = -2

# Limits
MAX_ATTEMPTS = 3 

# system 
UBUNTU_ROOT_PWD = ''# initial root pass

# creating universal env 
MEDILINK_ENV = os.environ.copy() # copying current env settings

def get_config():
    pass

def update_const():
    pass
# Mysql
MYSQL_HOST  = 'localhost' 
MYSQL_ROOT_USER = 'root'
MEDILINK_ENV['MYSQL_PWD'] = ''  # pass var for root user 


# Database DEFAULTS 
DEFAULT_DB = 'MediLink' 
DEFAULT_DB_USER = 'medilink_admin'
MEDILINK_ENV['DEFAULT_DB_PWD'] = ''  # pass var for default database user

# database Currents
CURRENT_DATABASE = '' 
CURRENT_USER = ''

# genral user 
MEDILINK_ENV['USER_PWD'] = ''



# mysql errors that occur during execution of a code by cursor.execute()
# Errors we can fix automatically
NEED_RECONNECT = {
    '2002': 'Server not running',      # Start server
    '2006': 'Server gone away',        # Reconnect
    '2013': 'Connection lost'          # Reconnect
}

# Errors we can recover from
NEED_CREATION = {
    '1046': 'No database selected',    # Can USE database
    '1049': 'Database missing',        # Can CREATE DATABASE
    '1146': 'Table missing',           # Can CREATE TABLE
    '1051': 'Table unknown'            # Can CREATE TABLE
}

# Warnings - can skip/ignore
CAN_BE_SKIPPED= {
    '1050': 'Table already exists',    # Skip if creating
    '1007': 'Database exists'          # Skip if creating
}

# Critical - just show error, can't fix
CRITICAL = {
    '1064': 'Syntax error',            # User's SQL is wrong
    '1054': 'Unknown column',          # Column doesn't exist
    '1062': 'Duplicate entry',         # Constraint violation
    '1452': 'Foreign key fail'         # FK constraint
}