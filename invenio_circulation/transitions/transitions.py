# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Circulation custom transitions."""

from ..errors import TransitionValidationFailed
from ..transitions.base import Transition
from ..transitions.conditions import is_pickup_at_same_library, \
    should_item_be_returned


class PendingToItemAtDesk(Transition):
    """."""

    def before(self, loan, **kwargs):
        """."""
        super(PendingToItemAtDesk, self).before(loan, **kwargs)
        if not is_pickup_at_same_library(
            loan['item_pid'],
            loan['pickup_location_pid']
        ):
            raise TransitionValidationFailed(
                msg='Invalid transition to {0}: Pickup is not at the same '
                    'library.'.format(self.dest))


class PendingToItemInTransitPickup(Transition):
    """."""

    def before(self, loan, **kwargs):
        """."""
        super(PendingToItemInTransitPickup, self).before(loan, **kwargs)
        if is_pickup_at_same_library(
            loan['item_pid'],
            loan['pickup_location_pid']
        ):
            raise TransitionValidationFailed(
                msg='Invalid transition to {0}: Pickup is at the same library.'
                    .format(self.dest))


class ItemOnLoanToItemInTransitHouse(Transition):
    """."""

    def before(self, loan, **kwargs):
        """."""
        super(ItemOnLoanToItemInTransitHouse, self).before(loan, **kwargs)
        if should_item_be_returned(
            loan['item_pid'],
            kwargs.get('transaction_location_pid')
        ):
            raise TransitionValidationFailed(
                msg='Invalid transition to {0}: item should be returned.'
                    .format(self.dest))


class ItemOnLoanToItemReturned(Transition):
    """."""

    def before(self, loan, **kwargs):
        """."""
        super(ItemOnLoanToItemReturned, self).before(loan, **kwargs)
        if not should_item_be_returned(
            loan['item_pid'],
            kwargs.get('transaction_location_pid')
        ):
            raise TransitionValidationFailed(
                msg='Invalid transition to {0}: item should be in transit to '
                    'house.'.format(self.dest))


class CreatedToPending(Transition):
    """."""

    def before(self, loan, **kwargs):
        """."""
        super(CreatedToPending, self).before(loan, **kwargs)
        if not kwargs.get('pickup_location_pid'):
            raise TransitionValidationFailed(
                msg='Invalid transition to {0}: Pickup location is required'
                    .format(self.dest))
