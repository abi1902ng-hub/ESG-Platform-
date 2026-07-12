"""
Role/permission-based access control decorators.
Usage:
    @role_required("org_admin", "super_admin")
    def view(): ...

    @permission_required("carbon.create")
    def create_carbon_entry(): ...
"""
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*role_names):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if not current_user.has_role(*role_names):
                flash("You do not have permission to access that page.", "danger")
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


def permission_required(*permission_codes):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if not any(current_user.has_permission(code) for code in permission_codes):
                flash("You do not have permission to perform that action.", "danger")
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


def active_account_required(view_func):
    """Blocks deactivated users even if their session is still valid."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated and not current_user.is_active:
            flash("Your account has been deactivated. Contact your administrator.", "danger")
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped
