from .entities.User import User

class ModelUser():
    
    @classmethod
    def login(self, db, user):
        try:
            cr= db.connection.cursor()
            sql = """SELECT id, username, password, fullname, email, is_admin FROM users 
            WHERE username = '{}'""".format(user.username)
            cr.execute(sql)
            row = cr.fetchone()
            if row != None:
                password_check = User.check_password(row[2], user.password)  # Cambia esto según tu lógica de negocio
                user = User(row[0], row[1], password_check, row[3], row[4], row[5])
                return user
            else: 
                return None

        except Exception as ex:
            print(f"Error during login: {str(ex)}")
            raise Exception(ex)
        
    
    
    @classmethod
    def register(self, db, user):
        try:
            cr = db.connection.cursor()
            # Verificar si el nombre de usuario ya existe
            sql_check = "SELECT COUNT(*) FROM users WHERE username = %s"
            cr.execute(sql_check, (user.username,))
            result = cr.fetchone()
            if result[0] > 0:
                raise Exception("El nombre de usuario ya existe.")
            
            sql = "INSERT INTO users (id, username, password, fullname, email, is_admin) VALUES ('{}','{}','{}','{}','{}', '{}' )".format(user.id, user.username, user.password, user.fullname, user.email, user.is_admin)
            cr.execute(sql)
            db.connection.commit()
            cr.close()

        except Exception as ex:
            db.connection.rollback()
            print(f"Error during register: {str(ex)}")
            raise Exception(ex)
                
        
    @classmethod
    def get_by_id(self, db, id):
        try:
            cr= db.connection.cursor()
            sql = """SELECT id, username, password, fullname, email, is_admin FROM users 
            WHERE id = '{}'""".format(id)
            cr.execute(sql)
            row = cr.fetchone()
            if row != None:
                logged_user = User(row[0], row[1], row[2], row[3], row[4],  row[5])
                return logged_user
            else: 
                return None

        except Exception as ex:
            print(f"Error during login: {str(ex)}")
            raise Exception(ex)
    
    @classmethod
    def obtener_todos(cls, db):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, username, fullname, email FROM users"
            cursor.execute(sql)
            data = cursor.fetchall()
            usuarios = []
            for row in data:
                usuario = User(row[0], row[1], None, row[2], row[3])
                usuarios.append(usuario)
            return usuarios
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def buscar_usuarios(cls, db, query):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, username, fullname, email FROM users WHERE username LIKE %s OR fullname LIKE %s OR email LIKE %s"
            like_query = f"%{query}%"
            cursor.execute(sql, (like_query, like_query, like_query))
            data = cursor.fetchall()
            usuarios = []
            for row in data:
                usuario = User(row[0], row[1], None, row[2], row[3])
                usuarios.append(usuario)
            return usuarios
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def eliminar(cls, db, user_id):
        try:
            cursor = db.connection.cursor()
            sql = "DELETE FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            db.connection.commit()
            return True
        except Exception as ex:
            raise Exception(ex)
        
  
    @classmethod
    def actualizar_user(cls, db, user):
        try:
            cr = db.connection.cursor()
            sql = """UPDATE users SET username = %s, fullname = %s, email = %s WHERE id = %s"""
            cr.execute(sql, (user.username, user.fullname, user.email, user.id))
            db.connection.commit()
            return True
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def cambiar_password(cls, db, user_id, new_password):
        try:
            cr = db.connection.cursor()
            hashed_password = User.hash_pass(new_password)
            sql = """UPDATE users SET password = %s WHERE id = %s"""
            cr.execute(sql, (hashed_password, user_id))
            db.connection.commit()
            return True
        except Exception as ex:
            raise Exception(ex)