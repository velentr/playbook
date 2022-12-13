# SPDX-FileCopyrightText: 2022 Brian Kubisiak <brian@kubisiak.com>
#
# SPDX-License-Identifier: GPL-3.0-only

"""Various pre-set tasks for a playbook."""

import dataclasses
import glob
import os
import pathlib
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


@dataclasses.dataclass
class AcceptPathInput(AcceptUserInput):
    """Please enter a valid path."""

    prompt: str = "> "

    last_glob: T.Optional[str] = None
    cached_expansion: T.Optional[T.List[str]] = None

    # These need to be cached so they can be reloaded later.
    old_delims: T.Optional[str] = None

    def _complete_path(self, text: str, state: int) -> T.Optional[str]:
        """Completion function for completing paths using globs."""
        if text != self.last_glob:
            expansion = glob.glob(os.path.expanduser(text) + "*")
            # Did we do $HOME expansion?
            if len(expansion) > 0 and not expansion[0].startswith(text):
                # If so, replace $HOME with ~/ so that expansions match the text
                # already input by the user.
                home = os.path.expanduser("~/")
                expansion = ["~/" + s.removeprefix(home) for s in expansion]
            self.cached_expansion = expansion
            self.last_glob = text

        assert self.cached_expansion is not None
        if state >= len(self.cached_expansion):
            return None

        return self.cached_expansion[state]

    def do_prepare(self) -> None:
        """Set up tab completion for completing paths."""
        self.old_delims = readline.get_completer_delims()
        readline.set_completer_delims("\t\n")
        readline.set_completer(self._complete_path)

    def accept(self, response: str) -> Transition:
        """Accept the raw input string from the user and convert to a path."""
        response_path = pathlib.Path(os.path.expanduser(response))
        if not response_path.exists():
            raise RuntimeError(f"Path {response} does not exist!")
        return self.accept_path(response_path)

    def accept_path(self, response: pathlib.Path) -> Transition:
        """Handle the user's response path before transitioning."""
        raise NotImplementedError()

    def do_cleanup(self) -> None:
        """Remove path tab completion."""
        assert self.old_delims is not None
        readline.set_completer_delims(self.old_delims)
        readline.set_completer(None)
