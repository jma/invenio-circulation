# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for the circulation of bibliographic items."""

# TODO: This is an example file. Remove it if your package does not use any
# extra configuration variables.

from .utils import is_checkout_valid, item_location_retriever

CIRCULATION_DEFAULT_VALUE = 'foobar'
"""Default value for the application."""

CIRCULATION_BASE_TEMPLATE = 'invenio_circulation/base.html'
"""Default base template for the demo page."""

CIRCULATION_ITEM_LOCATION_RETRIEVER = item_location_retriever

CIRCULATION_POLICIES = dict(checkout=is_checkout_valid)
