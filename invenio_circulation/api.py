# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation API."""

from elasticsearch import VERSION as ES_VERSION
from flask import current_app
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from .search import LoansSearch


class Loan(Record):
    """Loan record class."""

    def __init__(self, data, model=None):
        """."""
        data.setdefault(
            'state',
            current_app.config['CIRCULATION_LOAN_INITIAL_STATE']
        )
        super(Loan, self).__init__(data, model)

    @classmethod
    def get_loans(cls, item_pid, exclude_states=None):
        """."""
        search = LoansSearch()
        if exclude_states:
            if ES_VERSION[0] > 2:
                search = search.exclude('terms', state=exclude_states)
            else:
                from elasticsearch_dsl.query import Bool, Q

                search = search.query(
                    Bool(filter=[~Q('terms', state=exclude_states)])
                )
        search = search.filter('term', item_pid=item_pid).source(
            includes='loan_pid'
        )

        for result in search.scan():
            if result.loan_pid:
                yield cls.get_record_by_pid(result.loan_pid)

    @classmethod
    def get_record_by_pid(cls, pid, with_deleted=False):
        """Get ils record by pid value."""
        from .config import _CIRCULATION_LOAN_PID_TYPE
        resolver = Resolver(
            pid_type=_CIRCULATION_LOAN_PID_TYPE,
            object_type='rec',
            getter=cls.get_record,
        )
        persistent_identifier, record = resolver.resolve(str(pid))
        return record


def is_item_available(item_pid):
    """."""
    config = current_app.config
    cfg_item_available = config.get('CIRCULATION_POLICIES').get(
        'item_available'
    )
    if not cfg_item_available(item_pid):
        return False
    if list(
        Loan.get_loans(
            item_pid,
            exclude_states=config.get('CIRCULATION_STATES_ITEM_AVAILABLE'),
        )
    ):
        return False
    return True


def get_pending_loans_for_item(item_pid):
    """."""
    # TODO: implement search on ES and fetch results from DB
    return []
