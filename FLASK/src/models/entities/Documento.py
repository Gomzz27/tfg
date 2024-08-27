class Documento:
    def __init__(self, id, user_id, filename, file_path, upload_date, documento_hash):
        self.id = id
        self.user_id = user_id
        self.filename = filename
        self.file_path = file_path
        self.upload_date = upload_date
        self.documento_hash = documento_hash
