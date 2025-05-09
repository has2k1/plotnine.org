import os
import re
import sys
from pathlib import Path
from typing import Callable

from _repo import Git

gh_output_file = os.environ.get("GITHUB_OUTPUT")

# The "branch" should be one of the targets that the Makefile
# knows how to checkout. i.e. The should be a checkout-<branch-name>
# in the Makefile
BRANCH = re.compile(
    r"^plotnine-branch:\s+(?P<branch>release|pre-release|main|dev)\s*$",
    re.MULTILINE,
)


def set_plotnine_branch(pr_message_file: str):
    """
    Set the plotnine-branch to build

    Checks the pr message or the commit message for

        plotnine-branch: branch-name
    """
    if not gh_output_file:
        return

    pr_message = Path(pr_message_file).read_text()
    text = f"{pr_message}\n{Git.commit_message()}"
    m = BRANCH.search(text)
    branch = m.group("branch") if m else "release"

    with Path(gh_output_file).open("a") as f:
        print(f"plotnine-branch={branch}", file=f)


def process_request(task_name: str, *args: str) -> str | None:
    if task_name in TASKS:
        return TASKS[task_name](*args)


TASKS: dict[str, Callable[[], str | None]] = {
    "set_plotnine_branch": set_plotnine_branch,
}

if __name__ == "__main__":
    task_name, *args = sys.argv[1:]
    output = process_request(task_name, *args)
    if output:
        print(output)
