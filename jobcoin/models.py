from dataclasses import dataclass
from datetime import datetime
from typing import List

from jobcoin import db


class Account(db.Model):

    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deposit_address = db.Column(db.String(64), nullable=False)
    withdrawal_addresses = db.Column(db.ARRAY(db.String(64)), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    withdrawal_amount = db.Column(db.Float, nullable=False)
    withdrawal_addresses_index = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        deposit_address,
        withdrawal_addresses,
        total_amount,
        withdrawal_amount,
        withdrawal_addresses_index,
        *args,
        **kwargs
    ):
        self.deposit_address = deposit_address
        self.withdrawal_addresses = withdrawal_addresses
        self.total_amount = total_amount
        self.withdrawal_amount = withdrawal_amount
        self.withdrawal_addresses_index = withdrawal_addresses_index
