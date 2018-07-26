# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation exceptions."""


class CirculationException(Exception):
    """."""

    def __init__(self, msg):
        """."""
        self.msg = msg


class InvalidState(CirculationException):
    """State not found in circulation configuration."""


class TransitionValidationFailed(CirculationException):
    """Transition validation failed."""


class NoValidTransitionAvailable(CirculationException):
    """Exception raised when all transitions validation failed."""


class TransitionPermissionsFailed(CirculationException):
    """."""
