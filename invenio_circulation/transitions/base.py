# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Circulation base transitions."""

from ..errors import TransitionValidationFailed
from ..proxies import current_circulation


def check_trigger(f):
    """."""
    def inner(self, loan, **kwargs):
        """."""
        if kwargs.get('trigger', 'next') != self.trigger:
            raise TransitionValidationFailed(
                msg='No param `trigger` with value `{0}` found.'
                    .format(self.trigger))
        return f(self, loan, **kwargs)
    return inner


class Transition(object):
    """A transition object that is triggered on conditions."""

    def __init__(self, src, dest, trigger='next', permission_factory=None,
                 **kwargs):
        """."""
        self.src = src
        self.dest = dest
        self.trigger = trigger
        self.permission_factory = permission_factory

    @check_trigger
    def before(self, loan, **kwargs):
        """Evaluate conditions and raise if anything wrong."""
        if not all([self.src in current_circulation.circulation.transitions,
                    self.dest in current_circulation.circulation.transitions]):
            raise TransitionValidationFailed(
                msg='Source state `{0}` or destination state `{1}` not in '
                    '[{2}]'.format(
                        self.src,
                        self.dest,
                        current_circulation.circulation.transitions.keys()
                    )
            )

    def update_loan(self, loan, **kwargs):
        """Update current loan with new values."""
        loan.update(kwargs)

    def execute(self, loan, **kwargs):
        """."""
        self.before(loan, **kwargs)
        self.update_loan(loan, **kwargs)
        loan['state'] = self.dest
        self.after(loan, **kwargs)

    def after(self, loan, **kwargs):
        """."""
        loan.commit()
        # TODO: index loan here
