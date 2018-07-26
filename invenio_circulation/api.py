# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation API."""

from flask import current_app
from invenio_records.api import Record


class Loan(Record):
    """Loan record class."""

    def __init__(self, data, model=None):
        """."""
        data.setdefault(
            'state',
            current_app.config['CIRCULATION_LOAN_INITIAL_STATE']
        )
        super(Loan, self).__init__(data, model)


def get_pending_loans_for_item(item_pid):
    """."""
    # TODO: implement search on ES and fetch results from DB
    return []
