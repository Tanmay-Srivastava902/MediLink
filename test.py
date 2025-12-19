import pickle

d = {"tanmay": "SecurePass@1201" , "root": "SecurePass@1201" , "medilink_admin":"medilink@1201"}
with open('pwd.dat','wb') as f :
    pickle.dump(d,f)