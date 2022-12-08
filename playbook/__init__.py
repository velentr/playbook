# SPDX-FileCopyrightText: 2022 Brian Kubisiak <brian@kubisiak.com>
#
# SPDX-License-Identifier: GPL-3.0-only

"""Playbooks for semi-automated repetitive tasks."""

from __future__ import annotations

import argparse
import atexit
import enum
import importlib
import os
import readline
import sys
import textwrap
import typing as T


PLAYBOOK_HISTORY_PATH = os.path.expanduser("~/.playbook_history")
if os.path.exists(PLAYBOOK_HISTORY_PATH):
    readline.read_history_file(PLAYBOOK_HISTORY_PATH)
readline.set_history_length(256)
atexit.register(readline.write_history_file, PLAYBOOK_HISTORY_PATH)


class Transition(enum.Enum):
    """Transition for moving on to the next task."""

    CONTINUE = "continue"
    RETRY = "retry"
    HALT = "halt"


class Playbook:
    """A single repetitive task that must be accomplished."""

    wrapper = textwrap.TextWrapper()

    def do_run(self) -> Transition:
        """Run this playbook."""
        raise NotImplementedError()

    def _print_docstring(self) -> None:
        if self.__doc__ is None:
            return

        lines = self.__doc__.split("\n\n")
        paragraphs = [
            self.wrapper.wrap(textwrap.dedent(line)) for line in lines
        ]
        print()
        for paragraph in paragraphs:
            for line in paragraph:
                print(line)
            print()

    def run(self) -> None:
        """Run a playbook."""
        self._print_docstring()
        result = self.do_run()
        if result == Transition.CONTINUE:
            return
        if result == Transition.RETRY:
            print(f"re-trying {self.__class__.__name__}...")
            self.run()
        else:
            # the playbook either returned HALT or some unknown value
            print(f"cannot continue after {self.__class__.__name__}; exiting")
            sys.exit(1)

    @classmethod
    def serial(cls, doc: str, playbooks: T.List[Playbook]) -> T.Type[Playbook]:
        """Build a new playbook that runs the specified playbooks in series."""

        class SerialPlaybook(Playbook):
            """Default docstring to pass the linter."""

            def do_run(self) -> Transition:
                for playbook in playbooks:
                    playbook.run()
                return Transition.CONTINUE

        SerialPlaybook.__doc__ = doc

        return SerialPlaybook


def main() -> None:
    """Load and run a playbook."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-L",
        metavar="LOADPATH",
        type=str,
        help="add LOADPATH to the python path for loading playbooks",
    )
    parser.add_argument(
        "PLAYBOOK",
        type=str,
        help="python expression evaluating to the class of the playbook to run",
    )
    args = parser.parse_args()
    sys.path.append(args.L)

    (module, _, cls) = args.PLAYBOOK.rpartition(".")
    playbook = importlib.import_module(module).__dict__.get(cls, object)
    if not issubclass(playbook, Playbook):
        print(f"The expression {args.PLAYBOOK} doesn't evaluate to a playbook.")
        print("Cannot continue; exiting.")
        sys.exit(1)

    playbook().run()


if __name__ == "__main__":
    main()
