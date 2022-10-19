from jobcoin.constants import (
    GET_NEW_DEPOSITS_TASK_INTERVAL_SEC,
    DISTRIBUTE_DEPOSITS_TASK_INTERVAL_SEC,
)


broker_url = "redis://127.0.0.1:6379/0"
result_backend = "redis://127.0.0.1:6379/0"

imports = ("jobcoin.tasks",)

beat_schedule = {
    "get_new_deposits": {
        "task": "get_new_deposits",
        "schedule": GET_NEW_DEPOSITS_TASK_INTERVAL_SEC,
    }
}

beat_schedule = {
    "distribute_deposits": {
        "task": "distribute_deposits",
        "schedule": DISTRIBUTE_DEPOSITS_TASK_INTERVAL_SEC,
    }
}
