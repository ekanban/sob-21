import csv
import traceback
from datetime import date, datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
import copy

print(f"Started reading csv at {datetime.now()}")

with open (f"/Users/ekansh/Desktop/projects/summer_of_bitcoin_code_challenge/mempool.csv", newline='') as f:
    reader = csv.reader(f)
    mempool_txns = list(reader)

mempool_txns_dict = {}

print(f"started building mempool dict at: {datetime.now()}")

for txn in mempool_txns:

    txn_details = {}
    txn_details['fees'] = int(txn[1])
    txn_details['weight'] = int(txn[2])
    txn_details['parent_txids'] = []
    if txn[3] != '':
        txn_details['parent_txids'] = txn[3].split(';')

    mempool_txns_dict[txn[0]] = txn_details

original_txns_dict = copy.deepcopy(mempool_txns_dict)

test_dict = {}

def do_things(txn):
    if len(mempool_txns_dict[txn]['parent_txids']) != 0:
        parent_txns = mempool_txns_dict[txn]['parent_txids']
        all_parents = [] 
        total_txn_fees = mempool_txns_dict[txn]['fees'] 
        total_txn_weight = mempool_txns_dict[txn]['weight'] 
        while len(parent_txns) != 0:
            for parent_txn in parent_txns:
                all_parents.append(parent_txn)
                parent_txns.remove(parent_txn)
                total_txn_fees += original_txns_dict[parent_txn]['fees']
                total_txn_weight += original_txns_dict[parent_txn]['weight']
                parent_txns.extend(original_txns_dict[parent_txn]['parent_txids'])

        mempool_txns_dict[txn]['parent_txids'] = all_parents
        mempool_txns_dict[txn]['fees'] = total_txn_fees
        mempool_txns_dict[txn]['weight'] = total_txn_weight
    
    mempool_txns_dict[txn]['fee_rate'] = mempool_txns_dict[txn]['fees']/mempool_txns_dict[txn]['weight']
    print(f"{txn} = {datetime.now()}")
    test_dict[txn] = 'Done'
    print(f"Done: {len(test_dict)}")

started_at = datetime.now()
print("Operation started")

with ThreadPoolExecutor(max_workers=120) as executor:
    results = executor.map(do_things, mempool_txns_dict)

print("BIG DONE")
print(f"started building dict at: {started_at}")
print(f"started sort at: {datetime.now()}")

with open('result.json', 'w') as fp:
    json.dump(mempool_txns_dict, fp)

# sort mempool dictionary
sorted_mempool_dict = sorted(mempool_txns_dict.items(), key=lambda item: item[1]['fee_rate'], reverse=True)

included_txns = []
included_txns_dict = {}

max_weight = 4000000
total_weight = 0
total_fees = 0
print(f"started final inclusions at: {datetime.now()}")
for sorted_tx_id, sorted_txn in sorted_mempool_dict:
    if total_weight + sorted_txn['weight'] <= 4000000:
        txns_to_include = []
        if sorted_tx_id not in included_txns_dict:
            txns_to_include.append(sorted_tx_id)
            total_weight += sorted_txn['weight']
            total_fees += sorted_txn['fees']
            included_txns_dict[sorted_tx_id] = 'Included'
            for parent_txn in sorted_txn['parent_txids']:
                if parent_txn not in included_txns_dict:
                    txns_to_include.append(parent_txn)
                    included_txns_dict[parent_txn] = 'Included'
                else:
                    total_fees -= original_txns_dict[parent_txn]['fees']
                    total_weight -= original_txns_dict[parent_txn]['weight']

        txns_to_include.reverse()
        included_txns.extend(txns_to_include)
    else:
        break
print(f"all done at: {datetime.now()}")
print(f"total weight: {total_weight}")
print(f"total fees: {total_fees}")
print(f"total txns: {len(included_txns)}")
print(f"total txns: {len(included_txns_dict)}")


# return reversed included_txns <- this won't work I think
# remove weights and fees of parents who have already been included in the list
