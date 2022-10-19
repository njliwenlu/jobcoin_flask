import datetime
import requests
import json
from celery import group

from jobcoin import celery
import jobcoin
from jobcoin.constants import API_TRANSACTIONS_URL, GET_NEW_DEPOSITS_TASK_INTERVAL_SEC
from jobcoin.jobcoin_mixer import jobcoin_mixer
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery.task(
    name="get_new_deposits",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def get_new_deposits():
    # Make HTTP requests to the transactions API to get a list of all transactions.
    # Since the response has transactions sorted in increasing order of timestamp value
    # and this task runs periodically, therefore, we iterate from the end of the list,
    # check if there are transfers to deposit addresses,
    # and stop when timestamp is before last time this task was run.
    logger.info("Running periodic task get_new_deposits")
    offset = datetime.datetime.utcnow() - datetime.timedelta(
        seconds=GET_NEW_DEPOSITS_TASK_INTERVAL_SEC
    )
    jobcoin_mixer.get_new_deposits(offset)
    # logger.info(
    #     "Running periodic task get_new_deposits",
    #     json.dumps(jobcoin_mixer.deposit_address_store),
    # )


@celery.task(
    name="distribute_deposits",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def distribute_deposits():
    logger.info("Running periodic task distribute_deposits")
    jobcoin_mixer.process_new_transactions()
    # logger.info(
    #     "Running periodic task get_new_deposits",
    #     json.dumps(jobcoin_mixer.deposit_address_store),
    # )
