#!/bin/sh

# SPDX-FileCopyrightText: 2022 Brian Kubisiak <brian@kubisiak.com>
#
# SPDX-License-Identifier: GPL-3.0-only

export PYTHONPATH=.
export PYTHONDONTWRITEBYTECODE=1
export PATH="${PATH}:./scripts"

exec "$@"
