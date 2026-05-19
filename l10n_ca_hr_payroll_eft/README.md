# Canada - Payroll EFT (CPA Standard 005)

## Company setup (one time)

On the company form, open **Canadian Payroll EFT** and configure:
- **Bank EFT Format** (all major Canadian formats supported; default is **RBC**)
- **CPA Originator ID**, short/long originator names
- Originator bank routing (institution/transit/account) and destination data centre
- **EFT Bank Journal** and optional **Net Pay Clearing Account** (defaults to account **2380** if left empty)

## Employee setup

On each employee payroll settings, set:
- **Pay Method** (`Direct Deposit (EFT)`, `Paper Cheque`, `Cash`)
- If EFT: Institution / Transit / Account

Employees with non-EFT pay methods are skipped when generating EFT files.

## Payroll workflow

1. Confirm payroll batch (`hr.payslip.run`) to closed state.
2. Click **Generate EFT File**.
3. Choose settlement date and options (mark payslips paid, create bulk payment).
4. Download generated `.txt` CPA 005 file and upload to bank portal.
5. Payslips can be auto-set to **Paid**, and a bulk `account.payment` is posted against the bank journal and clearing account 2380.

## Bank format notes

Supported dialects:
- RBC Royal Bank (ACH 1464)
- TD Canada Trust (ACS 1464)
- BMO Bank of Montreal (Direct 1464)
- Scotiabank (ScotiaConnect 1464)
- CIBC (1464)
- National Bank of Canada (1464)
- Desjardins (AFT 1464)
- Generic CPA 005 (1464)

All formats use CPA Standard 005 fixed-width **1464-byte** records with format-specific overrides handled via bank-format dispatch.

## Production warning

Always validate your first generated file with your bank's published EFT/CPA 005 specification PDF before production use. Bank-side file rejection is the most common go-live issue.
