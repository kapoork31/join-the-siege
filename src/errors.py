class FileExtensionNotSupported(Exception):
    def __init__(self, msg, status_code=400):
        self.status_code = status_code
