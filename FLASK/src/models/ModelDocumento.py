from .entities.Documento import Documento

class ModelDocumento:

    @classmethod
    def guardar_documento(cls, db, user_id, filename, file_path, documento_hash):
        try:
            cursor = db.connection.cursor()
            sql = """INSERT INTO documentos (user_id, filename, file_path, documento_hash) 
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (user_id, filename, file_path, documento_hash))
            db.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            print(f"Error durante el guardado del documento: {str(ex)}")
            return False

    @classmethod
    def obtener_documentos(cls, db, user_id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, user_id, filename, file_path, upload_date, documento_hash FROM documentos WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()
            documentos = [Documento(row[0], row[1], row[2], row[3], row[4], row[5]) for row in rows]
            cursor.close()
            return documentos
        except Exception as ex:
            print(f"Error al obtener documentos: {str(ex)}")
            return []