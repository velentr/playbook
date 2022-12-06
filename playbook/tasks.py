# SPDX-FileCopyrightText: 2022 Brian Kubisiak <brian@kubisiak.com>
#
# SPDX-License-Identifier: GPL-3.0-only

"""Various pre-set tasks for a playbook."""

import dataclasses

from playbook import Playbook, Transition


@dataclasses.dataclass
class AcceptUserInput(Playbook):
    """Please enter the required information to proceed."""

    prompt: str = "> "

    def do_run(self) -> Transition:
        """Prompt the user for input before continuing."""
        response = input(self.prompt)
        return self.accept(response)

    def accept(self, response: str) -> Transition:
        """Handle the user's input string before transitioning."""
        raise NotImplementedError()


@dataclasses.dataclass
class WaitToProceed(AcceptUserInput):
    """Pausing until you wish to continue."""

    prompt: str = "continue? (y|n) "

    def accept(self, response: str) -> Transition:
        """Prompt the user to continue."""
        if response == "y":
            return Transition.CONTINUE
        if response == "n":
            return Transition.HALT
        return Transition.RETRY
