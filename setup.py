# Importing Required Modules 
import subprocess  # for handling processes 
import getpass # for hiding password in terminal 
import time # for delay effect
import utils # for utility functions 
import constants as const 




# Set / Update Sudo  Password Globally 
def set_sudo_pass():
    '''
    Set A Password For Mysql Root User If Not Done Alredy 

    Args:

        None 
    
    Return:

        SUCCESS : if password is configured 
        FAILED : if password is not configured 

    '''
    
    # attempting Sudo access for password verification
    for attempt in range(3): # three attempts given 
        # getting password 
        current_pass  = getpass.getpass('Please Enter Your Sudo  Password : ')  # getting password hidden from terminal log
        print('Password Captured ')

        # Running sudo to validate
        res  = subprocess.run(
                                ['sudo' , '-S' , 'su'],  # -s sends one time input  to shell and closes the pipe immediately 
                                input=current_pass + '\n',  # sending input to the terminal 
                                capture_output=True,   # to avoid terminal interruption
                                text=True # dechipher the output into stderr and stdout
                                )
        
        # checking the return codes o
        # execution success : password verified
        if res.returncode == 0 : 
            print('Password Verified : This password will be  used for all future sudo requirements')
            # Updating Global Root Password 
            
            const.UBUNTU_ROOT_PASS = current_pass 
            return const.SUCCESS  # success password updated 
        # wrong password 
        elif res.returncode == 1 :  
            print(f'Sorry wrong Password please try again attempt left : {3 - (attempt +1)}')
        # unknown error 
        else :  
            print(f"Sorry An Error has occurred \n {res.stderr}")
            return const.FAILED
    # attempts ended
    print('sorry no attempts left Exiting... ')
    return const.FAILED

# Running command as sudo 
def run_as_sudo(command : list[str]):  # setting hint for command argument
    '''
    Run Commands As Root User For System Level Operations  And Returns The Output Of it 
    '''
    # getting root password 
      
    # Ensuring the password is set
    if const.UBUNTU_ROOT_PASS is None :
        set_sudo_pass() 
    # executing commands with root access
    result  = subprocess.run(['sudo' ,'-S'] + command ,  # adding sudo to the command 
                        input=const.UBUNTU_ROOT_PASS + '\n', # sending password 
                        capture_output=True,
                        text=True)
    return result   # sending result back 



# Managing Server Status 
def service_manager(service :str, operation : str): 
    # # NOTE Service : apache2 / mysql etc .. , operation : start /stop / status
    #   # getting global password for sudo operation
    result  =  run_as_sudo(['systemctl' , operation , service])    # getting the result of command
    # Ex - command will now become :  sudo systemctl start apache2 
    # return result # getting the result back 
    
    # if status has requested 
    if operation == 'status' : 
        print(f'getting {service} status ... ')
        time.sleep(0.5)
        status = result.returncode 

        # sending status 
        if status == 0 :   # service is running properly
            print(f'{service} is Running Properly')
            return const.SUCCESS  # started 
        elif status  == 3 : # service is not running
            print(f'{service} Is Stopped' )
            return const.FAILED # FAILED 
        # service install required 
        else : 
            # ask user whether to install or quit 
            print(f'{service} Install Required')
            return const.NEEDS_INSTALL 
    
    # if start has requested
    elif operation == 'start' :
        print(f'starting {service}.... ')
        time.sleep(0.5)
        if result.returncode  == 0 :
            print(f' {service} has Started')
            return const.SUCCESS
        else : 
            print(f'{service} could not be Started : \n {result.stderr}')
            return const.FAILED
    
    # if stop has requested
    elif operation == 'stop' :
        print(f'stopping {service}.... ')
        time.sleep(0.5)
        if result.returncode  == 0 :
            print(f' {service} has Stopped successfully...')
            return const.SUCCESS # success
        else : 
            print(f'{service} could not be Stopped : \n {result.stderr}')
            return const.FAILED # FAILED 
    # if restart was requested 
    elif operation == 'restart' :
        if result.returncode == 0 : 
            print(f' {service} has restarted successfully...')
            return const.SUCCESS # success
        elif result.returncode == 5 : 
            print(f'{service} is not installed ')
            return const.NEEDS_INSTALL 
        else : 
            print(f'Restart FAILED : \n {result.stderr}')
            return const.FAILED # FAILED 
            
        
    # if don't know what requested
    else : 
        print(f'Unknown Error occurred')
        return



# for installation of service
def package_installer( package_type : str  , package : str) :
    # type : system / python  package mysql-connector-python
    print(f'Package Installer has started... \n Installing {package}...')
    # asking the user 
    if not utils.is_continue() :
        exit() 

    time.sleep(0.5)
    print(f"installing  {package} Please wait...")

    # installing system package
    if package_type == 'system' :
        
        result  = run_as_sudo(['apt' , 'install' , '-y' ,  package])
        if result.returncode == 0 :
            print(f'Installation successful : {package} Installed')
            return const.SUCCESS # success
        else : 
            print(f'Package Installation FAILED : \n{result.stderr} \n program may not run as usual if proceeded ...')
            return const.FAILED if utils.is_continue() else exit()   # FAILED 
            # user can continue but without this package or exit here 

    # installing python package
    elif package_type == 'python' : 
        try : 
            result = run_as_sudo(['pip' , 'install' , package]) 
            # ex - pip install mysql-connector-python
            if result.returncode == 0 :
                print(f'Installation success : {package} Installed')
                return const.SUCCESS # success
            else : 
                print(f'Package Installation FAILED : \n{result.stderr} \n program may not run as usual if proceeded ...')
                return const.FAILED if utils.is_continue() else exit()   # FAILED 
        
        # pip installation required
        except FileNotFoundError :
            print(f'pip is not installed : Fixing please wait.....')
            installed = package_installer('system' , 'python3-pip')  # installing as system package 
            
            # pip is now installed , now installing the package requested 
            if installed : 
                result = run_as_sudo(['pip' , 'install' , package]) # installing the package
                # ex - pip install mysql-connector-python
                # installed package 
                if result.returncode == 0 :
                    print(f'Installation successful : {package} Installed')
                    return const.SUCCESS # success
                # package FAILED to install
                else : 
                    print(f'Package Installation FAILED : \n{result.stderr} \n program may not run as usual if proceeded ...')
                    return const.FAILED if utils.is_continue() else exit()   # FAILED 
            # pip FAILED to install
            else :
                print(f'Package Installation FAILED : \n{result.stderr} \n program may not run as usual if proceeded ...')
                if utils.is_continue() :
                    return const.FAILED # 
                else :
                    exit()
    # Unknown package_type variable 
    else : 
        print('package_type of package is incorrect please select from (system / python)')
        return const.FAILED # FAILED  

   
# apache server configuration
def apache_config():
    # getting server status 
    status  = service_manager('apache2' , 'status')  # getting the result of the command 

    # running 
    if status == const.SUCCESS  : 
        print('Apache Server Setup successful...')
        return const.SUCCESS # setup success
    # server is stopped
    elif status == const.FAILED :
        # starting 
        started = service_manager('apache2' , 'start')
        if started : 
            print(' Apache Server Setup success...')
            return const.SUCCESS # success
        else : 
            print('Apache Setup FAILED  : Exiting......')
            return const.FAILED if utils.is_continue() else exit() # FAILED 
    # not installed 
    elif status == const.NEEDS_INSTALL : 
        print('Installing...')
        installed = package_installer('system' , 'apache2')
        if installed  : 
            print('Apache Server Setup success...')
            return const.SUCCESS # success
        else : 
            print('Apache Setup FAILED  : Exiting......')
            return const.FAILED if utils.is_continue() else exit()  # FAILED 
                
    else  :   # unknown error Setup FAILED 
        print('Unknown Error occurred \n configuration UnSUCCESSful Exiting.....')
        return const.FAILED
                
   
# mysql configuration 
def mysql_config() :

    # getting server status 
    status  = service_manager('mysql' , 'status')  # getting the result of the command 

    # running 
    if status == const.SUCCESS  : 
        print('mysql Server Setup successful...')
        return const.SUCCESS # setup success
    # server is stopped
    elif status == const.FAILED :
        # starting 
        started = service_manager('mysql' , 'start')
        if started : 
            print('Mysql Server Setup successful...')
            return const.SUCCESS # success
        else : 
            print(f'Mysql Setup FAILED  : Exiting......')
            return const.FAILED if utils.is_continue() else exit() # FAILED 
    # not installed 
    elif status == const.NEEDS_INSTALL : 
        installed = package_installer('system' , 'mysql-server')
        if installed  : 
            print('Mysql Server Setup successful...')
            return const.SUCCESS # success
        else : 
            print(f'Mysql Setup FAILED  : Exiting......')
            return const.FAILED if utils.is_continue() else exit()  # FAILED 
    else  :   # unknown error Setup FAILED 
        print('Unknown Error occurred \n configuration unsuccessful .....')
        return const.FAILED

   
# for testing purpose only  

if __name__ == "__main__" :
    
    print('Script Testing Started.... ')

    # NOTE password is required 
    # no password known needed sudo to set it 
    set_sudo_pass() # setting password 
    apache_config() 
    mysql_config()  







    
            




    







    
            



