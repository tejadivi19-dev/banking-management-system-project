import random
from functools import wraps

from flask import session, redirect, url_for, flash

from models import Account


def generate_account_number():
    """Generate a unique 6-digit account number."""
    while True:
        acc_no = str(random.randint(100000, 999999))
        if not Account.query.filter_by(account_number=acc_no).first():
            return acc_no


def login_required(view_func):
    """Redirect to login if there's no active session."""
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "account_number" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped_view


def current_account():
    """Return the Account object for the logged-in user, or None."""
    acc_no = session.get("account_number")
    if not acc_no:
        return None
    return Account.query.filter_by(account_number=acc_no).first()
