# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.


"""Click command-line interface for circulation management."""

from __future__ import absolute_import, print_function

import click


@click.group()
def circulation():
    """Records management."""


@circulation.command()
@click.argument('output_file_name')
def diagram(output_file_name):
    """Save the circulation state diagram to a png file."""
    from .api import Loan

    if not Loan.export_diagram(output_file_name):
        raise click.Abort()
