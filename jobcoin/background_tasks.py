import time
import datetime
from jobcoin.constants import (
    GET_NEW_DEPOSITS_TASK_INTERVAL_SEC,
    DISTRIBUTE_DEPOSITS_TASK_INTERVAL_SEC,
)

from jobcoin.jobcoin_mixer import jobcoin_mixer


def get_new_deposits():
    global jobcoin_mixer
    while True:
        offset = datetime.datetime.utcnow() - datetime.timedelta(
            seconds=GET_NEW_DEPOSITS_TASK_INTERVAL_SEC
        )
        jobcoin_mixer.get_new_deposits(offset)
        time.sleep(GET_NEW_DEPOSITS_TASK_INTERVAL_SEC)


def distribute_deposits():
    global jobcoin_mixer
    while True:
        jobcoin_mixer.distribute_deposits()
        time.sleep(DISTRIBUTE_DEPOSITS_TASK_INTERVAL_SEC)
