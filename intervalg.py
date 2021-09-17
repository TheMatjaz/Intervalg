#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2021, Matjaž Guštin <dev@matjaz.it> <https://matjaz.it>.
# Released under the BSD 3-Clause License

import math
import re
from numbers import Number
from typing import Tuple, Optional


class Interval(tuple):
    # Immutable class
    def __new__(cls, *args, **kwargs):
        if len(args) == 0:
            lower = upper = None  # Infinite interval
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, cls):
                return arg  # Return arg itself, as immutable
            elif isinstance(arg, str):
                lower, upper = cls._from_string(arg)
            elif arg is None:
                lower = upper = None
            elif isinstance(arg, Number):
                # Single number is an interval of length 0
                if not math.isfinite(arg):
                    lower = upper = None
                else:
                    lower = upper = arg
            else:
                # Try iterating arg
                lower, upper = arg
                # Raises TypeError if not iterable arg
                # Raises ValueError if not exactly 2 values in arg
        else:
            lower, upper = args
            # Raises ValueError if not exactly 2 values in args
        # kwargs overwriting anything (if anything at all) specified in args
        lower = kwargs.get('lower', kwargs.get('min', lower))
        upper = kwargs.get('upper', kwargs.get('max', upper))
        if lower is not None and upper is not None and lower > upper:
            # Swap if out of order
            lower, upper = upper, lower
        # Replace undefined values with numerically useful ones
        if lower is None:
            lower = -math.inf
        if upper is None:
            upper = +math.inf
        return tuple.__new__(Interval, (lower, upper))

    @classmethod
    def _from_string(cls, string: str
                     ) -> Tuple[Optional[Number], Optional[Number]]:
        """Parses the lower and upper interval limits from a human-readable
        string.

        Empty intervals: `[]` `[[` `]]` `][` `[)` `(]` `()`
        Empty intervals are counted as infinite intervals.
        Infinite interval: `[,]` `[-inf,inf]` `[None,None]` `[nan,nan]`
        Only lower: `[42,]` `[42,None]` `[42,None]` `[42,nan]` `[42,inf]`
        Only upper: `[,42]` `[None,42]` `[nan,42]` `[-inf,42]`
        Both limits: `[42,43]` `[42,None]` `[42,None]` `[42,nan]` `[42,inf]`
        In all cases all brackets are acceptable.
        No distinction is done between open and closed interval limits for now.
        Acceptable separators between the lower and upper limit are: `,;:|`
        """
        string = re.sub(r'\s+', '', string).lower().strip('[]()')
        string = re.sub(r'[;:|]', ',', string)
        fields = string.split(',')
        if len(fields) == 1:
            # Infinite interval, no separator was used
            return None, None
        elif len(fields) == 2:
            lower = cls._parse_string_limit(fields[0])
            upper = cls._parse_string_limit(fields[1])
            return lower, upper
        if len(fields) > 2:
            raise ValueError(
                'Too many fields, must be at most 2. '
                f'Found {len(fields)}.'
            )

    @classmethod
    def _parse_string_limit(cls, string: str) -> Optional[Number]:
        """Converts a single interval limit (lower or upper) from string
        to a number or None if undefined (open interval)."""
        string = string.strip()
        if string in ('', 'none', 'null'):
            return None
        try:
            return int(string, base=0)  # Accepts also 0x, 0o, 0b prefixes
        except ValueError:
            value = float(string)
            if math.isfinite(value):
                return value
            else:
                return None  # nan, inf, +inf, -inf

    # ----- Properties -----
    @property
    def lower(self):
        return self[0]

    @property
    def upper(self):
        return self[1]

    @property
    def min(self):
        return self[0]

    @property
    def max(self):
        return self[1]

    @property
    def is_infinite(self) -> bool:
        return math.isinf(self.lower) and math.isinf(self.upper)

    @property
    def is_finite(self) -> bool:
        return math.isfinite(self.lower) and math.isfinite(self.upper)

    def __bool__(self) -> bool:
        return self.is_finite

    @property
    def is_lower_open(self) -> bool:
        return math.isinf(self.lower)

    @property
    def is_upper_open(self) -> bool:
        return math.isinf(self.upper)

    def __repr__(self) -> str:
        return f'[{self.lower}, {self.upper}]'

    def __hash__(self) -> int:
        return hash(tuple(self))

    # ----- Size properties -----
    def __len__(self) -> int:
        return int(math.ceil(self.upper - self.lower))

    @property
    def true_len(self) -> float:
        return self.upper - self.lower

    @property
    def is_single_number(self) -> bool:
        return self.lower == self.upper

    # ----- Binary arithmetic operators -----
    def __add__(self, other) -> 'Interval':
        other = Interval(other)
        return Interval(self.lower + other.lower, self.upper + other.upper)

    def __radd__(self, other) -> 'Interval':
        return self + other  # Commutative with __add__

    def __sub__(self, other) -> 'Interval':
        other = Interval(other)
        return Interval(self.lower - other.lower, self.upper - other.upper)

    def __rsub__(self, other) -> 'Interval':
        other = Interval(other)  # NOT commutative with __sub__
        return Interval(other.lower - self.lower, other.upper - self.upper)

    def __mul__(self, other) -> 'Interval':
        other = Interval(other)
        return Interval(self.lower * other.lower, self.upper * other.upper)

    def __rmul__(self, other) -> 'Interval':
        return self * other  # Commutative with __mul__

    def __truediv__(self, other) -> 'Interval':
        other = Interval(other)
        return Interval(self.lower / other.lower, self.upper / other.upper)

    def __rtruediv__(self, other) -> 'Interval':
        other = Interval(other)  # NOT commutative with __truediv__
        return Interval(other.lower / self.lower, other.upper / self.upper)

    def __floordiv__(self, other) -> 'Interval':
        other = Interval(other)
        return Interval(self.lower // other.lower, self.upper // other.upper)

    def __rfloordiv__(self, other) -> 'Interval':
        other = Interval(other)  # NOT commutative with __floordiv__
        return Interval(other.lower // self.lower, other.upper // self.upper)

    def __mod__(self, other) -> 'Interval':
        other = Interval(other)
        return Interval(self.lower % other.lower, self.upper % other.upper)

    def __rmod__(self, other) -> 'Interval':
        other = Interval(other)  # NOT commutative with __mod__
        return Interval(other.lower % self.lower, other.upper % self.upper)

    def __lshift__(self, other) -> 'Interval':
        other = Interval(other)
        return Interval(self.lower << other.lower, self.upper << other.upper)

    def __rlshift__(self, other) -> 'Interval':
        other = Interval(other)  # NOT commutative with __lshift__
        return Interval(other.lower << self.lower, other.upper << self.upper)

    def __rshift__(self, other) -> 'Interval':
        other = Interval(other)
        return Interval(self.lower >> other.lower, self.upper >> other.upper)

    def __rrshift__(self, other) -> 'Interval':
        other = Interval(other)  # NOT commutative with __rshift__
        return Interval(other.lower >> self.lower, other.upper >> self.upper)

    def __divmod__(self, other) -> Tuple['Interval', 'Interval']:
        other = Interval(other)
        lowers = divmod(self.lower, other.lower)
        uppers = divmod(self.upper, other.upper)
        return Interval(lowers[0], uppers[0]), Interval(lowers[1], uppers[1])

    def __rdivmod__(self, other) -> Tuple['Interval', 'Interval']:
        other = Interval(other)  # NOT commutative with __divmod__
        lowers = divmod(other.lower, self.lower)
        uppers = divmod(other.upper, self.upper)
        return Interval(lowers[0], uppers[0]), Interval(lowers[1], uppers[1])

    def __pow__(self, power, modulo=None) -> 'Interval':
        power = Interval(power)
        return Interval(pow(self.lower, power.lower, modulo),
                        pow(self.upper, power.upper, modulo))

    # TODO __rpow__ not implemented

    # Unary arithmetic operators
    def __neg__(self) -> 'Interval':
        return Interval(-self.lower, -self.upper)

    def __pos__(self) -> 'Interval':
        return self

    def __abs__(self) -> 'Interval':
        return Interval(abs(self.lower), abs(self.upper))

    def __round__(self) -> 'Interval':
        return Interval(round(self.lower), round(self.upper))

    def __floor__(self) -> 'Interval':
        return Interval(math.floor(self.lower), math.floor(self.upper))

    def __ceil__(self) -> 'Interval':
        return Interval(math.ceil(self.lower), math.ceil(self.upper))

    def __trunc__(self) -> 'Interval':
        return Interval(math.trunc(self.lower), math.trunc(self.upper))

    def round_wider(self) -> 'Interval':
        lower = math.floor(self.lower) if self.lower >= 0 else math.ceil(self.lower)
        upper = math.ceil(self.upper) if self.upper >= 0 else math.floor(self.upper)
        return Interval(lower, upper)

    def round_narrower(self) -> 'Interval':
        lower = math.ceil(self.lower) if self.lower >= 0 else math.floor(self.lower)
        upper = math.floor(self.upper) if self.upper >= 0 else math.ceil(self.upper)
        return Interval(lower, upper)

    def sign(self) -> 'Interval':
        lower = 1 if self.lower > 0 else -1 if self.lower < 0 else 0
        upper = 1 if self.upper > 0 else -1 if self.upper < 0 else 0
        return Interval(lower, upper)

    # Comparison operators
    def __eq__(self, other) -> bool:
        other = Interval(other)
        return self.lower == other.lower and self.upper == other.upper

    def __lt__(self, other) -> bool:
        other = Interval(other)
        return self.upper < other.lower

    def __le__(self, other) -> bool:
        other = Interval(other)
        return self.upper <= other.lower

    def __gt__(self, other) -> bool:
        other = Interval(other)
        return self.lower > other.upper

    def __ge__(self, other) -> bool:
        other = Interval(other)
        return self.lower >= other.upper

    # ----- Conversions -----
    def __complex__(self) -> complex:
        return complex(self.lower, self.upper)

    def to_dict(self) -> dict:
        return {'lower': self.lower, 'upper': self.upper}

    def to_range(self) -> range:
        # Works only for integer-limited intervals
        return range(self.lower, self.upper)

    def to_set(self) -> set:
        return set(self.to_range())

    # ----- Set-like operations -----
    def is_disjoint(self, other) -> bool:
        other = Interval(other)
        return self.upper < other.lower

    def is_superset(self, other) -> bool:
        other = Interval(other)
        return self.lower <= other.lower and other.upper <= self.upper

    def is_subset(self, other) -> bool:
        other = Interval(other)
        return other.lower <= self.lower and self.upper <= other.upper

    def __contains__(self, item) -> bool:
        return self.is_superset(item)

    def intersection(self, other, err_on_disjoint: bool = False) -> 'Interval':
        other = Interval(other)
        if self.is_disjoint(other):
            if err_on_disjoint:
                raise ValueError(
                    f'Disjoint Intervals {self}, {other}. Cannot intersect.'
                )
        return Interval(max(self.lower, other.lower),
                        min(self.upper, other.upper))

    def union(self, other, err_on_disjoint: bool = False) -> 'Interval':
        other = Interval(other)
        if self.is_disjoint(other):
            if err_on_disjoint:
                raise ValueError(
                    f'Disjoint Intervals {self}, {other}. Cannot create union.'
                )
        return Interval(min(self.lower, other.lower),
                        max(self.upper, other.upper))
