"""Result record: named output data of one analysis call.

Port of ``RLum.Results`` (``RLum.Results-class.R``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from luminescence.core.base import Record


@dataclass(kw_only=True, eq=False)
class Result(Record):
    """Output of one analysis call, split into named parts.

    Attributes:
        data: Named result parts, e.g. ``"summary"``, ``"data"``, ``"args"``.
    """

    data: dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        pass

    def __len__(self):
        pass

    def get(self):
        pass

    def subset(self):
        pass

    def get_info(self):
        pass

    def names(self):
        pass

    def view(self):
        pass
