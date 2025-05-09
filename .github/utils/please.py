import re
import sys
from typing import Callable

from _repo import Git

gh_output_file = os.environ.get("GITHUB_OUTPUT")


def process_request(task_name: str, *args: str) -> str | None:
    if task_name in TASKS:
        return TASKS[task_name](*args)


TASKS: dict[str, Callable[[], str | None]] = {
}

if __name__ == "__main__":
    task_name, *args = sys.argv[1:]
    output = process_request(task_name, *args)
    if output:
        print(output)
