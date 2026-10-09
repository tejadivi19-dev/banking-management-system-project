from datetime import datetime

from extensions import db


class Account(db.Model):
    """A bank account belonging to one customer."""

    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(6), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    pin_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, default=0.0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship(
        "Transaction",
        backref="account",
        lazy="dynamic",
        order_by="desc(Transaction.timestamp)",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Account {self.account_number} - {self.name}>"


class Transaction(db.Model):
    """A single ledger entry: deposit, withdrawal, transfer, etc."""

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.type} {self.amount} on {self.account_id}>"
