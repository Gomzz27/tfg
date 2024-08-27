class ModelArticulo():

    @classmethod
    def buscar_articulos(cls, db, query):
        try:
            cr = db.connection.cursor()
            sql = "SELECT idArticulo, titulo, contenido, resumen FROM articulos WHERE titulo LIKE %s OR contenido LIKE %s"
            cr.execute(sql, ('%' + query + '%', '%' + query + '%'))
            rows = cr.fetchall()
            cr.close()
            return rows
        except Exception as ex:
            print(f"Error durante la búsqueda de artículos: {str(ex)}")
            return []    
        
    @classmethod
    def obtener_por_id(cls, db, articulo_id):
        try:
            cr = db.connection.cursor()
            sql = "SELECT idArticulo, titulo, contenido, resumen FROM articulos WHERE idArticulo = %s"
            cr.execute(sql, (articulo_id,))
            row = cr.fetchone()
            cr.close()
            if row:
                return row
        except Exception as ex:
            print(f"Error durante la obtención del artículo: {str(ex)}")
        return None
    
    @classmethod
    def crear_articulo(cls, db, titulo, contenido, resumen):
        try:
            cr = db.connection.cursor()
            sql = "INSERT INTO articulos (titulo, contenido, resumen) VALUES (%s, %s, %s)"
            cr.execute(sql, (titulo, contenido, resumen))
            db.connection.commit()
            cr.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            print(f"Error durante la creación del artículo: {str(ex)}")
            return False
    
    @classmethod
    def actualizar_articulo(cls, db, articulo_id, titulo, contenido, resumen):
        try:
            cr = db.connection.cursor()
            sql = "UPDATE articulos SET titulo = %s, contenido = %s, resumen = %s WHERE idArticulo = %s"
            cr.execute(sql, (titulo, contenido, resumen, articulo_id))
            db.connection.commit()
            cr.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            print(f"Error durante la actualización del artículo: {str(ex)}")
            return False
    
    @classmethod
    def eliminar_articulo(cls, db, articulo_id):
        try:
            cr = db.connection.cursor()
            sql = "DELETE FROM articulos WHERE idArticulo = %s"
            cr.execute(sql, (articulo_id,))
            db.connection.commit()
            cr.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            print(f"Error durante la eliminación del artículo: {str(ex)}")
            return False   
    
