# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan states."""

from datetime import timedelta

import pytest
from helpers import SwappedConfig, SwappedNestedConfig

from invenio_circulation.api import Loan, is_item_available
from invenio_circulation.errors import NoValidTransitionAvailable, \
    TransitionConstraintsViolation
from invenio_circulation.proxies import current_circulation
from invenio_circulation.utils import parse_date


def test_loan_checkout_checkin(loan_created, db, params):
    """Test loan checkout and checkin actions."""
    assert loan_created['state'] == 'CREATED'

    loan = current_circulation.circulation.trigger(
        loan_created, **dict(params, trigger='checkout')
    )
    db.session.commit()
    assert loan['state'] == 'ITEM_ON_LOAN'

    # set same transaction location to avoid "in transit"
    same_location = params['transaction_location_pid']
    with SwappedConfig('CIRCULATION_ITEM_LOCATION_RETRIEVER',
                       lambda x: same_location):
        loan = current_circulation.circulation.trigger(loan, **dict(params))
        db.session.commit()
        assert loan['state'] == 'ITEM_RETURNED'


def test_loan_request(db, params):
    """Test loan request action."""
    loan = Loan.create({})
    assert loan['state'] == 'CREATED'

    loan = current_circulation.circulation.trigger(
        loan, **dict(params,
                     trigger='request',
                     pickup_location_pid='pickup_location_pid')
    )
    db.session.commit()
    assert loan['state'] == 'PENDING'


def test_cancel_action(loan_created, db, params):
    """Test should pass when calling `cancel` from `ITEM_ON_LOAN`."""
    loan = current_circulation.circulation.trigger(
        loan_created, **dict(params, trigger='checkout')
    )
    db.session.commit()

    current_circulation.circulation.trigger(
        loan_created, **dict(params, trigger='cancel')
    )
    assert loan['state'] == 'CANCELLED'


def test_cancel_fail(loan_created, params):
    """Test should fail when calling `cancel` from `CREATED`."""
    with pytest.raises(NoValidTransitionAvailable):
        current_circulation.circulation.trigger(
            loan_created, **dict(params, trigger='cancel')
        )


def test_validate_item_in_transit_for_pickup(loan_created, db, params):
    """."""
    loan = current_circulation.circulation.trigger(
        loan_created, **dict(params,
                             trigger='request',
                             pickup_location_pid='pickup_location_pid')
    )
    db.session.commit()
    assert loan['state'] == 'PENDING'

    with SwappedConfig('CIRCULATION_ITEM_LOCATION_RETRIEVER',
                       lambda x: 'external_location_pid'):
        loan = current_circulation.circulation.trigger(loan,
                                                       **dict(params))
        assert loan['state'] == 'ITEM_IN_TRANSIT_FOR_PICKUP'


def test_validate_item_at_desk(loan_created, db, params):
    """."""
    loan = current_circulation.circulation.trigger(
        loan_created, **dict(params,
                             trigger='request',
                             pickup_location_pid='pickup_location_pid')
    )
    db.session.commit()
    assert loan['state'] == 'PENDING'

    with SwappedConfig('CIRCULATION_ITEM_LOCATION_RETRIEVER',
                       lambda x: 'pickup_location_pid'):
        loan = current_circulation.circulation.trigger(loan_created,
                                                       **dict(params))
        assert loan['state'] == 'ITEM_AT_DESK'


def test_checkout_start_is_transaction_date(loan_created, db, params):
    """Test checkout start date to transaction date when not set."""
    number_of_days = 10

    with SwappedNestedConfig(
            ['CIRCULATION_POLICIES', 'checkout', 'duration_default'],
            lambda x: number_of_days):
        loan = current_circulation.circulation.trigger(
            loan_created, **dict(params, trigger='checkout')
        )
        db.session.commit()

        assert loan['state'] == 'ITEM_ON_LOAN'
        assert loan['start_date'] == loan['transaction_date']
        start_date = parse_date(loan['start_date'])
        end_date = start_date + timedelta(number_of_days)
        assert loan['end_date'] == end_date.isoformat()


def test_checkout_with_input_start_end_dates(loan_created, db, params):
    """Test checkout start and end dates are set as input."""
    start_date = '2018-02-01T09:30:00+02:00'
    end_date = '2018-02-10T09:30:00+02:00'
    loan = current_circulation.circulation.trigger(
        loan_created, **dict(params,
                             start_date=start_date,
                             end_date=end_date,
                             trigger='checkout')
    )
    db.session.commit()
    assert loan['state'] == 'ITEM_ON_LOAN'
    assert loan['start_date'] == start_date
    assert loan['end_date'] == end_date


def test_checkout_fails_when_wrong_dates(loan_created, params):
    """Test checkout fails when wrong input dates."""
    with pytest.raises(ValueError):
        current_circulation.circulation.trigger(
            loan_created, **dict(params,
                                 start_date='2018-xx',
                                 end_date='2018-xx',
                                 trigger='checkout')
        )


# def test_checkout_fails_when_duration_invalid(loan_created, params):
#     """Test checkout fails when wrong max duration."""
#     def validate_false(x, start_date, end_date):
#         raise Exception('invalid')
#     with pytest.raises(TransitionConstraintsViolation):
#         with SwappedNestedConfig(
#                 ['CIRCULATION_POLICIES', 'checkout', 'validate'],
#                 validate_false):
#             current_circulation.circulation.trigger(
#                 loan_created, **dict(params,
#                                      start_date='2018-02-01T09:30:00+02:00',
#                                      end_date='2018-04-10T09:30:00+02:00',
#                                      trigger='checkout')
#             )


def test_checkin_end_date_is_transaction_date(loan_created, db, params):
    """Test date the checkin date is the transaction date."""
    loan = current_circulation.circulation.trigger(
        loan_created, **dict(params,
                             start_date='2018-02-01T09:30:00+02:00',
                             end_date='2018-02-10T09:30:00+02:00',
                             trigger='checkout')
    )
    db.session.commit()
    assert loan['state'] == 'ITEM_ON_LOAN'

    same_location = params['transaction_location_pid']
    with SwappedConfig('CIRCULATION_ITEM_LOCATION_RETRIEVER',
                       lambda x: same_location):
        params['transaction_date'] = '2018-03-11T19:15:00+02:00'
        loan = current_circulation.circulation.trigger(loan, **dict(params))
        assert loan['state'] == 'ITEM_RETURNED'
        assert loan['end_date'] == params['transaction_date']


def test_get_loans(indexed_loans):
    """Test retrive loan list given belonging to an item."""
    loans = list(Loan.get_loans(item_pid='item_pending_1'))
    assert loans
    assert len(loans) == 1
    assert loans[0].get('item_pid') == 'item_pending_1'

    loans = list(
        Loan.get_loans(
            item_pid='item_multiple_pending_on_loan_7',
            exclude_states=['ITEM_ON_LOAN'],
        )
    )
    assert len(loans) == 2


def test_item_availibility(indexed_loans):
    """Test item_availibility with various conditions."""
    assert not is_item_available(item_pid='item_pending_1')
    assert not is_item_available(item_pid='item_on_loan_2')
    assert is_item_available(item_pid='item_returned_3')
    assert not is_item_available(item_pid='item_in_transit_4')
    assert not is_item_available(item_pid='item_at_desk_5')
    assert not is_item_available(item_pid='item_pending_on_loan_6')
    assert is_item_available(item_pid='item_returned_6')
    assert is_item_available(item_pid='no_loan')
