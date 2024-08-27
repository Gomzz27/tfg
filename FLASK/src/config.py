class Config:
    SECRET_KEY = 'Cl4v353cr3t4'

class DevelopmentConfig(Config):
    
    DEBUG =True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'ce_login'
  

config ={
    'development':DevelopmentConfig
}