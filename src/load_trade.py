from cdm_util import cdm_trade_from_file

print('loading trade from file system')
#trade              = cdm_trade_from_file('ird-ex01-vanilla-swap_4_3.json')
trade              = cdm_trade_from_file('LargeCDM.json')

contractualProduct = trade.tradableProduct.product.contractualProduct
economic_terms     = contractualProduct.economicTerms
if (contractualProduct.productTaxonomy[0].productQualifier != 'InterestRate_IRSwap_FixedFloat'):
	print('Not InterestRate_IRSwap_FixedFloat')
elif (len(economic_terms.payout.interestRatePayout) != 2):
	print('Not a two legged swap')
else:
	float_idx          = 0 if (economic_terms.payout.interestRatePayout[0].rateSpecification.fixedRate == None) else 1
	fixed_idx          = 1 if (float_idx == 0) else 1
	float_payout       = economic_terms.payout.interestRatePayout[float_idx]
	fixed_payout       = economic_terms.payout.interestRatePayout[fixed_idx]
	float_pq           = trade.tradableProduct.tradeLot[0].priceQuantity[float_idx]
	fixed_pq           = trade.tradableProduct.tradeLot[0].priceQuantity[fixed_idx]
	print('effective date: ' + str(float_payout.calculationPeriodDates.effectiveDate.adjustableDate.unadjustedDate))
	print('termination date: ' + str(float_payout.calculationPeriodDates.terminationDate.adjustableDate.unadjustedDate))
