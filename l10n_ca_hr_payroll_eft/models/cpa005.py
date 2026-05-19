# Part of MHC. See LICENSE file for full copyright and licensing details.
"""CPA Standard 005 EFT file builder.

References:
- Payments Canada Rule F1 (Standard 005), 1464-byte fixed-width ASCII.
- Bank-specific specs (RBC ACH, TD ACS, BMO Direct, Scotia ScotiaConnect,
  CIBC, NBC, Desjardins AFT) for filler/sundry overrides.

Record types used:
  A — File header        (1 per file)
  C — Credit detail      (1..N records, up to 6 transactions per record)
  Z — File trailer       (1 per file)

Transaction code 200 = payroll deposit (Type C credit).
"""

from datetime import date

CRLF = '\r\n'
RECORD_LEN = 1464


def julian(d: date) -> str:
    """Return CPA julian date 0YYDDD (6 digits)."""
    return f"0{d:%y}{d.timetuple().tm_yday:03d}"


def alpha(v, n: int) -> str:
    return (v or '')[:n].ljust(n)


def num(v, n: int) -> str:
    return str(int(v or 0)).rjust(n, '0')


class CPA005Builder:
    """Build a CPA 005 EFT file. Subclass per bank for dialect overrides."""

    BANK_FORMAT = 'generic'
    DIALECT = {
        'originator_id_len': 10,
        'header_filler': 1406,
        'trailer_filler': 1396,
        'sundry': '',
        'sequence_scope': 'file',
    }

    def __init__(self, company, file_number, creation_date, settlement_date, currency='CAD'):
        self.company = company
        self.file_number = file_number
        self.creation_date = creation_date
        self.settlement_date = settlement_date
        self.currency = currency
        self._records = []
        self._txn_count = 0
        self._total_cents = 0

    def add_credit(self, employee, amount_cad, cross_reference):
        cents = int(round(amount_cad * 100))
        self._total_cents += cents
        self._txn_count += 1
        self._records.append(('C', employee, cents, cross_reference))

    def build(self) -> bytes:
        out = [self._header()]
        credits = [r for r in self._records if r[0] == 'C']
        seq = self._sequence_start()
        for i in range(0, len(credits), 6):
            chunk = credits[i:i + 6]
            out.append(self._credit_record(seq, chunk))
            seq += 1
        out.append(self._trailer(seq))
        for rec in out:
            assert len(rec) == RECORD_LEN, f'record length {len(rec)} != {RECORD_LEN}'
        return CRLF.join(out).encode('ascii')

    def _sequence_start(self):
        if self.DIALECT.get('sequence_scope') == 'global':
            return ((int(self.file_number) - 1) * 100000) + 1
        return 1

    def _originator_id(self):
        return alpha(self.company.l10n_ca_eft_originator_id, self.DIALECT.get('originator_id_len', 10))

    def _header(self) -> str:
        c = self.company
        rec = (
            'A'
            + num(1, 9)
            + self._originator_id()
            + num(self.file_number, 4)
            + julian(self.creation_date)
            + alpha(c.l10n_ca_eft_data_centre or '', 5)
            + alpha(self.currency, 3)
            + ' ' * self.DIALECT.get('header_filler', 1406)
        )
        return rec[:RECORD_LEN].ljust(RECORD_LEN)

    def _credit_record(self, seq, chunk) -> str:
        head = (
            'C'
            + num(seq, 9)
            + self._originator_id()
            + num(self.file_number, 4)
        )
        body = ''.join(self._txn_block(emp, cents, xref) for (_t, emp, cents, xref) in chunk)
        body = body.ljust(240 * 6)
        rec = head + body
        return rec[:RECORD_LEN].ljust(RECORD_LEN)

    def _txn_block(self, emp, cents, xref) -> str:
        c = self.company
        sundry = alpha(self.DIALECT.get('sundry', ''), 15)
        return (
            '200'
            + num(cents, 10)
            + julian(self.settlement_date)
            + num(emp.l10n_ca_bank_institution, 4)
            + num(emp.l10n_ca_bank_transit, 5)
            + alpha(emp.l10n_ca_bank_account, 12)
            + num(0, 22)
            + alpha(c.l10n_ca_eft_short_name, 15)
            + alpha((emp.name or '').upper(), 30)
            + alpha(c.l10n_ca_eft_long_name, 30)
            + self._originator_id()
            + alpha(xref, 19)
            + num(0, 9)
            + num(0, 5)
            + alpha('', 12)
            + sundry
            + alpha('', 22)
            + alpha('', 2)
        )[:240].ljust(240)

    def _trailer(self, _last_seq) -> str:
        rec = (
            'Z'
            + num(99999999, 9)
            + self._originator_id()
            + num(self.file_number, 4)
            + num(self._total_cents, 14)
            + num(self._txn_count, 8)
            + num(0, 14)
            + num(0, 8)
            + ' ' * self.DIALECT.get('trailer_filler', 1396)
        )
        return rec[:RECORD_LEN].ljust(RECORD_LEN)


class RBCBuilder(CPA005Builder):
    BANK_FORMAT = 'rbc'


class TDBuilder(CPA005Builder):
    BANK_FORMAT = 'td'


class BMOBuilder(CPA005Builder):
    BANK_FORMAT = 'bmo'


class ScotiaBuilder(CPA005Builder):
    BANK_FORMAT = 'scotia'
    DIALECT = {**CPA005Builder.DIALECT, 'sundry': 'SCOTIA'}


class CIBCBuilder(CPA005Builder):
    BANK_FORMAT = 'cibc'


class NBCBuilder(CPA005Builder):
    BANK_FORMAT = 'nbc'


class DesjardinsBuilder(CPA005Builder):
    BANK_FORMAT = 'desjardins'
    DIALECT = {**CPA005Builder.DIALECT, 'sequence_scope': 'global'}


class GenericBuilder(CPA005Builder):
    BANK_FORMAT = 'generic'


BUILDER_REGISTRY = {
    'rbc': RBCBuilder,
    'td': TDBuilder,
    'bmo': BMOBuilder,
    'scotia': ScotiaBuilder,
    'cibc': CIBCBuilder,
    'nbc': NBCBuilder,
    'desjardins': DesjardinsBuilder,
    'generic': GenericBuilder,
}


def get_builder(bank_format):
    return BUILDER_REGISTRY.get(bank_format, GenericBuilder)
