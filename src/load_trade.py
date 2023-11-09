from pydantic import ValidationError
from cdm_util import cdm_trade_from_file

print('loading trade from file system')
#trade              = cdm_trade_from_file('ird-ex01-vanilla-swap_4_3.json')
try:
    trade           = cdm_trade_from_file('LargeCDM.json')
    contractualProduct = trade.tradableProduct.product.contractualProduct
    economic_terms     = contractualProduct.economicTerms
except ValidationError as exc:
    print(exc)
    print(repr(exc.errors()[0]['type']))