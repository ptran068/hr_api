#!/usr/bin/env python

# author Huy
# date 9/18/2019
__all__ = ['Genders']

from api.base_const import const


class Genders(const):
    Select = 0

    GENDERS = (
        (0, 'male'),
        (1, 'female'),
        (2, 'other'),
    )
