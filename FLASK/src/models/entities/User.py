from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class User(UserMixin):
    
    def __init__(self, id, username, password, fullname, email, is_admin=False) -> None:
        self.id = id
        self.username = username 
        self.password = password
        self.fullname = fullname
        self.email = email
        self.is_admin = is_admin
    
    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)
    
    @classmethod
    def hash_pass(self, password):
        passwordHash = generate_password_hash(password)
        return passwordHash
        
