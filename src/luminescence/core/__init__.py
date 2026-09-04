"""Core object model: the base classes every luminescence record builds on."""

from luminescence.core.base import Record
from luminescence.core.curve import Curve

__all__ = ["Curve", "Record"]
