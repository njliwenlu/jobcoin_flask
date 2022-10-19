from dataclasses import dataclass
from tokenize import Double
from typing import List

from jobcoin.constants import WITHDRAWAL_INCREMENT


@dataclass
class Account:
    deposit_address: str
    withdrawal_addresses: List[str]
    total_amount: float = 0
    withdrawal_amount: int = WITHDRAWAL_INCREMENT
    withdrawal_addresses_index: int = 0
