# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation API."""

from datetime import datetime, timedelta

import ciso8601

from .errors import TransitionPoliciesViolation


def patron_exists(patron_pid):
    """Return True if patron exists, False otherwise."""
    return False


def item_exists(item_pid):
    """Return True if item exists, False otherwise."""
    return False


def is_item_available(item_pid):
    """."""
    return True


def item_location_retriever(item_pid):
    """Retrieve the location pid of the passed item pid."""
    pass


def get_default_loan_duration(loan):
    """Return a default loan duration in number of days."""
    return 30


def is_loan_valid(loan, start_date, end_date):
    """Validate the loan duration.

    :param start_date: :class:`~datetime.datetime` instance.
    :param end_date: :class:`~datetime.datetime` instance.
    """
    loan_duration = end_date - start_date
    if loan_duration > timedelta(days=60):
        raise TransitionPoliciesViolation('Loan duration too long')
    return True


def parse_date(date_datetime_or_str):
    """Parse string date with timezone and return a datetime object."""
    if not date_datetime_or_str:
        return date_datetime_or_str
    if isinstance(date_datetime_or_str, datetime):
        return date_datetime_or_str
    return ciso8601.parse_datetime(date_datetime_or_str)
