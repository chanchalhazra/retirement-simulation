import numpy as np
from data.tax_rate_table import rate_table


def estimate_retirement_tax(income, expense, ssn_earning, retirement_contribution, filing='single', state_tax_rate=0):
    single_tax_rates, married_tax_rates = rate_table()
    std_deduction_married = 30000.0
    std_deduction_single = 15000.0
    add_withdrawal = max(0.0, (expense - income - ssn_earning))
    if filing == 'single':
        #taxable_income = income + 0.85*ssn_earning + add_withdrawal - retirement_contribution - std_deduction_single
        taxable_income = income + 0.85 * ssn_earning + add_withdrawal - retirement_contribution - std_deduction_single
        tax_rates = single_tax_rates
    elif filing == 'married':
        #taxable_income = income + 0.85*ssn_earning + add_withdrawal - retirement_contribution - std_deduction_married
        taxable_income = income + 0.85 * ssn_earning + add_withdrawal - retirement_contribution - std_deduction_married
        tax_rates = married_tax_rates
    tax_amt = 0
    state_tax_amt = taxable_income*state_tax_rate*0.01
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
    return tax_amt + state_tax_amt
