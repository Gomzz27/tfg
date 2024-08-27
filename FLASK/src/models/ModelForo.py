from .entities.Post import Post

class ModelForo():
        
    @classmethod
    def publicar(self, db, post):
        try:
            cr= db.connection.cursor()
            sql = "INSERT INTO posts (id, titulo, contenido, autor, fecha) VALUES ('{}','{}','{}','{}','{}')".format(post.id, post.titulo, post.contenido, post.autor, post.fecha)
            cr.execute(sql)
            db.connection.commit()
            cr.close()
            return True

        except Exception as ex:
            db.connection.rollback()
            print(f"Error during publicar: {str(ex)}")
            raise Exception(ex)
            return False
        
    @classmethod
    def obtener_todas(cls, db):
        try:
            cr = db.connection.cursor()
            sql = "SELECT id, titulo, autor FROM posts"
            cr.execute(sql)
            rows = cr.fetchall()
            print(rows)
            cr.close()
            return rows
        except Exception as ex:
            print(f"Error during obtener_todas: {str(ex)}")
            return []
        
    @classmethod
    def buscar_publicaciones(cls, db, query):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, titulo, autor FROM posts WHERE titulo LIKE %s OR contenido LIKE %s"
            like_query = f"%{query}%"
            cursor.execute(sql, (like_query, like_query))
            publicaciones = cursor.fetchall()
            return publicaciones
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def obtener_misPosts(cls, db, username):
        try:
            cr = db.connection.cursor()
            sql = "SELECT id, titulo, fecha FROM posts where autor = %s"
            cr.execute(sql, (username,))
            rows = cr.fetchall()
            print(rows)
            cr.close()
            return rows
        except Exception as ex:
            print(f"Error during obtener_todas: {str(ex)}")
            return []
        
    @classmethod
    def obtener_por_id(cls, db, post_id):
        try:
            cr = db.connection.cursor()
            sql = "SELECT id, titulo, contenido, autor, fecha FROM posts WHERE id = %s"
            cr.execute(sql, (post_id,))
            row = cr.fetchone()
            cr.close()
            return row
        except Exception as ex:
            print(f"Error during obtener_por_id: {str(ex)}")
            return None
        
    @classmethod
    def obtener_post_by_idResp(cls, db, idResp):
        try:
            print('entra' )
            print( idResp)
            cr = db.connection.cursor()
            sql = "SELECT post_id FROM respuestas WHERE idResp = %s"
            cr.execute(sql, (idResp,))
            row = cr.fetchone()
            print(row)
            cr.close()
            return row
        except Exception as ex:
            print(f"Error during obtener_por_id: {str(ex)}")
            return None




    @classmethod
    def add_respuesta(cls, db, resp):
        try:
            cr = db.connection.cursor()
            sql = "INSERT INTO respuestas (idResp, post_id, contenido, autor, fecha) VALUES ('{}','{}','{}','{}','{}')".format(resp.idResp, resp.post_id, resp.contenido, resp.autor, resp.fecha)
            cr.execute(sql)
            db.connection.commit()
            resp.idResp = cr.lastrowid
            cr.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            print(f"Error during add_respuesta: {str(ex)}")
            return False

    @classmethod
    def obtener_respuestas(cls, db, post_id):
        try:
            cr = db.connection.cursor()
            sql = "SELECT contenido, autor, fecha, idResp FROM respuestas WHERE post_id = '{}' order by fecha desc".format(post_id)
            cr.execute(sql)
            rows = cr.fetchall()
            print(rows)
            cr.close()
            return rows
        except Exception as ex:
            print(f"Error during obtener_respuestas: {str(ex)}")
            return []   
        
    @classmethod
    def add_notificacion(cls, db, noti):
        try:
            cr = db.connection.cursor()
            sql = "INSERT INTO notificaciones (idNotify, idResp, autor, leida) VALUES ('{}','{}','{}','{}')".format(noti.idNotify, noti.idResp, noti.autor, noti.leida)
            cr.execute(sql)
            db.connection.commit()
            cr.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            print(f"Error during add_notificacion: {str(ex)}")
            return False

    @classmethod
    def eliminarPost(cls, db, post_id):
        try:
            cursor = db.connection.cursor()
            sql = "DELETE FROM posts WHERE id = {}".format(post_id)
            cursor.execute(sql)
            db.connection.commit()
            return True
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def eliminarResp(cls, db, idResp):
        try:
            cursor = db.connection.cursor()
            sql = "DELETE FROM respuestas WHERE idResp = %s"
            cursor.execute(sql, (idResp,))
            db.connection.commit()
            return True
        except Exception as ex:
            raise Exception(ex)
        

#Apartado de notificaciones del foro
    @classmethod
    def obtener_notificaciones(cls, db, autor):
        try:
            cr = db.connection.cursor()
            sql = "SELECT * FROM notificaciones WHERE autor = %s"
            cr.execute(sql, (autor,))
            notificaciones = cr.fetchall()
            cr.close()
            return notificaciones
        except Exception as ex:
            print(f"Error during obtener_notificaciones: {str(ex)}")
            return []

    @classmethod
    def obtener_notificacion(cls, db, notificacion_id):
        try:
            cr = db.connection.cursor()
            sql = "SELECT * FROM notificaciones WHERE idNotify = %s"
            cr.execute(sql, (notificacion_id,))
            notificacion = cr.fetchone()
            cr.close()
            return notificacion
        except Exception as ex:
            print(f"Error during obtener_notificacion: {str(ex)}")
            return None
        
    @classmethod
    def obtener_notificaciones_no_leidas(cls, db, username):
        try: 
            cr = db.connection.cursor()
            sql = "SELECT COUNT(*) FROM notificaciones WHERE autor = %s AND leida = %s"
            cr.execute(sql, (username, 0))
            count = cr.fetchone()[0]
            cr.close()
            return count
        except Exception as ex:
            print(f"Error during obtener_notificaciones_no_leidas: {str(ex)}")
            return []

    @classmethod
    def actualizar_notificacion(cls, db, notificacion):
        try:
            cr = db.connection.cursor()
            sql = "UPDATE notificaciones SET leida = %s WHERE idNotify = %s"
            cr.execute(sql, (1, notificacion))
            db.connection.commit()
            cr.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            print(f"Error during actualizar_notificacion: {str(ex)}")
            return False
    
    @staticmethod
    def eliminar_notificaciones_por_usuario(db, username):
        cursor = db.connection.cursor()
        cursor.execute("DELETE FROM notificaciones WHERE autor = %s", (username,))
        db.connection.commit()