from .db import check_permission, USER_PERMS
import utils.str_consts as sconst
import flask_login

MANAGER_PERM = {
    "document": {
        USER_PERMS.ADM: ["REMOVE_PERMANENT", "CHANGE_EDIT_PERM"],
        USER_PERMS.OPR: ["CHANGE_EDIT_PERM"],
        USER_PERMS.USR: [],
        USER_PERMS.SUS: [],
        USER_PERMS.ANN: []
    },
    "user": {
        USER_PERMS.ADM: ["SUSPEND", "DELETE"],
        USER_PERMS.OPR: ["SUSPEND"],
        USER_PERMS.USR: [],
        USER_PERMS.SUS: [],
        USER_PERMS.ANN: []
    }
}

def get_permission_list(current_user, perm_target):
        manager_perms = [USER_PERMS.ADM, USER_PERMS.OPR]

        return dict (
            status=sconst.SUCCESS, 
            content=\
                dict (
                    is_operator=(current_user.user_type in manager_perms), 
                    perm_list=current_user.get_user_permission(perm_target),
                    managable_perms=[i for i in USER_PERMS.PERM_LIST 
                    if USER_PERMS.get_ord(i) < USER_PERMS.get_ord(current_user.user_type)]
                )
            )


def check_document_perm(user, readonly=False):
    def deco(func):
        def wrapper(*args, **kargs):
            title = args[0].replace("image::", "")

            if (isinstance(user,flask_login.AnonymousUserMixin)):
                if (readonly and check_permission(title, USER_PERMS.ANN)):
                    return func(*args, **kargs)
                else:
                    return dict(status=sconst.LOGIN_REQUIRED, content=sconst.LOGIN_REQUIRED)

            else:

                if check_permission(title, user.user_type):
                    return func(*args, **kargs)
                
                else:
                    return dict(status=sconst.NO_PERMISSION)
            
        return wrapper

    return deco


def check_perm(user, perm_target, using_perm, managed_user_type=None):
    '''
    user: current_user 객체
    perm_target: 'document' || 'user'
    managed_perm : 조작되는 perm
    '''
    perm_list = get_permission_list(user, perm_target)
    perm_names = perm_list["content"]["perm_list"]
    managable_types = perm_list["content"]["managable_perms"]

    if (managed_user_type is not None):
        return (using_perm in perm_names and managed_user_type in managable_types)
    
    else:
        return (using_perm in perm_names)

