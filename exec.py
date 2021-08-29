from typing import List
import sys
import subprocess

def execute_save(command: List[str]):
    returncode, stdout, stderr = execute(command)
    if returncode == 0:
        return stdout
    else:
        raise Exception


def execute(command: List[str]):
    """
    Run the given command in a subprocess and pass stdin (if given) to that process.
    Wait for command to complete.

    :param command: A command to executed as list of words, e.g. ['echo', 'Hello world!']
    :return: (exit_code, stdout, stderr)
    """

    completed: subprocess.CompletedProcess = subprocess.run(
        command,
        stdin=sys.stdin,
        capture_output=True,
        check=False,
        text=True
    )
    return completed.returncode, completed.stdout, completed.stderr
