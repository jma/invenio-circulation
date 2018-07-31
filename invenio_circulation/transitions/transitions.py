# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Circulation custom transitions."""

from datetime import timedelta

from flask import current_app

from ..errors import TransitionConditionsFailed, TransitionConstraintsViolation
from ..transitions.base import Transition
from ..transitions.conditions import is_same_location
from ..utils import parse_date


def _ensure_valid_loan(loan):
    """Validate start and end dates for a loan."""
    loan.setdefault('start_date', loan['transaction_date'])
    start_date = parse_date(loan.get('start_date'))
    end_date = parse_date(loan.get('end_date'))
    if not end_date:
        get_loan_duration = current_app.config['CIRCULATION_POLICIES'][
            'checkout']['duration_default']
        number_of_days = get_loan_duration(loan)
        end_date = start_date + timedelta(days=number_of_days)

    if end_date < start_date:
        msg = 'The loan duration from `{0}` to `{1}` is not valid'.format(
            loan['start_date'],
            loan['end_date']
        )
        raise TransitionConstraintsViolation(msg=msg)

    is_valid = current_app.config['CIRCULATION_POLICIES']['checkout'][
        'validate']
    assert is_valid(loan, start_date, end_date)
    loan['start_date'] = start_date.isoformat()
    loan['end_date'] = end_date.isoformat()


class CreatedToPending(Transition):
    """Action to request to loan an item."""

    def before(self, loan, **kwargs):
        """Set a default pickup location if not passed as param."""
        super(CreatedToPending, self).before(loan, **kwargs)
        # set pickup location to item location if not passed as default
        if not loan.get('pickup_location_pid'):
            item_location_pid = current_app.config[
                'CIRCULATION_ITEM_LOCATION_RETRIEVER'](loan['item_pid'])
            loan['pickup_location_pid'] = item_location_pid


class CreatedToItemOnLoan(Transition):
    """Checkout action to perform a direct loan without a request."""

    def before(self, loan, **kwargs):
        """Validate checkout action."""
        super(CreatedToItemOnLoan, self).before(loan, **kwargs)

        _ensure_valid_loan(loan)

    def after(self, loan):
        """Convert dates to string before saving loan."""
        super(CreatedToItemOnLoan, self).after(loan)


class PendingToItemAtDesk(Transition):
    """Validate pending request to prepare the item at desk of its location."""

    def before(self, loan, **kwargs):
        """Validate if the item is for this location or should transit."""
        super(PendingToItemAtDesk, self).before(loan, **kwargs)

        if not is_same_location(loan['item_pid'], loan['pickup_location_pid']):
            msg = 'Invalid transition to {0}: Pickup is not at the same ' \
                  'library.'.format(self.dest)
            raise TransitionConditionsFailed(msg=msg)


class PendingToItemInTransitPickup(Transition):
    """Validate pending request to send the item to the pickup location."""

    def before(self, loan, **kwargs):
        """Validate if the item is for this location or should transit."""
        super(PendingToItemInTransitPickup, self).before(loan, **kwargs)
        if is_same_location(loan['item_pid'], loan['pickup_location_pid']):
            raise TransitionConditionsFailed(
                msg='Invalid transition to {0}: Pickup is at the same library.'
                    .format(self.dest))


class ItemAtDeskToItemOnLoan(Transition):
    """Check-out action to perform a loan when item ready at desk."""

    def before(self, loan, **kwargs):
        """Validate checkout action."""
        super(ItemAtDeskToItemOnLoan, self).before(loan, **kwargs)
        if loan.get('start_date'):
            loan['start_date'] = parse_date(loan['start_date'])
        if loan.get('end_date'):
            loan['end_date'] = parse_date(loan['end_date'])

        _ensure_valid_loan_duration(loan)

    def after(self, loan):
        """Convert dates to string before saving loan."""
        super(ItemAtDeskToItemOnLoan, self).after(loan)


class ItemOnLoanToItemInTransitHouse(Transition):
    """Check-in action when returning an item not to its belonging location."""

    def before(self, loan, **kwargs):
        """Validate check-in action."""
        super(ItemOnLoanToItemInTransitHouse, self).before(loan, **kwargs)
        if is_same_location(loan['item_pid'],
                            loan['transaction_location_pid']):
            msg = 'Invalid transition to {0}: item should be returned ' \
                  'because already to house.'.format(self.dest)
            raise TransitionConditionsFailed(msg=msg)

        # set end loan date as transaction date when completing loan
        loan['end_date'] = loan['transaction_date']

    def after(self, loan):
        """Convert dates to string before saving loan."""
        # loan['end_date'] = loan['end_date'].isoformat()
        super(ItemOnLoanToItemInTransitHouse, self).after(loan)


class ItemOnLoanToItemReturned(Transition):
    """Check-in action when returning an item to its belonging location."""

    def before(self, loan, **kwargs):
        """Validate check-in action."""
        super(ItemOnLoanToItemReturned, self).before(loan, **kwargs)
        if not is_same_location(loan['item_pid'],
                                loan['transaction_location_pid']):
            msg = 'Invalid transition to {0}: item should be in transit to ' \
                  'house.'.format(self.dest)
            raise TransitionConditionsFailed(msg=msg)

        # set end loan date as transaction date when completing loan
        loan['end_date'] = loan['transaction_date']

    def after(self, loan):
        """Convert dates to string before saving loan."""
        # loan['end_date'] = loan['end_date'].isoformat()
        super(ItemOnLoanToItemReturned, self).after(loan)
