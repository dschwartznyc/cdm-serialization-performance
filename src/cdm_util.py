import json
from pathlib import Path
from cdm.event.common.Trade import Trade

def cdm_trade_from_json (trade_json: str):
	json_dict = json.loads (trade_json)
	return Trade.parse_obj(json_dict['trade'])

def cdm_trade_from_file (file_name: str):
	json_str = Path(file_name).read_text()
	return cdm_trade_from_json (json_str)
