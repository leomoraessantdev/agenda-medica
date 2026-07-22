"""Decorators de controle de acesso baseado em sessao."""
from functools import wraps

from flask import flash, redirect, session, url_for

from app import messages


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash(messages.LOGIN_NECESSARIO, "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapper
