import os
from utils.funcs import get_doc_list
import utils.str_consts as sconst
import traceback
from PIL import Image
from .perms import check_document_perm
from flask_login import current_user


ALLOWED_FILES = {"png", "jpg", 'gif', 'jpeg', 'webp'}
# images 경로 있는지 확인
IMG_PATH_LIST = [".", "assets", "images"]
if (IMG_PATH_LIST[2] not in get_doc_list(IMG_PATH_LIST[1])):
    os.mkdir("/".join(IMG_PATH_LIST))


def _check_allowed(filename):
    return ('.' in filename and
            filename.split('.')[-1].lower() in ALLOWED_FILES)

def _convert_imagename(name):
    return name.replace("image::", "") + ".jpg"

@check_document_perm(current_user)
def add(image_name: str, image):
    image_name = _convert_imagename(image_name)

    if image.filename == ".jpg":
        return dict(status=sconst.NO_SELECTED_FILE)
    
    # 이미 이미자가 존재하는지 확인
    if (image_name in get_doc_list("/".join(IMG_PATH_LIST))):
        return dict(status=sconst.DOC_ALREADY_EXISTS)

    try:
        if image and _check_allowed(image.filename):
            img = Image.open(image)

            # RGB로 변환(투명한 이미지일 경우 문제가 생길 수 있어서..)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            filename = image_name
            filepath = os.path.join(*IMG_PATH_LIST, filename)
            # image.save(os.path.join(*IMG_PATH_LIST, filename))
            img.save(filepath, format="JPEG")
            return dict(status=sconst.SUCCESS)
        
    except Exception as err:
        traceback.print_exc()
        return dict(status=sconst.UNKNOWN_ERROR)
    
    return dict(status=sconst.NOT_ALLOWED_FILE)

def get(image_name:str):
    image_name = _convert_imagename(image_name)

    if image_name not in get_doc_list("/".join(IMG_PATH_LIST)):
        return dict(status=sconst.DOC_NOT_EXIST)
    
    return dict(status=sconst.SUCCESS, content="/".join(IMG_PATH_LIST + [image_name]))

@check_document_perm(current_user)
def delete(image_name:str):
    image_name = _convert_imagename(image_name)

    if (image_name not in get_doc_list("/".join(IMG_PATH_LIST))):
        return dict(status=sconst.DOC_NOT_EXIST)
    
    try:
        os.remove(os.path.join(*IMG_PATH_LIST, image_name))
        return dict(status=sconst.SUCCESS)
    except Exception as err:
        traceback.print_exc()
        return dict(status=sconst.UNKNOWN_ERROR)

