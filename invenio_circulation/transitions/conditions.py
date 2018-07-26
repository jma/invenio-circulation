# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Circulation transitions conditions."""

from flask import current_app

from ..api import get_pending_loans_for_item


def is_pickup_at_same_library(item_pid, pickup_location_pid):
    """."""
    item_location_pid = current_app.config.get(
        'CIRCULATION_ITEM_LOCATION_RETRIEVER'
    )(item_pid)
    return pickup_location_pid == item_location_pid


def should_item_be_returned(item_pid, transaction_location_pid):
    """."""
    # pending loans
    pendings = len(get_pending_loans_for_item(item_pid))
    if pendings:
        return True

    # same location
    item_location_pid = current_app.config.get(
        'CIRCULATION_ITEM_LOCATION_RETRIEVER'
    )(item_pid)

    return transaction_location_pid == item_location_pid
