from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from extensions import db
from models import Account, Transaction
from helpers import generate_account_number, login_required, current_account


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


def register_routes(app):

    @app.route("/")
    def index():
        return render_template("index.html")

    
    # ACCOUNT CREATION
   
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name", "").strip().title()
            phone = request.form.get("phone", "").strip()
            pin = request.form.get("pin", "").strip()
            confirm_pin = request.form.get("confirm_pin", "").strip()

            if not name:
                flash("Name is required.", "danger")
            elif not (phone.isdigit() and len(phone) == 10):
                flash("Enter a valid 10-digit phone number.", "danger")
            elif not (pin.isdigit() and len(pin) == 4):
                flash("PIN must be exactly 4 digits.", "danger")
            elif pin != confirm_pin:
                flash("PINs do not match.", "danger")
            else:
                acc_no = generate_account_number()
                account = Account(
                    account_number=acc_no,
                    name=name,
                    phone=phone,
                    pin_hash=generate_password_hash(pin),
                    balance=0.0,
                )
                db.session.add(account)
                db.session.commit()

                db.session.add(Transaction(
                    account_id=account.id, type="account_created",
                    amount=0, balance_after=0, description="Account created",
                ))
                db.session.commit()

                flash(f"Account created! Your account number is {acc_no} — save it, you'll need it to log in.", "success")
                return redirect(url_for("login"))

        return render_template("register.html")

    
    # LOGIN / LOGOUT
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            acc_no = request.form.get("account_number", "").strip()
            pin = request.form.get("pin", "").strip()

            account = Account.query.filter_by(account_number=acc_no).first()
            if account and check_password_hash(account.pin_hash, pin):
                session["account_number"] = account.account_number
                flash(f"Welcome back, {account.name}!", "success")
                return redirect(url_for("dashboard"))

            flash("Invalid account number or PIN.", "danger")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("index"))

    
    # DASHBOARD
    
    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", account=current_account())

   
    # DEPOSIT
    
    @app.route("/deposit", methods=["GET", "POST"])
    @login_required
    def deposit():
        account = current_account()
        if request.method == "POST":
            try:
                amount = float(request.form.get("amount", 0))
                if amount <= 0:
                    raise ValueError
            except ValueError:
                flash("Enter a valid positive amount.", "danger")
                return render_template("deposit.html", account=account)

            account.balance += amount
            db.session.add(Transaction(
                account_id=account.id, type="deposit", amount=amount,
                balance_after=account.balance, description=f"Deposited Rs. {amount:.2f}",
            ))
            db.session.commit()
            flash(f"Rs. {amount:.2f} deposited successfully.", "success")
            return redirect(url_for("dashboard"))

        return render_template("deposit.html", account=account)

   
    # WITHDRAW
   
    @app.route("/withdraw", methods=["GET", "POST"])
    @login_required
    def withdraw():
        account = current_account()
        if request.method == "POST":
            try:
                amount = float(request.form.get("amount", 0))
                if amount <= 0:
                    raise ValueError
            except ValueError:
                flash("Enter a valid positive amount.", "danger")
                return render_template("withdraw.html", account=account)

            if amount > account.balance:
                flash("Insufficient balance.", "danger")
                return render_template("withdraw.html", account=account)

            account.balance -= amount
            db.session.add(Transaction(
                account_id=account.id, type="withdraw", amount=amount,
                balance_after=account.balance, description=f"Withdrew Rs. {amount:.2f}",
            ))
            db.session.commit()
            flash(f"Rs. {amount:.2f} withdrawn successfully.", "success")
            return redirect(url_for("dashboard"))

        return render_template("withdraw.html", account=account)

    
    # TRANSFER
    
    @app.route("/transfer", methods=["GET", "POST"])
    @login_required
    def transfer():
        account = current_account()
        if request.method == "POST":
            receiver_no = request.form.get("receiver_account", "").strip()
            try:
                amount = float(request.form.get("amount", 0))
                if amount <= 0:
                    raise ValueError
            except ValueError:
                flash("Enter a valid positive amount.", "danger")
                return render_template("transfer.html", account=account)

            if receiver_no == account.account_number:
                flash("You cannot transfer to your own account.", "danger")
                return render_template("transfer.html", account=account)

            receiver = Account.query.filter_by(account_number=receiver_no).first()
            if not receiver:
                flash("Receiver account does not exist.", "danger")
            elif amount > account.balance:
                flash("Insufficient balance.", "danger")
            else:
                account.balance -= amount
                receiver.balance += amount

                db.session.add(Transaction(
                    account_id=account.id, type="transfer_out", amount=amount,
                    balance_after=account.balance,
                    description=f"Transferred Rs. {amount:.2f} to A/C {receiver.account_number}",
                ))
                db.session.add(Transaction(
                    account_id=receiver.id, type="transfer_in", amount=amount,
                    balance_after=receiver.balance,
                    description=f"Received Rs. {amount:.2f} from A/C {account.account_number}",
                ))
                db.session.commit()
                flash(f"Rs. {amount:.2f} transferred to account {receiver_no}.", "success")
                return redirect(url_for("dashboard"))

        return render_template("transfer.html", account=account)

    
    # TRANSACTION HISTORY
    
    @app.route("/history")
    @login_required
    def history():
        account = current_account()
        transactions = account.transactions.all()
        return render_template("history.html", account=account, transactions=transactions)

    
    # CHANGE PIN
    
    @app.route("/change-pin", methods=["GET", "POST"])
    @login_required
    def change_pin():
        account = current_account()
        if request.method == "POST":
            old_pin = request.form.get("old_pin", "").strip()
            new_pin = request.form.get("new_pin", "").strip()
            confirm_pin = request.form.get("confirm_pin", "").strip()

            if not check_password_hash(account.pin_hash, old_pin):
                flash("Old PIN is incorrect.", "danger")
            elif not (new_pin.isdigit() and len(new_pin) == 4):
                flash("New PIN must be exactly 4 digits.", "danger")
            elif new_pin != confirm_pin:
                flash("New PINs do not match.", "danger")
            else:
                account.pin_hash = generate_password_hash(new_pin)
                db.session.add(Transaction(
                    account_id=account.id, type="pin_change", amount=0,
                    balance_after=account.balance, description="PIN changed",
                ))
                db.session.commit()
                flash("PIN changed successfully.", "success")
                return redirect(url_for("dashboard"))

        return render_template("change_pin.html")


app = create_app()

if __name__ == "__main__":
    app.run()
