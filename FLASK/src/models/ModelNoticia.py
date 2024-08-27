from .entities.Noticia import Noticia

class ModelNoticia():

    @classmethod
    def obtener_todas(cls, db):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, titulo, contenido,  fecha, link FROM noticias"
            cursor.execute(sql)
            data = cursor.fetchall()
            return data
        except Exception as ex:
            raise Exception(ex)
    
    @classmethod
    def obtener_por_id(cls, db, noticia_id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, titulo, contenido, fecha, link FROM noticias WHERE id = {}".format(noticia_id)
            cursor.execute(sql)
            data = cursor.fetchone()
            if data:
                noticia = Noticia(data[0], data[1], data[2], data[3], data[4])
                return noticia
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def crear(cls, db, noticia):
        try:
            cursor = db.connection.cursor()
            sql = """INSERT INTO noticias (id, titulo, contenido,  fecha, link) 
                     VALUES ('{}', '{}', '{}', '{}', '{}')""".format(noticia.id, noticia.titulo, noticia.contenido, noticia.fecha, noticia.link)
            cursor.execute(sql)
            db.connection.commit()
            return True
        except Exception as ex:
            raise Exception(ex)
    
    @classmethod
    def actualizar(cls, db, noticia):
        try:
            cursor = db.connection.cursor()
            sql = """UPDATE noticias SET titulo = '{}', contenido = '{}', fecha = '{}', link = '{}' 
                     WHERE id = {}""".format(noticia.titulo, noticia.contenido, noticia.fecha, noticia.link, noticia.id)
            cursor.execute(sql)
            db.connection.commit()
            return True
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def eliminar(cls, db, noticia_id):
        try:
            cursor = db.connection.cursor()
            sql = "DELETE FROM noticias WHERE id = {}".format(noticia_id)
            cursor.execute(sql)
            db.connection.commit()
            return True
        except Exception as ex:
            raise Exception(ex)