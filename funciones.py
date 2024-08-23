# Funcion para redireccionar al registro si no hay alguno hecho 
from flask import *
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/registrarse")
        return f(*args, **kwargs)
    return decorated_function
    