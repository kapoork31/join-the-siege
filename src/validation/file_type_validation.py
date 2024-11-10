from src.settings import ALLOWED_EXTENSIONS
from src.errors import FileExtensionNotSupported

# Allowed file extensions
# this is a limiting factor
# should just extract the text and then classify
# any image based things we can bin and then need to extend that for a different solution
def allowed_file(filename: str) -> bool:
    if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        return True
    else:
        raise FileExtensionNotSupported("File type not supported")
