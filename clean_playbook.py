#!/bin/python

import os

PLAYBOOKS_DIR = "playbooks"

if __name__ == "__main__":
    playbook = input("Enter the name of the playbook, do you want to clean: ")

    if playbook == "":
        print("The playbook name is empty")
        exit(1)

    playbook_path = os.path.join(PLAYBOOKS_DIR, playbook)

    if os.path.exists(playbook_path) is False:
        print("The playbook does not exist")
        exit(1)
    else:
        os.system(f"rm -rf {playbook_path}")
        print(f"The playbook {playbook} has been removed")
