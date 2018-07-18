# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for loan states."""

from invenio_circulation.api import Loan


def test_loan_creation(db, params):
    """Test loan checkout and checkin."""
    loan = Loan.create({})
    assert loan.state == 'CREATED'

    loan.checkout(**params)
    assert loan.state == 'ITEM_ON_LOAN'

    loan.checkin(**params)
    assert loan.state == 'ITEM_RETURNED'


def test_conditional_checkout(app, db, params):
    """Test loan checkout and checkin."""
    loan = Loan.create({})
    loan.checkout(**params)
    assert loan.state == 'ITEM_ON_LOAN'
    assert loan['start_date'] == params.get('transaction_date')


def test_storing_loan_parameters(db, params):
    """."""
    loan = Loan.create({})

    loan.checkout(**params)

    params['state'] = 'ITEM_ON_LOAN'
    params['start_date'] = loan['start_date']
    params['end_date'] = loan['end_date']
    assert loan == params


def test_persist_loan(db, params):
    """."""
    loan = Loan.create({})
    loan.checkout(**params)
    db.session.commit()

    loan = Loan.get_record(loan.id)
    assert loan.state == 'ITEM_ON_LOAN'


def test_validate_item_in_transit(app, db, params):
    """."""
    loan = Loan.create({})
    params['pickup_location_pid'] = 'pickup_location_pid'

    loan.request(**params)
    assert loan.state == 'PENDING'

    app.config['CIRCULATION_ITEM_LOCATION_RETRIEVER'] =\
        lambda x: 'external_location_pid'
    loan.validate_request()
    assert loan.state == 'ITEM_IN_TRANSIT'


def test_validate_item_at_desk(app, db, params):
    """."""
    loan = Loan.create({})
    params['pickup_location_pid'] = 'pickup_location_pid'

    loan.request(**params)
    assert loan.state == 'PENDING'

    app.config['CIRCULATION_ITEM_LOCATION_RETRIEVER'] =\
        lambda x: 'pickup_location_pid'
    loan.validate_request()
    assert loan.state == 'ITEM_AT_DESK'
