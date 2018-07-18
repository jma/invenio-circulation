# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import shutil
import tempfile
from datetime import datetime

import pytest
from flask import Flask
from flask.cli import ScriptInfo
from flask_babelex import Babel
from invenio_db import db as db_
from invenio_db.ext import InvenioDB
from invenio_records.ext import InvenioRecords
from sqlalchemy_utils.functions import create_database, database_exists

from invenio_circulation.ext import InvenioCirculation


@pytest.yield_fixture()
def instance_path():
    """Temporary instance path."""
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)


@pytest.fixture()
def params():
    """."""
    now = datetime.now().strftime('%Y-%m-%d')
    return dict(transaction_user_pid='user_pid', patron_pid='patron_pid',
                item_pid='item_pid', transaction_location_pid='loc_pid',
                transaction_date=now)


@pytest.fixture
def script_info(app):
    """Get ScriptInfo object for testing CLI."""
    return ScriptInfo(create_app=lambda info: app)


@pytest.yield_fixture
def diagram_file_name():
    """Temporary digram file name."""
    file_name = tempfile.mkstemp(prefix='test_diagram_', suffix='.png')[1]
    yield file_name
    os.remove(file_name)


@pytest.yield_fixture(scope='session')
def tmp_db_path():
    """Temporary database path."""
    os_path = tempfile.mkstemp(prefix='circulation_test_', suffix='.db')[1]
    path = 'sqlite:///' + os_path
    yield path
    os.remove(os_path)


@pytest.fixture()
def base_app(instance_path, tmp_db_path):
    """Flask application fixture."""
    app_ = Flask('testapp', instance_path=instance_path)
    app_.config.update(
        SECRET_KEY='SECRET_KEY',
        SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI',
                                               tmp_db_path),
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        TESTING=True,
    )
    Babel(app_)
    return app_


@pytest.yield_fixture()
def app(base_app):
    """Flask application fixture."""
    InvenioDB(base_app)
    InvenioRecords(base_app)
    InvenioCirculation(base_app)
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
