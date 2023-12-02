#!/bin/python

# MIT License
#
# Copyright (c) 2023 ArthurPV
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
