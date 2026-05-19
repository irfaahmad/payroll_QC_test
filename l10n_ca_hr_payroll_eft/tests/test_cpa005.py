# Part of MHC. See LICENSE file for full copyright and licensing details.

from __future__ import annotations

import importlib.util
import pathlib
from dataclasses import dataclass
from datetime import date


def _load_module():
    path = pathlib.Path(__file__).parent.parent / 'models' / 'cpa005.py'
    spec = importlib.util.spec_from_file_location('cpa005', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cpa005 = _load_module()


@dataclass
class Company:
    l10n_ca_eft_originator_id: str = '1234567890'
    l10n_ca_eft_data_centre: str = '00540'
    l10n_ca_eft_short_name: str = 'ACME PAYROLL'
    l10n_ca_eft_long_name: str = 'ACME PAYROLL INC'


@dataclass
class Employee:
    name: str
    l10n_ca_bank_institution: str = '003'
    l10n_ca_bank_transit: str = '12345'
    l10n_ca_bank_account: str = '987654321'


def _builder():
    builder_cls = cpa005.get_builder('rbc')
    return builder_cls(
        Company(),
        file_number=1,
        creation_date=date(2026, 5, 1),
        settlement_date=date(2026, 5, 15),
        currency='CAD',
    )


def test_record_lengths_are_1464_bytes():
    b = _builder()
    b.add_credit(Employee('Alice'), 100.00, 'SLIP-1')
    rows = b.build().decode('ascii').split(cpa005.CRLF)
    assert len(rows) == 3
    assert all(len(r) == cpa005.RECORD_LEN for r in rows)


def test_trailer_total_matches_credit_sum():
    b = _builder()
    b.add_credit(Employee('Alice'), 100.00, 'SLIP-1')
    b.add_credit(Employee('Bob'), 250.25, 'SLIP-2')
    trailer = b.build().decode('ascii').split(cpa005.CRLF)[-1]
    # total_cents starts at position 24 and is 14 chars in this builder layout
    assert int(trailer[24:38]) == 35025


def test_multi_record_batching_for_13_credits():
    b = _builder()
    for i in range(13):
        b.add_credit(Employee(f'Emp {i}'), 10.00 + i, f'SLIP-{i}')
    rows = b.build().decode('ascii').split(cpa005.CRLF)
    credit_rows = [r for r in rows if r.startswith('C')]
    assert len(credit_rows) == 3
