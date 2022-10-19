import logging
from typing import Dict
import uuid
import datetime
import time

import requests

from jobcoin.account import Account
from jobcoin.constants import (
    API_ADDRESS_URL,
    API_TRANSACTIONS_URL,
    GET_NEW_DEPOSITS_TASK_INTERVAL_SEC,
    WITHDRAWAL_INCREMENT,
    HOUSE_ADDRESS,
)
from jobcoin.exceptions import (
    InvalidWithdrawalAddressException,
    WithdrawalAddressInUseException,
)
from jobcoin import db

logging.basicConfig(
    filename="/tmp/jobcoin-mixer",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class JobCoinMixer:
    def __init__(self) -> None:
        self.deposit_address_store: Dict[str, Account] = {}

    # def run(self):
    #     while True:
    #         offset = datetime.datetime.utcnow() - datetime.timedelta(
    #             seconds=GET_NEW_DEPOSITS_TASK_INTERVAL_SEC
    #         )
    #         self.get_new_deposits(offset)
    #         print("get_new_deposits", self.deposit_address_store)
    #         time.sleep(10)

    # def run2(self):
    #     while True:
    #         self.distribute_deposits()
    #         print("distribute_deposits", self.deposit_address_store)
    #         time.sleep(5)

    def get_new_deposit_address(self, withdrawal_addresses_str):
        withdrawal_addresses = self._convert_withdrawal_addresses_input(
            withdrawal_addresses_str
        )
        self._check_withdrawal_addresses_unused(withdrawal_addresses)

        new_address = "deposit_address_" + uuid.uuid4().hex
        self.deposit_address_store[new_address] = Account(
            deposit_address=new_address,
            withdrawal_addresses=withdrawal_addresses_str.split(","),
        )
        logging.info(
            f"New deposit address {new_address} for withdrawal addresses {withdrawal_addresses_str}"
        )
        # account = Account(
        #     deposit_address=new_address,
        #     withdrawal_addresses=withdrawal_addresses,
        #     total_amount=0,
        #     withdrawal_amount=WITHDRAWAL_INCREMENT,
        #     withdrawal_addresses_index=0,
        # )
        # db.session.add(account)
        # db.session.commit()
        return new_address

    def get_new_deposits(self, offset):
        for deposit_address in self.deposit_address_store.keys():
            transactions = requests.get(f"{API_ADDRESS_URL}/{deposit_address}").json()[
                "transactions"
            ]
            for transaction in transactions[::-1]:
                if self._should_process_transaction(
                    transaction, offset, deposit_address
                ):
                    self.transfer_to_house_address(
                        transaction["toAddress"], transaction["amount"]
                    )
                    self.deposit_address_store[
                        transaction["toAddress"]
                    ].total_amount += float(transaction["amount"])

    def distribute_deposits(self):
        for deposit_address, account in self.deposit_address_store.items():
            withdrawl_amount = (
                account.withdrawal_amount
                if account.withdrawal_amount < account.total_amount
                else account.total_amount
            )
            if not withdrawl_amount:
                logging.info(
                    f"0 balance for deposit address {deposit_address}, no distribution"
                )
                continue
            self.transfer_to_withdrawal_address(
                account.withdrawal_addresses[account.withdrawal_addresses_index],
                withdrawl_amount,
            )
            account.total_amount -= withdrawl_amount
            account.withdrawal_addresses_index = (
                account.withdrawal_addresses_index + 1
            ) % len(account.withdrawal_addresses)
            account.withdrawal_amount += WITHDRAWAL_INCREMENT

    def transfer_to_house_address(self, from_address, amount):
        self._send_jobcoins(from_address, HOUSE_ADDRESS, amount)
        logging.info(
            f"Transfered {amount} from {from_address} to house address {HOUSE_ADDRESS}"
        )

    def transfer_to_withdrawal_address(self, to_address, amount):
        self._send_jobcoins(HOUSE_ADDRESS, to_address, amount)
        logging.info(
            f"Transfered {amount} from house address {HOUSE_ADDRESS} to withdrawal address {to_address}"
        )

    def _send_jobcoins(self, from_address, to_address, amount):
        response = requests.post(
            API_TRANSACTIONS_URL,
            data={
                "fromAddress": from_address,
                "toAddress": to_address,
                "amount": amount,
            },
        )
        response.raise_for_status()

    def _should_process_transaction(self, transaction, offset, deposit_address):
        return (
            self._is_after_offset(transaction["timestamp"], offset)
            and transaction["toAddress"] == deposit_address
        )

    def _is_after_offset(self, timestamp, offset):
        transaction_time = datetime.datetime.strptime(
            timestamp, "%Y-%m-%dT%H:%M:%S.%f%z"
        ).replace(tzinfo=None)
        return transaction_time >= offset

    def _check_withdrawal_addresses_unused(self, withdrawal_addresses):
        addresses_in_use = []
        for address in withdrawal_addresses:
            address_info = requests.get(f"{API_ADDRESS_URL}/{address}").json()
            if address_info["balance"] != "0" or address_info["transactions"]:
                addresses_in_use.append(address)
        if addresses_in_use:
            addresses_in_use_str = ",".join(addresses_in_use)
            raise WithdrawalAddressInUseException(
                f"Following addressed are in use: {addresses_in_use_str}. Please provide only new and unused addresses."
            )

    def _convert_withdrawal_addresses_input(self, withdrawal_addresses_str):
        withdrawal_addresses = withdrawal_addresses_str.split(",")
        withdrawal_addresses = [address.strip() for address in withdrawal_addresses]
        withdrawal_addresses_non_empty = [
            address for address in withdrawal_addresses if address
        ]
        if withdrawal_addresses_non_empty != withdrawal_addresses:
            raise InvalidWithdrawalAddressException(
                "Empty addresses found, please provide comma-separate list of addresses"
            )
        return withdrawal_addresses


jobcoin_mixer = JobCoinMixer()
