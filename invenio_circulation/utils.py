# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation API."""

from datetime import datetime, timedelta


def item_location_retriever(item_pid):
    """."""
    pass


def is_checkout_valid(transaction_user_pid,
                      patron_pid,
                      item_pid,
                      transaction_location_pid,
                      transaction_date,
                      start_date=None,
                      end_date=None):
    """."""
    if not start_date:
        start_date = datetime.strptime(transaction_date, '%Y-%m-%d')
    if not end_date:
        end_date = start_date + timedelta(days=30)
    return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
