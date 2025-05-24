import numpy as np
from data.tax_rate_table import rate_table


def estimate_retirement_tax(income, expense, ssn_earning, retirement_contribution, filing='single'):
    single_tax_rates, married_tax_rates = rate_table()
    std_deduction_married = 30000
    std_deduction_single = 15000
    add_withdrawal = max(0, (expense- income - ssn_earning))
    if filing == 'single':
        taxable_income = income + 0.85*ssn_earning + add_withdrawal - retirement_contribution - std_deduction_single
        tax_rates = single_tax_rates
    elif filing == 'married':
        taxable_income = income + 0.85*ssn_earning + add_withdrawal - retirement_contribution - std_deduction_married
        tax_rates = married_tax_rates
        tax_amt = 0
    if taxable_income > 0:
        for i, tax_rate in tax_rates.iterrows():
            if taxable_income >= tax_rate['To$']:
                tax_amt += tax_rate['rate']*0.01*(tax_rate['To$']-tax_rate['from$'])
                #print(tax_amt)
            else:
                tax_amt += tax_rate['rate']*0.01*(taxable_income-tax_rate['from$'])
                #print(tax_amt)
                break
        effective_tax_rate = int((tax_amt / (income+ssn_earning+add_withdrawal)*100))
    else:
        effective_tax_rate = 0
    return tax_amt
'''
def estimate_retirement_tax_rate(income, ssn_earning, total_expense, ssn_earning, filing='single'):
    # In retirement period, total expense is funded through SSN earning, dividends, bond income and equity sell.
    # So roughly you can consider Total income = total expense
    # SSN tax rule : no tax if adjusted gross income is less than 32K for married and 25K for single
    # Between 32K to 44K, 50% is taxed for married and between 25K to 34K for single, 50% is taxed
    # Above 44K for married, 85% of SSN income is taxed and above 34K for single, 85% is taxed.
    adjusted_gross_income = total_expense - ssn_earning*0.5
    if filing == 'single':
        if adjusted_gross_income <= 25000:
            eff_retirement_tax_rate = estimate_pre_retirement_tax_rate((total_expense-ssn_earning),0,filing=filing)
        elif 25000 < adjusted_gross_income <= 34000:
            eff_retirement_tax_rate = estimate_pre_retirement_tax_rate((total_expense - 0.5*ssn_earning), 0, filing=filing)
        else:
            eff_retirement_tax_rate = estimate_pre_retirement_tax_rate((total_expense - 0.15*ssn_earning), 0, filing=filing)
    elif filing == 'married':
        if adjusted_gross_income <= 32000:
            eff_retirement_tax_rate = estimate_pre_retirement_tax_rate((total_expense - ssn_earning), 0, filing=filing)
        elif 32000 < adjusted_gross_income <= 44000:
            eff_retirement_tax_rate = estimate_pre_retirement_tax_rate((total_expense - 0.5 * ssn_earning), 0,
                                                                       filing=filing)
        else:
            eff_retirement_tax_rate = estimate_pre_retirement_tax_rate((total_expense - 0.15 * ssn_earning), 0,
                                                                       filing=filing)

    return eff_retirement_tax_rate

amt = estimate_pre_retirement_tax_rate(1000, retirement_contribution=0, filing='married')
print(amt)
'''
#amt = estimate_retirement_tax(100000, 180000, 33000, 15000, filing='married')
#print(amt)