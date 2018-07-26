# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import json
import os
import shutil
import tempfile
from datetime import datetime
from os.path import dirname, join

import pytest
from elasticsearch.exceptions import RequestError
from flask import Flask
from flask_babelex import Babel
from helpers import create_loan
from invenio_db import db as db_
from invenio_db.ext import InvenioDB
from invenio_indexer import InvenioIndexer
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import InvenioJSONSchemas
from invenio_pidstore.ext import InvenioPIDStore
from invenio_records.ext import InvenioRecords
from invenio_records_rest.ext import InvenioRecordsREST
from invenio_records_rest.utils import PIDConverter
from invenio_records_rest.views import create_blueprint_from_app
from invenio_search import InvenioSearch, current_search, current_search_client
from sqlalchemy_utils.functions import create_database, database_exists

from invenio_circulation.api import Loan
from invenio_circulation.ext import InvenioCirculation


@pytest.yield_fixture()
def instance_path():
    """Temporary instance path."""
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)


@pytest.yield_fixture()
def loan_created(db):
    """Minimal Loan object."""
    yield Loan.create({})


@pytest.fixture()
def params():
    """."""
    now = datetime.now().strftime('%Y-%m-%d')
    return dict(
        transaction_user_pid='user_pid',
        patron_pid='patron_pid',
        item_pid='item_pid',
        transaction_location_pid='loc_pid',
        transaction_date=now,
    )


@pytest.yield_fixture()
def loan_schema():
    """Loan Json schema."""
    yield {
        '$schema': 'http://localhost:5000/schema/loans/loan-v1.0.0.json'
    }


@pytest.yield_fixture(scope='session')
def tmp_db_path():
    """Temporary database path."""
    os_path = tempfile.mkstemp(prefix='circulation_test_', suffix='.db')[1]
    path = 'sqlite:///' + os_path
    yield path
    os.remove(os_path)


@pytest.fixture()
def base_app(instance_path):
    """Flask application fixture."""
    app_ = Flask('testapp', instance_path=instance_path)
    app_.config.update(
        SERVER_NAME='localhost:5000',
        SECRET_KEY='SECRET_KEY',
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite://'
        ),  # NOTE: in memory
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY=None,
        TESTING=True,
        JSONSCHEMAS_ENDPOINT='/schema',
        JSONSCHEMAS_HOST='localhost:5000',
    )
    Babel(app_)
    return app_


@pytest.yield_fixture()
def app(base_app):
    """Flask application fixture."""
    base_app.url_map.converters['pid'] = PIDConverter
    InvenioDB(base_app)
    InvenioRecords(base_app)
    InvenioRecordsREST(base_app)
    InvenioPIDStore(base_app)
    InvenioIndexer(base_app)
    InvenioPIDStore(base_app)
    InvenioSearch(base_app)
    InvenioCirculation(base_app)
    InvenioJSONSchemas(base_app)
    base_app.register_blueprint(create_blueprint_from_app(base_app))
    with base_app.app_context():
        yield base_app


@pytest.yield_fixture()
def db(app):
    """Database fixture."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()


@pytest.fixture()
def json_headers(app):
    """JSON headers."""
    return [
        ('Content-Type', 'application/json'),
        ('Accept', 'application/json'),
    ]


@pytest.yield_fixture(scope='session')
def test_data():
    """Load test records."""
    path = 'data/testloans.json'
    with open(join(dirname(__file__), path)) as fp:
        loans = json.load(fp)
    yield loans


@pytest.yield_fixture()
def test_loans(db, test_data):
    """Load test records."""
    loans = []
    for data in test_data:
        loans.append(create_loan(data))
    db.session.commit()
    yield loans


@pytest.yield_fixture()
def es(app):
    """Elasticsearch fixture."""
    try:
        list(current_search.create())
    except RequestError:
        list(current_search.delete(ignore=[404]))
        list(current_search.create(ignore=[400]))
    current_search_client.indices.refresh()
    yield current_search_client
    list(current_search.delete(ignore=[404]))


@pytest.yield_fixture()
def indexer(app, es):
    """Create a record indexer."""
    InvenioIndexer(app)
    yield RecordIndexer()


@pytest.yield_fixture()
def indexed_loans(indexer, test_loans):
    """Get a function to wait for records to be flushed to index."""
    for pid, loan in test_loans:
        indexer.index_by_id(loan.id)
    current_search.flush_and_refresh(index='loans')
    yield test_loans
