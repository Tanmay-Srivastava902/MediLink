''' This Module Contains the Functions For Setting Up the System For Convinience'''
# getting modules 
from file_handdler import pwd_handdler
from app_utils import gtpass , MAX_ATTEMPTS , NEEDS_INSTALL , SUCCESS , FAILED , is_continue  , SERVICE_TO_PACKAGE
from subprocess import run
# NOTE fix max attempts as soon as posible 
def update_pwd():
    # getting sudo password 
        try : 
            # password found
            sudo_pwd = pwd_handdler('load','sudo')
            print(sudo_pwd)
            
        # either file is missing/currupted  or password for sudo user is not in file
        except RuntimeError as e :
            
            print(e)
            
            print("No password found for sudo user. Password is being updated.")

            # setting sudo password
            for attempt in range(MAX_ATTEMPTS):

                print(f"Attempts Left {MAX_ATTEMPTS-attempt}")
                pwd = gtpass('sudo','system',1)

                res = run(
                            ['sudo' , '-S' , 'su'],  # -s sends one time input  to shell and closes the pipe immediately 
                            input=pwd + '\n',  # sending input to the terminal 
                            capture_output=True,   # to avoid terminal interruption
                            text=True # dechipher the output into stderr and stdout
                        )
                
                # checking for res 
                if res.returncode == 0 : # cmd success

                    print('Password verified: Saving password for future use')
                    
                    try:
                        # saving sudo pwd
                        pwd_handdler('update','sudo',pwd=pwd)
                    except RuntimeError as e : 
                        print(f"Password could not be saved. You may need to re-enter it when needed: {e}")
                    finally : 
                        return pwd  # returning Password 
                    
                elif res.returncode == 1  : # auth error 
                    print("Wrong sudo password entered. Please retry.")
                    continue # retrying 
                else : 
                    raise RuntimeError(f"Sorry Could Not Update Password : {res.stderr}")

                  
            # attempts exceeded (only reached if loop completes without success)
            print('Sorry, no attempts left. Exiting...')
            raise RuntimeError("Sorry No Attempts Left")
        

def execute_cmd(cmd:list[str],sudo_access:bool=False):
    '''
    Executes The Command And Returns 
    [**sudo access is set to false by default**]

    Args:
        Cmd: list['arg1','arg2'] command to be executed
        sudo_access: false if normally command is to be run and true if command requires sudo access
    Returns:
        CompletedProcess[str] : an object containing res of the command Executed
    Exceptions:
        RuntimeError : if any error occured
    '''
    # if root access is denied 
    if sudo_access is  False :
        res  = run(
                    cmd,
                    capture_output=True,
                    text=True
                    )
        
        return res
    # if sudo access is required
    else : 

        # getting sudo password 
        for attempt in range(MAX_ATTEMPTS):
            print(f"Attempts Left {MAX_ATTEMPTS-attempt}")

            # loading pwd from file
            try : 
                sudo_pwd = pwd_handdler('load','sudo')
            except RuntimeError as e: 
                print(f"No Saved Password Found For 'sudo' ")
                sudo_pwd = input("Enter 'sudo' password : ")


            # executing command 
            res  = run(
                                ['sudo' ,'-S'] + cmd ,  # adding sudo to the command 
                                input=sudo_pwd + '\n', # sending password 
                                capture_output=True,
                                text=True
                        )
            # checking returncode 
            if res.returncode == 0: # command executed successfully
                # saving sudo password 
                try :
                    pwd_handdler('update','sudo',sudo_pwd) 
                    print("Password is saved for future sudo operations.")
                except RuntimeError :
                    print("Password is not saved for sudo! You may need to re-enter it in future again.")
                finally: 
                    return res  # sending res out 
            elif res.returncode == 1: # command failed to execute
                print(f'Sorry, wrong password. Please try again.')
                continue
                # sent to retry
            else : 
                # we do not know the error 
                raise RuntimeError(f"Unknown Error Occured : {res.stderr}")
            
        raise RuntimeError("Could Not Execute Command Max Attempt Reached ")   
     

def service_manager(service :str, operation : str) -> int: 

    ''' 
    Manages System Services

    Args:
        Service : apache2 / mysql
        Operation : start /stop / status


    # '''
    # if status has requested  does not require sudo access
    if operation == 'status' : 

        print(f'Getting {service} status ... ')

        res = execute_cmd(['systemctl','status',service])

        # sending status 
        if res.returncode == 0 : 
            print(f'{service} is Running Properly')
            return SUCCESS  # started 
        elif res.returncode  == 3 : # service is not running
            print(f'{service} has Stopped' )
            return FAILED 
        else :  # service install required 
            print(f'{service} service is not installed ')
            return NEEDS_INSTALL 
        

    elif operation in ['start','stop','restart'] :
        # require sudo access
        res = execute_cmd(['systemctl',operation , service] , sudo_access=True)

        if res.returncode == 0 : 
            print(f'{service} {operation}ed successfully..')
            return SUCCESS
        elif res.returncode == 5:
            print(f' {service} Not Found ! Installing Package For {service}...')

            # installing service 
            try :
                # getting package for service
                package = SERVICE_TO_PACKAGE[service] 
                package_installer('system',package)
                # package installed 
                return service_manager(service,operation) # again sending to get perform the operation given 
               
            except KeyError as e : 
                raise RuntimeError(f'No Suitable Package Found For Service {service} Concider Installing Package First')

        else:
            raise RuntimeError(f'{service} Could Not Be {operation}ed : {res.stderr}')
        
    else : 
            raise RuntimeError(f'Unknown Operation Requested')

 

# for installation of service
def package_installer(package_type :str, package : str) -> None :
    '''
    Installs Packages Returns None when success Raises RuntimeError Otherwise

    Args:
        Package_type : system / python 
        package : name of package want to install

    '''
    # type :  package mysql-connector-python
    
    # asking user before installation
    print(f'Package installer is trying to install {package_type} package "{package}"')
    if is_continue() == False:
        raise RuntimeError('User denied! Package could not be installed.')
    
    # installing system package
    if package_type == 'system' :
        
        execute_cmd(['apt','update'] , sudo_access=True) # update packages 
        res = execute_cmd(['apt','install','-y',package],sudo_access=True)

        if res.returncode == 0 :
            print(f'{package} Installed Successfully')
            return None 
        else : 
              raise RuntimeError(f'Could Not Install Package  : \n{res.stderr}')
    
    # installing python package
    elif package_type == 'python':

        res  = execute_cmd(['python3','-m','pip','install', package])
        
        if res.returncode == 0 : 
            # pip is installed 
            print(f'{package} Installed Successfully')
            return None

        elif res.returncode != 0 and 'no module named pip' in res.stderr : 
            print('pip not found')
            try : 
                # installing pip
                package_installer('system','python3-pip') # calling itself to install pip
                # pip installed
                return package_installer('python',package) # calling itsef to install package and send results out 
            except RuntimeError as e : 
                raise RuntimeError(f'{package} Could Not Be Installed : {e}')
        else : 
           raise RuntimeError(f'{package} Could Not Be Installed : {res.stderr}')
    else: 
        raise RuntimeError(f'Unknown Package Type {package_type} Provided')


def configure_server(server:str) :
    '''
    Configures Provided Server Returns int 1 if confiured otherwise raise RuntimeError
    
    Args: 
        server :[apache2/mysql] name of the server to configure 
    '''
    try : 
        status  = service_manager( server , 'status')  # getting the result of the command
        # status found 
        if status == 1 : 
            print(f'{server} Server Setup successful...')
            return SUCCESS 
        elif status == 0 :
            # server is stopped 
            service_manager(server,'start')
            # service started 
            print('Apache Server Setup successful...')
            return SUCCESS 
        else : 
            # needs install 
            print(f'Server  Not Found ! Installing {server} server')

            # installing server 
            package_installer('system',server)
            # package installed 
            print(f'{server} Server Setup successful...')
            return SUCCESS 
        
    except RuntimeError as e :
        raise RuntimeError(f'{server} server Setup Failed ! {e}')
    

if __name__ == "__main__":
    # try :
    #     res = execute_cmd(['systemctl','status','mysql'])
    #     print('return code :',res.returncode,'\noutput is : ' ,res.stdout,'\nerror is :' , res.stderr)
    # except RuntimeError as e :
    #     print('exception is e ')