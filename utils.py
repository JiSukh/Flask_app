from flask import abort
from flask_login import current_user
from functools import wraps
from cryptography.fernet import Fernet
from hashlib import scrypt
import base64
import os

def roles_required(*roles):
    def inner_decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not hasattr(current_user, 'role'):
                abort(401)
            elif current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return inner_decorator

def get_last_n_lines(file_path, n=10):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            return lines[-n:]  
    else:
        return []

class Sym_Encryption:
    def __init__(self, user):
        
        self.privateKey = scrypt(password= user.password.encode(), salt=user.salt.encode(),n=2048,r=8,p=1,dklen=32)
        self.cipher = Fernet(base64.b64encode(self.privateKey))



    def encrypt(self,str):

        str_bs = str.encode()
        return self.cipher.encrypt(str_bs)
    
    def decrypt(self, str):

        str_bs = self.cipher.decrypt(str)
        return str_bs.decode()

    @staticmethod
    def decrypt_post(post):
        f_cipher = Sym_Encryption(post.user)
        post.title = f_cipher.decrypt(post.title)
        post.body = f_cipher.decrypt(post.body)
        
        return post
    @staticmethod
    def encrypt_post(author_user, post):
        f_cipher = Sym_Encryption(author_user)
        post.title = f_cipher.encrypt(post.title)
        post.body = f_cipher.encrypt(post.body)

        return post
    @staticmethod
    def encrypt_text(author_user, text):
        f_cipher = Sym_Encryption(author_user)

        return f_cipher.encrypt(text)

    @staticmethod
    def decrypt_all_posts(posts):
        newposts = posts
        for i, post in enumerate(posts):
            newposts[i] = Sym_Encryption.decrypt_post(post)


        return newposts

