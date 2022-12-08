# SPDX-FileCopyrightText: 2022 Brian Kubisiak <brian@kubisiak.com>
#
# SPDX-License-Identifier: GPL-3.0-only

"""Various pre-set tasks for a playbook."""

import dataclasses
import readline
import typing as T

from playbook import Playbook, Transition


def _complete_yn(text: str, state: int) -> T.Optional[str]:
    """Completion function for completing y|n."""
    responses = ["y", "n"]
    if text == "" and state < len(responses):
        return responses[state]
    if text in responses and state == 0:
        return text
    return None


@dataclasses.dataclass
class AcceptUserInput(Playbook):
    """Please enter the required information to proceed."""

    prompt: str = "> "

    def do_run(self) -> Transition:
        """Prompt the user for input before continuing.

        Once the input is received, calls self.accept(response) for handling the
        user's input.

        You'll likely want to set up a tab completion function in the prepare
        phase (and remove it in the cleanup phase).
        """
        try:
            response = input(self.prompt)
        except EOFError:
            print("\n\nno input provided")
            return Transition.HALT
        return self.accept(response)

    def accept(self, response: str) -> Transition:
        """Handle the user's input string before transitioning."""
        raise NotImplementedError()


@dataclasses.dataclass
class WaitToProceed(AcceptUserInput):
    """Pausing until you wish to continue."""

    prompt: str = "continue? (y|n) "

    @classmethod
    def do_prepare(cls) -> None:
        """Set up tab completion to prepare for running."""
        readline.set_completer(_complete_yn)

    def accept(self, response: str) -> Transition:
        """Prompt the user to continue."""
        if response == "y":
            return Transition.CONTINUE
        if response == "n":
            return Transition.HALT
        return Transition.RETRY

    @classmethod
    def do_cleanup(cls) -> None:
        """Remove y/n tab completion."""
        readline.set_completer(None)
