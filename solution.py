import csv
import traceback
from datetime import datetime, timedelta
import copy

with open (f"/Users/ekansh/Desktop/projects/summer_of_bitcoin_code_challenge/mempool.csv", newline='') as f:
    reader = csv.reader(f)
    mempool_txns = list(reader)

mempool_txns_dict = {}

for txn in mempool_txns:

    txn_details = {}
    txn_details['fees'] = int(txn[1])
    txn_details['weight'] = int(txn[2])
    txn_details['parent_txids'] = []
    if txn[3] != '':
        txn_details['parent_txids'] = txn[3].split(';')

    mempool_txns_dict[txn[0]] = txn_details

original_txns_dict = copy.deepcopy(mempool_txns_dict)

started_at = datetime.now()

for tx_id, txn in mempool_txns_dict.items():
    if len(txn['parent_txids']) != 0:
        parent_txns = txn['parent_txids']
        txns_in_family = []
        total_fees = txn['fees']
        total_weight = txn['weight']
        while len(parent_txns) != 0:
            for parent_txn in parent_txns:
                txns_in_family.append(parent_txn)
                parent_txns.remove(parent_txn)
                total_fees += original_txns_dict[parent_txn]['fees']
                total_weight += original_txns_dict[parent_txn]['weight']
                if len(original_txns_dict[parent_txn]['parent_txids']) != 0: # try using extend here instead
                    for xyz in original_txns_dict[parent_txn]['parent_txids']:
                        parent_txns.append(xyz)

        
        txn['parent_txids'] = txns_in_family
        txn['fees'] = total_fees
        txn['weight'] = total_weight
    
    txn['fee_rate'] = txn['fees']/txn['weight']
    print(f"{tx_id} = {txn['fee_rate']}")

print("BIG DONE")
print(started_at)
print(datetime.now)
# # sort mempool dictionary
# sorted_mempool_dict = sorted(mempool_txns_dict.items(), key=lambda item: item[1]['fee_rate'], reverse=True)
# for txn in sorted_mempool_dict:
#     print(txn)

