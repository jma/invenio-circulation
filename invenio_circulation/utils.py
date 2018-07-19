# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation API."""

from datetime import datetime, timedelta

from flask import current_app


def item_location_retriever(item_pid):
    """."""
    pass


def is_checkout_valid(
    transaction_user_pid,
    patron_pid,
    transaction_location_pid,
    transaction_date,
    item_pid,
    start_date=None,
    end_date=None,
):
    """."""
    default_loan_duration = \
        current_app.config.get('CIRCULATION_DEFAULT_LOAN_DURATION')
    if not start_date:
        start_date = transaction_date
    if not end_date:
        end_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(
            days=default_loan_duration
        )
        end_date = end_date.strftime('%Y-%m-%d')
    assert datetime.strptime(start_date, '%Y-%m-%d')
    assert datetime.strptime(end_date, '%Y-%m-%d')
    return (start_date, end_date)


def is_checkin_valid(
    transaction_user_pid,
    patron_pid,
    transaction_location_pid,
    transaction_date,
    item_pid,
    end_date=None,
):
    """."""
    if not end_date:
        end_date = transaction_date
    assert datetime.strptime(end_date, '%Y-%m-%d')
    return end_date


def is_request_valid(
    transaction_user_pid,
    patron_pid,
    transaction_location_pid,
    transaction_date,
    item_pid,
    pickup_location_pid=None,
    request_expire_date=None,
):
    """."""
    default_request_duration = \
        current_app.config.get('CIRCULATION_DEFAULT_REQUEST_DURATION')
    # item location by default
    if not pickup_location_pid:
        pickup_location_pid = current_app.config.get(
            'CIRCULATION_ITEM_LOCATION_RETRIEVER'
        )(item_pid)
    if not request_expire_date:
        request_expire_date = datetime.strptime(
            transaction_date, '%Y-%m-%d'
        ) + timedelta(days=default_request_duration)
        request_expire_date = request_expire_date.strftime('%Y-%m-%d')
    return (pickup_location_pid, request_expire_date)


def is_request_validate_valid(
    transaction_user_pid,
    patron_pid,
    item_pid,
    transaction_location_pid,
    transaction_date,
):
    """."""
    return True
