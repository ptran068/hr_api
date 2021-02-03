#!/usr/bin/env python

# author Dat
# date 29/08/2020
__all__ = ['Relationships']

from api.base_const import const


class Relationships(const):

    RELATIONSHIPS = (
        ('FATHER', 'FATHER'),
        ('MOTHER', 'MOTHER'),
        ('CHILD', 'CHILD'),
        ('SPOUSE', 'SPOUSE'),
    )
