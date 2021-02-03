#!/usr/bin/env python

# author Huy 
# date 9/18/2019
__all__ = ['Banks']

from api.base_const import const


class Banks(const):
    No = 'No bank'

    BANKS = (
        (No, 'No bank'),
        ('ABBANK', 'ABBANK'),
        ('ACB', 'ACB'),
        ('AGRIBANK', 'AGRIBANK'),
        ('BACABANK', 'BACABANK'),
        ('BIDV', 'BIDV'),
        ('DONGABANK', 'DONGABANK'),
        ('EXIMBANK', 'EXIMBANK'),
        ('HDBANK', 'HDBANK'),
        ('IVB', 'IVB'),
        ('JCB', 'JCB'),
        ('MASTERCARD', 'MASTERCARD'),
        ('MBBANK', 'MBBANK'),
        ('MSBANK', 'MSBANK'),
        ('NAMABANK', 'NAMABANK'),
        ('NCB', 'NCB'),
        ('OCB', 'OCB'),
        ('OJB', 'OJB'),
        ('PVCOMBANK', 'PVCOMBANK'),
        ('SACOMBANK', 'SACOMBANK'),
        ('SAIGONBANK', 'SAIGONBANK'),
        ('SCB', 'SCB'),
        ('SHB', 'SHB'),
        ('TECHCOMBANK', 'TECHCOMBANK'),
        ('TPBANK', 'TPBANK'),
        ('UPI', 'UPI'),
        ('VIB', 'VIB'),
        ('VIETCAPITALBANK', 'VIETCAPITALBANK'),
        ('VIETCOMBANK', 'VIETCOMBANK'),
        ('VIETINBANK', 'VIETINBANK'),
        ('VISA', 'VISA'),
        ('VNMART', 'VNMART'),
        ('VNPAYQR', 'VNPAYQR'),
        ('VPBANK', 'VPBANK')
    )
