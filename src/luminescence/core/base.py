"""Base record type shared by every luminescence data object.

Port of the R virtual class ``RLum`` (``RLum-class.R``): the common
originator/info/uid/pid slots and the ``replicate_RLum`` method inherited
by every ``RLum.*`` subclass.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


def validate_positive_scalar(value: int, *, name: str) -> None:
    """Raise ``ValueError`` unless ``value`` is a positive integer.

    Booleans are rejected; ``name`` names the offending parameter in the message.
    """
    if isinstance(value, bool) or value <= 0:
        raise ValueError(f"'{name}' should be a positive integer")


@dataclass(kw_only=True)
class Record:
    """Common base for every luminescence data object.

    Attributes:
        originator: Name of the function that produced this record.
        info: Free-form metadata.
        uid: Unique id, generated automatically if not given.
        pids: Provenance chain of parent uids.
    """

    originator: str
    info: dict[str, Any] = field(default_factory=dict)
    uid: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)
    pids: tuple[str, ...] = field(default=(), compare=False)

    def replicate(self, times: int = 1) -> list[Record]:
        """Return a list holding this record ``times`` times.

        Raises:
            ValueError: If ``times`` is not a positive integer.
        """
        validate_positive_scalar(times, name="times")
        return [self for _ in range(times)]
