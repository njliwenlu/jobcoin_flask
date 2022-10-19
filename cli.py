#!/usr/bin/env python
from threading import Thread
import sys
import click

from jobcoin.jobcoin_mixer import jobcoin_mixer
from jobcoin.background_tasks import get_new_deposits, distribute_deposits


def start_background_tasks():
    thread1 = Thread(target=get_new_deposits, daemon=True)
    thread2 = Thread(target=distribute_deposits, daemon=True)
    thread1.start()
    thread2.start()
    return [thread1, thread2]


@click.command()
def main(args=None):
    print("Welcome to the Jobcoin mixer!\n")
    tasks = start_background_tasks()

    while True:
        addresses = click.prompt(
            "Please enter a comma-separated list of new, unused Jobcoin "
            "addresses where your mixed Jobcoins will be sent.",
            prompt_suffix="\n[blank to quit] > ",
            default="",
            show_default=False,
        )
        if addresses.strip() == "":
            for task in tasks:
                task.join()
            sys.exit(0)

        deposit_address = jobcoin_mixer.get_new_deposit_address(addresses)
        click.echo(
            "\nYou may now send Jobcoins to address {deposit_address}. They "
            "will be mixed and sent to your destination addresses.\n".format(
                deposit_address=deposit_address
            )
        )


if __name__ == "__main__":
    sys.exit(main())
