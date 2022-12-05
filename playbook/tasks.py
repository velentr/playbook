# SPDX-FileCopyrightText: 2022 Brian Kubisiak <brian@kubisiak.com>
#
# SPDX-License-Identifier: GPL-3.0-only

"""Various pre-set tasks for a playbook."""

import dataclasses

from playbook import Playbook, Transition


@dataclasses.dataclass
class WaitToProceed(Playbook):
    """Pausing until you wish to continue."""

    prompt: str = "continue? (y|n) "

    def do_run(self) -> Transition:
        """Prompt the user to continue."""
        response = input(self.prompt)
        if response == "y":
            return Transition.CONTINUE
        if response == "n":
            return Transition.HALT
        return Transition.RETRY
