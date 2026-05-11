# v3 comparison — 20260511T233617Z

**Person-agent**: `entities/people/karlton-dennis`
**Query**: I own a small business as an S-corp making $400k/year and I'm tired of paying so much in taxes. My CPA only talks about 401(k) contributions. What 2-3 non-obvious strategies should I actually be using this year to cut my tax burden in half? Be specific.
**Model**: gpt-4o-mini

| runner | prompt_tok | completion_tok | elapsed_s | tool calls |
|---|---:|---:|---:|---:|
| bare | 70 | 588 | 8.82 | 0 |
| bare_search | 8114 | 804 | 18.21 | 4 |
| persona | 1381 | 430 | 9.0 | 0 |
| agentic | 9688 | 0 | 11.77 | 3 |

## bare

Reducing your tax burden as an S-corp owner requires a combination of strategies that may not be immediately obvious. Here are a few strategies to consider:

### 1. **Qualified Business Income (QBI) Deduction**
   - **What it is**: Under the Tax Cuts and Jobs Act, S-corp owners may qualify for a 20% deduction on qualified business income (QBI) from their business. This deduction can significantly reduce your taxable income.
   - **How to maximize it**: Ensure your business income qualifies for the deduction. If your taxable income exceeds certain thresholds ($170,050 for single filers or $340,100 for joint filers in 2023), the deduction may be limited based on W-2 wages paid or qualified property owned. Consider strategies to increase W-2 wages (e.g., paying yourself a reasonable salary) or investing in qualified property to maximize this deduction.

### 2. **Health Reimbursement Arrangements (HRAs)**
   - **What it is**: An HRA allows you to reimburse employees (including yourself as an owner-employee) for qualified medical expenses tax-free.
   - **How to implement it**: Set up an HRA and contribute funds to it. The contributions are tax-deductible for the business, and reimbursements for qualified medical expenses are tax-free to the employee. This can help reduce your taxable income while providing a valuable benefit to you and your employees.

### 3. **Retirement Plan Options Beyond 401(k)**
   - **What it is**: While your CPA has mentioned 401(k) contributions, consider other retirement plan options that may offer higher contribution limits and tax benefits.
   - **Specific plans**:
     - **SEP IRA**: Allows you to contribute up to 25% of your compensation or $66,000 (whichever is less) for 2023. This can be a significant deduction.
     - **Cash Balance Plan**: If you are looking to contribute even more, a cash balance plan allows for much larger contributions, especially beneficial for older business owners. Contributions can be in the hundreds of thousands, depending on your age and income.

### Additional Considerations
- **Accountable Plan**: If you are reimbursing yourself for business expenses (like travel, meals, or home office expenses), set up an accountable plan. This allows you to deduct these expenses without them being counted as taxable income to you.
- **Depreciation Strategies**: If you have significant assets, consider using bonus depreciation or Section 179 expensing to write off the cost of qualifying assets in the year they are purchased.

### Conclusion
It's essential to work closely with your CPA to implement these strategies effectively and ensure compliance with IRS regulations. Each of these strategies can help reduce your taxable income significantly, but the best approach will depend on your specific financial situation and goals.

---

## bare_search

**Tool calls:**
- `web_search(query='tax strategies for S-corp owners 2023', max_results=5)` → 2,365 chars
- `fetch_url(url='https://www.whitecoatinvestor.com/10-ways-to-slash-s-corp-taxes/')` → 12,031 chars
- `fetch_url(url='https://yolofskylaw.com/s-corp-tax-saving-strategies/')` → 9,763 chars
- `fetch_url(url='https://molentax.com/ten-proven-tax-strategies-for-saving-money-as-an-s-corp-owner/')` → 6,694 chars

To significantly reduce your tax burden as an S-corp owner making $400,000 a year, consider the following non-obvious strategies:

1. **Adjust Your Salary and Take Distributions**:
   - **Reduce Owner’s Wages**: You can lower your salary to the IRS's "reasonable compensation" level, which allows you to take the remaining profits as distributions that are not subject to self-employment taxes. This can save you thousands in payroll taxes. For instance, if your reasonable salary is determined to be $100,000, you can take the remaining $300,000 as distributions, which are not subject to payroll taxes. Just ensure you document how you arrived at your salary to avoid IRS scrutiny ([White Coat Investor](https://www.whitecoatinvestor.com/10-ways-to-slash-s-corp-taxes/)).

2. **Employ Your Children**:
   - **Hire Your Kids**: If you have children, you can hire them to work in your business. They can earn up to $12,950 (for 2023) without incurring federal income tax, and their wages are deductible for your S-corp. This strategy shifts income from your higher tax bracket to your children’s lower tax bracket. Ensure they perform legitimate work and document their hours and tasks ([Yolofsky Law](https://yolofskylaw.com/s-corp-tax-saving-strategies/)).

3. **Rent Your Home to Your S-Corp**:
   - **Utilize the Augusta Rule**: You can rent your home to your S-corp for up to 14 days a year without reporting the rental income. The S-corp can deduct the rental payments, which reduces its taxable income. Just ensure you charge a fair market rate and have a formal rental agreement. This can be particularly beneficial if you host business meetings at your home ([Molen Tax](https://molentax.com/ten-proven-tax-strategies-for-saving-money-as-an-s-corp-owner/)).

4. **Health Insurance Premiums**:
   - **Deduct Health Insurance Premiums**: If your S-corp pays for your health insurance premiums, you can deduct these as business expenses. This applies to you and your family, provided you own more than 2% of the S-corp. The premiums must be reported as wages on your W-2, but you can then deduct them on your personal tax return ([White Coat Investor](https://www.whitecoatinvestor.com/10-ways-to-slash-s-corp-taxes/)).

5. **Home Office Deduction**:
   - **Claim Home Office Expenses**: If you use part of your home exclusively for business, you can deduct related expenses. Your S-corp can reimburse you for these expenses, which are then not taxable to you. This includes a portion of your mortgage interest, utilities, and repairs ([Yolofsky Law](https://yolofskylaw.com/s-corp-tax-saving-strategies/)).

By implementing these strategies, you can effectively reduce your taxable income and save significantly on taxes. Always consult with a tax professional to ensure compliance and optimize your specific situation.

---

## persona

I completely understand your frustration with high taxes, especially as an S-corp owner. While 401(k) contributions are a great start, there are several non-obvious strategies you can implement to significantly reduce your tax burden. Here are a few specific strategies to consider:

1. **Cost Segregation Study**: If you own any real estate or have made significant improvements to your property, consider conducting a cost segregation study. This allows you to accelerate depreciation on certain components of your property, such as fixtures and improvements, which can lead to substantial tax savings. By breaking down the property into different categories, you can depreciate certain assets over a shorter period (5, 7, or 15 years instead of the standard 27.5 or 39 years), thereby increasing your deductions and reducing your taxable income.

2. **Health Savings Account (HSA)**: If you have a high-deductible health plan (HDHP), you can contribute to an HSA. Contributions to an HSA are tax-deductible, and the funds grow tax-free. Additionally, withdrawals for qualified medical expenses are also tax-free. For 2023, you can contribute up to $3,850 for individual coverage or $7,750 for family coverage, plus an additional $1,000 if you're over 55. This is a great way to reduce your taxable income while also saving for future medical expenses.

3. **Entity Structure Optimization**: While you’re currently operating as an S-corp, it may be worth evaluating whether your current structure is the most tax-efficient for your situation. Depending on your specific circumstances, converting to a different entity type, such as a partnership or LLC, or even considering a C-corp for certain income levels, might provide additional tax benefits. For example, C-corps are taxed at a lower rate on retained earnings, which could be beneficial if you plan to reinvest profits back into the business.

Implementing these strategies can help you significantly reduce your tax burden. However, I recommend consulting with a tax strategist who can tailor these strategies to your specific situation and ensure compliance with tax laws.

---

## agentic

**Tool calls:**
- `read_wiki_file(name='polaristaxandaccounting-com--tax-reduction-strategies-small-business.md')` → 9,136 chars
- `read_wiki_file(name='federaltaxcredits-org--how-to-reduce-business-taxes.md')` → 12,031 chars
- `read_wiki_file(name='turbotax-intuit-com--tax-tips-self-employment-taxes-7-ways-small-business-owners-can-reduce-their-tax.md')` → 12,031 chars

To significantly reduce your tax burden as an S-Corp making $400k/year, consider implementing the following non-obvious strategies:

1. **Accelerate Expenses**:
   If your business operates on a cash basis, you can reduce your taxable income by accelerating deductible expenses into the current year. This means prepaying expenses like rent, insurance, or supplies that you would incur anyway. The IRS allows this under specific guidelines, including the “12-month rule” for prepaid expenses. By planning ahead and timing your expenses strategically, you can smooth your cash flow and align deductions with higher-income years, effectively lowering your tax bill for the current year. 

2. **The Augusta Rule**:
   This lesser-known strategy allows you to rent your home to your business for up to 14 days per year without the rental income being taxable. Under Internal Revenue Code §280A(g), your business can deduct the rental expense, while you do not have to report that income on your personal tax return. This can be particularly useful for hosting company meetings or client gatherings at your home. Just ensure you document the fair rental value and keep proper records of the meetings held.

3. **Cost Segregation Studies**:
   If your business owns real estate, consider conducting a cost segregation study. This strategy allows you to reclassify building components into shorter depreciation schedules, enabling you to accelerate deductions. For instance, elements like fixtures and certain systems may qualify for faster depreciation, significantly reducing your taxable income in the early years of ownership. A professional cost segregation study can uncover substantial immediate tax deductions that can improve your cash flow and free up capital for reinvestment.

Implementing these strategies can help you cut your tax burden significantly while remaining compliant with tax laws. It's advisable to work closely with a tax professional to ensure proper execution and documentation for these strategies.

---
