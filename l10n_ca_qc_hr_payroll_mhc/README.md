\# Canada — Quebec Payroll



\*\*Complete payroll module for Quebec employers — Compliant with Revenu Québec and CRA 2026\*\*



| | |

|---|---|

| \*\*Author\*\* | MapleHorn Consulting Inc. |

| \*\*License\*\* | OPL-1 (Odoo Proprietary License v1.0) |

| \*\*Version\*\* | 18.0 \& 19.0 |

| \*\*Country\*\* | Canada — Quebec only |

| \*\*Contact\*\* | \[Info@maplehornconsulting.com](mailto:Info@maplehornconsulting.com) |

| \*\*Website\*\* | \[www.maplehornconsulting.com](https://www.maplehornconsulting.com) |



\---



\## Overview



The \*\*Canada — Quebec Payroll\*\* module provides a comprehensive set of salary rules, annual tax declarations, and payroll configuration tools designed \*\*exclusively for the province of Quebec\*\*. It integrates natively with Odoo's `hr\_payroll` module and includes 2026 rates from Revenu Québec and the Canada Revenue Agency (CRA).



\---



\## Key Features



\### 💰 Contributions and Premiums

\- \*\*QPP / QPP2\*\* — Quebec Pension Plan (replaces CPP)

\- \*\*QPIP\*\* — Quebec Parental Insurance Plan

\- \*\*EI\*\* — Employment Insurance at Quebec reduced rate

\- \*\*Employer contributions\*\*: QPP, QPP2, QPIP, EI, CNESST, HSF, CNT

\- Year-to-date accumulation and annual maximums enforced automatically



\### 🧾 Income Taxes

\- \*\*Federal income tax\*\* with 16.5% Quebec abatement

\- \*\*Quebec provincial income tax\*\* — 4 tax brackets

\- \*\*Federal TD1\*\* claim codes (Code 1 to 10, X, 0)

\- \*\*Quebec TP-1015.3\*\* claim codes (Code A to J, X, 0)

\- Additional federal and provincial deductions per period



\### 📄 Pre-Tax Deductions

\- \*\*RRSP\*\* — Registered Retirement Savings Plan

\- \*\*RPP\*\* — Registered Pension Plan

\- \*\*DPSP\*\* — Deferred Profit Sharing Plan

\- \*\*Union Dues\*\*



\### 🏖️ Vacation and Benefits

\- Automatic \*\*vacation pay accrual\*\* (4%, 6%, or 8%) based on years of service

\- Vacation pay payout via salary input

\- \*\*Taxable benefits\*\*: vehicle, group insurance, housing, stock options

\- Retroactive pay, termination pay, severance pay

\- Statutory holiday pay



\### ⚖️ Garnishments and Court Orders

\- Wage garnishments / court-ordered deductions

\- Types: child support, alimony/spousal support, tax debt, other court order

\- Priority, fixed amount or percentage, exempt amount

\- Remaining balance tracking and automatic deactivation



\### 📊 Annual Tax Reporting

\- \*\*RL-1\*\* — Slips and summary

\- \*\*RL-2\*\* — Slips and summary

\- \*\*T4\*\* — Slips and summary with XML export (CRA T619 format)

\- \*\*Record of Employment (ROE)\*\* — with XML export (Service Canada ROE Web format)

\- \*\*Remittance Reports\*\* (TPZ-1015.R.14 style)



\### 🌐 Bilingual Pay Stubs

\- Pay stub templates in \*\*English and French\*\*

\- \*\*Bill 96\*\* compliance (Charter of the French Language)



\### ⚙️ Pay Frequencies

\- Weekly (52 periods)

\- Bi-Weekly (26 periods)

\- Semi-Monthly (24 periods)

\- Monthly (12 periods)



\---



\## 29 Salary Rules



Complete pay structure: \*\*"Quebec Employee Salary"\*\*



| Name | Code | Category |

|---|---|---|

| Basic Salary | BASIC\_QC | Allowance |

| Retroactive Pay | RETRO\_QC | Allowance |

| Termination Pay | TERM\_PAY\_QC | Allowance |

| Severance Pay | SEVERANCE\_QC | Allowance |

| Statutory Holiday Pay | STAT\_HOL\_QC | Allowance |

| Taxable Benefits | TAXABLE\_BENEFITS\_QC | Allowance |

| Stock Option Taxable Benefit | STOCK\_OPT\_QC | Allowance |

| \*\*Gross Salary\*\* | \*\*GROSS\_QC\*\* | \*\*Taxable Salary\*\* |

| RPP (Registered Pension Plan) | RPP\_QC | Deduction |

| DPSP (Deferred Profit Sharing Plan) | DPSP\_QC | Deduction |

| Vacation Pay Payout | VAC\_PAYOUT\_QC | Allowance |

| RRSP Deduction | RRSP\_QC | Deduction |

| Union Dues | UNION\_QC | Deduction |

| QPP Employee Contribution | QPP\_EE | QPP |

| QPP2 Employee Contribution | QPP2\_EE | QPP |

| QPIP Employee Premium | QPIP\_EE | QPIP |

| EI Employee Premium (Quebec) | EI\_EE\_QC | EI (Quebec) |

| Federal Income Tax | FED\_TAX\_QC | Federal Tax |

| Quebec Provincial Income Tax | PROV\_TAX\_QC | Quebec Provincial Tax |

| Garnishment / Court-Ordered Deduction | GARNISH\_QC | Deduction |

| \*\*Net Salary\*\* | \*\*NET\_QC\*\* | \*\*Net\*\* |

| QPP Employer Contribution | QPP\_ER | Employer Contributions |

| QPP2 Employer Contribution | QPP2\_ER | Employer Contributions |

| QPIP Employer Premium | QPIP\_ER | Employer Contributions |

| EI Employer Premium (Quebec) | EI\_ER\_QC | Employer Contributions |

| CNESST Employer Contribution | CNESST\_ER | Employer Contributions |

| HSF Employer Contribution (Health Services Fund) | HSF\_ER | Employer Contributions |

| CNT Employer Contribution (Labour Standards) | CNT\_ER | Employer Contributions |

| Vacation Pay Accrual (Employer) | VAC\_ACCRUAL\_QC | Employer Contributions |



\---



\## 2026 Rates and Parameters



\### Contributions



| Parameter | 2026 Value |

|---|---|

| QPP — Employee Rate | 6.30% |

| QPP — YMPE | $74,600 |

| QPP — Basic Exemption | $3,500 |

| QPP — Max Employee Contribution | $4,479.30 |

| QPP2 — Rate | 4.00% |

| QPP2 — Ceiling (YAMPE) | $85,000 |

| QPP2 — Max Contribution | $416.00 |

| QPIP — Employee Rate | 0.430% |

| QPIP — Employer Rate | 0.602% |

| QPIP — Max Insurable Earnings | $103,000 |

| EI — Employee Rate (QC Reduced) | 1.30% |

| EI — Max Insurable Earnings | $68,900 |

| EI — Max Employee Premium | $895.70 |

| EI — Employer Multiplier | 1.4× |



\### Employer Contributions



| Parameter | 2026 Value |

|---|---|

| CNESST — Default Rate | 1.65% |

| HSF (Health Services Fund) — Rate | 1.65% |

| CNT (Labour Standards) — Rate | 0.07% |



\### Federal Tax Brackets



| Taxable Income | Rate |

|---|---|

| Up to $58,523 | 14% |

| $58,523 — $117,045 | 20.5% |

| $117,045 — $181,440 | 26% |

| $181,440 — $258,482 | 29% |

| Over $258,482 | 33% |

| Basic Personal Amount (BPA) | $16,452 |

| BPA Minimum (high income) | $14,829 |



\### Quebec Provincial Tax Brackets



| Taxable Income | Rate |

|---|---|

| Up to $54,345 | 14% |

| $54,345 — $108,680 | 19% |

| $108,680 — $132,245 | 24% |

| Over $132,245 | 25.75% |

| Basic Personal Amount | $18,952 |



\---



\## Screenshots



\### Payslip Computation

Full calculation including all employee and employer contributions, federal and provincial taxes, and net salary.



!\[Payslip Computation](static/description/Screenshot\_1.png)



\### Employee Record — Payroll Tab

Contract with "Quebec Employee" pay category, wage type, working hours, and employer costs.



!\[Employee Payroll Tab](static/description/Screenshot\_7.png)



\### Employee Record — Quebec Payroll Tab

Social Insurance Number (SIN), federal TD1 claim code, vacation pay accrual, and garnishments directly on the employee form.



!\[Employee Quebec Payroll Tab](static/description/Screenshot\_6.png)



\### Quebec Contract Settings

List view of contract versions with pay frequency, TD1 / TP-1015.3 claim codes, and QPP, EI, QPIP exemptions.



!\[Quebec Contract Settings](static/description/Screenshot\_8.png)



\### Vacation Pay Accrual

Automatic rate based on years of service: 4% (< 3 years), 6% (3–4 years), or 8% (5+ years).



!\[Vacation Pay Accrual](static/description/Screenshot\_9.png)



\### Vacation Pay Accrual — Rate Selection

Accrual rate selection compliant with Quebec Labour Standards Act.



!\[Vacation Accrual Rates](static/description/Screenshot\_4.png)



\### Garnishments and Court Orders

Garnishment types: child support, alimony/spousal support, tax debt, other court order. Fixed amount or percentage, exempt amount, priority, and balance tracking.



!\[Garnishment Form](static/description/Screenshot\_10.png)



\### Annual Tax Reporting Menu

RL-1, RL-2, T4, ROE, and remittance reports accessible from a single menu.



!\[Annual Tax Reporting Menu](static/description/Screenshot\_2.png)



\### Payroll Configuration Menu

Vacation pay accrual, garnishments, and Quebec contract settings.



!\[Payroll Configuration Menu](static/description/Screenshot\_3.png)



\---



\## Installation



\### Dependencies



| Module | Description |

|---|---|

| `hr\_payroll` | Odoo Enterprise Payroll module |

| `hr\_work\_entry\_holidays` | Work Entries and Time Off |

| `hr\_payroll\_holidays` | Payroll and Time Off |



\### Compatibility



\- \*\*Odoo Version\*\*: 18.0 Enterprise

\- \*\*Country\*\*: Canada

\- \*\*Province\*\*: Quebec only



\### Steps



1\. Place the `l10n\_ca\_qc\_hr\_payroll\_mhc` folder in your Odoo addons directory.

2\. Update the apps list: \*\*Settings → Apps → Update Apps List\*\*.

3\. Search for \*\*"Quebec Payroll"\*\* and click \*\*Install\*\*.

4\. Ensure your company country is set to \*\*Canada\*\*.



\---



\## Configuration



1\. \*\*Employee Contract\*\*: Set the pay category to \*\*"Quebec Employee"\*\* on the employee's contract (Payroll tab).

2\. \*\*Quebec Payroll Tab\*\*: Configure the employee's SIN, TD1 claim code, vacation pay accrual, and garnishments on the \*\*Quebec Payroll\*\* tab.

3\. \*\*Contract Settings\*\*: Review pay frequency, TD1/TP-1015.3 claim codes, and exemptions under \*\*Payroll Configuration → Quebec Contract Settings\*\*.

4\. \*\*Salary Rules\*\*: All 29 rules are installed automatically under the \*\*"Quebec Employee Salary"\*\* pay structure.



\---



\## License



This module is licensed under the \*\*OPL-1 (Odoo Proprietary License v1.0)\*\*.



\- Full use of this module requires a valid Odoo Enterprise instance.

\- Redistribution is not permitted without the written consent of the author.

\- See the \[OPL-1 License](https://www.odoo.com/documentation/18.0/legal/licenses.html#odoo-apps) for full terms.



\---



\## Support



\*\*MapleHorn Consulting Inc.\*\*



\- 🌐 \[www.maplehornconsulting.com](https://www.maplehornconsulting.com)

\- 📧 \[Info@maplehornconsulting.com](mailto:Info@maplehornconsulting.com)

