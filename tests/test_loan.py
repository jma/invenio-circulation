# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan states."""

import pytest

from invenio_circulation.api import Loan


def test_loan_creation(db, params):
    """Test loan checkout and checkin."""
    loan = Loan.create({})
    assert loan.state == 'CREATED'

    loan.checkout(**params)
    assert loan.state == 'ITEM_ON_LOAN'

    loan.checkin(**params)
    assert loan.state == 'ITEM_RETURNED'


def test_storing_loan_parameters(loan, db, params):
    """."""
    loan.checkout(**params)

    params['state'] = 'ITEM_ON_LOAN'
    params['start_date'] = loan['start_date']
    params['end_date'] = loan['end_date']
    assert loan == params


def test_persist_loan(loan, db, params):
    """."""
    loan.checkout(**params)
    db.session.commit()

    loan = Loan.get_record(loan.id)
    assert loan.state == 'ITEM_ON_LOAN'


def test_validate_item_in_transit(loan, app, db, params):
    """."""
    loan.request(**dict(pickup_location_pid='pickup_location_pid', **params))
    assert loan.state == 'PENDING'

    app.config[
        'CIRCULATION_ITEM_LOCATION_RETRIEVER'
    ] = lambda x: 'external_location_pid'
    loan.validate_request(**params)
    assert loan.state == 'ITEM_IN_TRANSIT'


def test_validate_item_at_desk(loan, app, db, params):
    """."""
    loan.request(**dict(pickup_location_pid='pickup_location_pid', **params))
    assert loan.state == 'PENDING'

    app.config[
        'CIRCULATION_ITEM_LOCATION_RETRIEVER'
    ] = lambda x: 'pickup_location_pid'
    loan.validate_request(**params)
    assert loan.state == 'ITEM_AT_DESK'


def test_conditional_checkout(loan, app, db, params):
    """Test checkout with some conditions."""
    loan.checkout(**params)
    assert loan.state == 'ITEM_ON_LOAN'
    assert loan['start_date'] == params.get('transaction_date')

    loan = Loan.create({})
    loan.checkout(
        **dict(start_date='2020-01-01', end_date='2020-02-01', **params)
    )
    assert loan.state == 'ITEM_ON_LOAN'
    assert loan['start_date'] == '2020-01-01'
    assert loan['end_date'] == '2020-02-01'

    loan = Loan.create({})
    with pytest.raises(ValueError):
        loan.checkout(**dict(start_date='2020-01-xx', **params))
    with pytest.raises(ValueError):
        loan.checkout(**dict(end_date='2020-01-xx', **params))


def test_conditional_checkin(loan, app, db, params):
    """Test checkin with some conditions."""
    loan.checkout(**params)
    loan.checkin(**params)
    assert loan.state == 'ITEM_RETURNED'

    loan = Loan.create({})
    loan.checkout(**params)
    loan.checkin(**dict(end_date='2020-02-01', **params))
    assert loan.state == 'ITEM_RETURNED'
    assert loan['end_date'] == '2020-02-01'

    loan = Loan.create({})
    loan.checkout(**params)
    with pytest.raises(ValueError):
        loan.checkin(**dict(end_date='2020-01-xx', **params))


def test_conditional_request(loan, app, db, params):
    """Test request with some conditions."""
    loan.request(
        **dict(
            pickup_location_pid='my_pickup_location_pid',
            request_expire_date='2020-02-01',
            **params
        )
    )
    assert loan.state == 'PENDING'
    loan['request_expire_date'] == '2020-02-01'
    loan['pickup_location_pid'] == 'my_pickup_location_pid'

    loan = Loan.create({})
    app.config[
        'CIRCULATION_ITEM_LOCATION_RETRIEVER'
    ] = lambda x: 'custom_pickup_location_pid'
    loan.request(**params)
    assert loan.state == 'PENDING'
    loan['pickup_location_pid'] == 'custom_pickup_location_pid'
