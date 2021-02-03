#!/usr/bin/env python

# author Dat
# date 29/08/2020
__all__ = ['Titles']

from api.base_const import const


class Titles(const):

    # push a new, don't modify the original
    TITLES = (
        ('Director', 'Director'),
        ('Quality assurance', 'Quality assurance'),
        ('Project manager', 'Project manager'),
        ('Developer', 'Developer'),
        ('Human resource', 'Human resource'),
        ('Software architect', 'Software architecture'),
        ('Accountant', 'Accountant')
    )

