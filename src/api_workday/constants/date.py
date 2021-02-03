#!/usr/bin/env python

# author Huy 
# date 9/23/2019

from api.base_const import const


class Workday(const):
    MORNING = 'Morning'
    AFTERNOON = 'Afternoon'
    FULL = 'All day'
    INSURANCE = 'Insurance pay'
    COMPANY = 'Company pay'

    TYPES = (
        (MORNING, 'Morning'),
        (AFTERNOON, 'Afternoon'),
        (FULL, 'All day')
    )

    LEAVE = 'Leave'
    REMOTE = 'Remote work'

    IN_WEEK = 'In Week'
    END_WEEK = 'End Week'
    ALL_WEEK = 'All Week'

    OT_DAYS = (
        (0, IN_WEEK),
        (1, END_WEEK),
        (2, ALL_WEEK)
    )

    DEFAULT_START_HOUR = '08:00'
    DEFAULT_END_HOUR = '17:30'
    DEFAULT_START_HOUR_AFTERNOON = '13:30'

    STATUS_ACCEPTED = 'Accepted'
    STATUS_PASSED = 'Passed'
    STATUS_PENDING = 'Pending'
    STATUS_REJECTED = 'Rejected'
    STATUS_CANCEL = 'Cancel'
    STATUS_FORWARDED = 'Forwarded'
    STATUS_APPROVED = 'Approved'

    TYPE_LEAVES = (
        (1, INSURANCE),
        (0, COMPANY)
    )

    FIRST_MONTH = 0
    LAST_MONTH = 12

    FIRST_DAY = 0
    LAST_DAY = 31

    ANNUAL_LEAVE = 1

    STT_NUM_NOT_ENOUGH = 'The number of days off is not enough'
