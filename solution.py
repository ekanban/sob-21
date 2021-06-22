import csv
from concurrent.futures import ThreadPoolExecutor
import copy
import json

###############################
##### GLOBAL VARIABLES ########
###############################
mempool_txns_dict = {}
mempool_txns_dict_copy = {}

# read the mempool csv
def read_mempool():
    with open (f"./mempool.csv", newline='') as f:
        reader = csv.reader(f)
        mempool_txns = list(reader)
    
    return mempool_txns


# create a dictionary of the txns in the mempool for O[1] access
def build_mempool_dictionary(mempool_txns):
    global mempool_txns_dict
    global mempool_txns_dict_copy

    for txn in mempool_txns:
        txn_details = {}
        try:
            txn_details['fees'] = int(txn[1])
            txn_details['weight'] = int(txn[2])
            txn_details['parent_txids'] = []
            if txn[3] != '':
                txn_details['parent_txids'] = txn[3].split(';')

            mempool_txns_dict[txn[0]] = txn_details
        except:
            continue # first line of csv may be string headers
    
    # create a copy of the mempool txns dict to access original data
    mempool_txns_dict_copy = copy.deepcopy(mempool_txns_dict)


''' if a child txn is included in the list, then it means all its parent txns have to be included too.
Hence it makes sense to get all the parents of a child txn and calculate their total fees and weight
and calculate the fee rate on the total fees and weight. The following function does precisely this
'''
def calculate_total_fee_rate(txn):
    if len(mempool_txns_dict[txn]['parent_txids']) != 0:
        parent_txns = mempool_txns_dict[txn]['parent_txids']
        all_parents = [] 
        total_txn_fees = mempool_txns_dict[txn]['fees'] 
        total_txn_weight = mempool_txns_dict[txn]['weight'] 
        while len(parent_txns) != 0:
            for parent_txn in parent_txns:
                all_parents.append(parent_txn)
                parent_txns.remove(parent_txn)
                total_txn_fees += mempool_txns_dict_copy[parent_txn]['fees']
                total_txn_weight += mempool_txns_dict_copy[parent_txn]['weight']
                for parent_tx in mempool_txns_dict_copy[parent_txn]['parent_txids']:
                    if parent_tx not in parent_txns: # to ensure parent txns aren't duplicated in cyclic txns
                        parent_txns.append(parent_tx)

        mempool_txns_dict[txn]['parent_txids'] = all_parents
        mempool_txns_dict[txn]['fees'] = total_txn_fees
        mempool_txns_dict[txn]['weight'] = total_txn_weight
    
    mempool_txns_dict[txn]['fee_rate'] = mempool_txns_dict[txn]['fees']/mempool_txns_dict[txn]['weight']


def build_final_list_of_txns():
    # sort mempool dictionary in descending order of fee rate
    sorted_mempool_dict = sorted(mempool_txns_dict.items(), key=lambda item: item[1]['fee_rate'], reverse=True)

    included_txns = [] # this is the final list that has to be returned
    included_txns_dict = {} # a dictionary to track which txns have already been included in the list

    max_weight = 4000000
    total_weight = 0
    total_fees = 0

    for sorted_tx_id, sorted_txn in sorted_mempool_dict:
        if total_weight + sorted_txn['weight'] <= max_weight:
            txns_to_include = []
            if sorted_tx_id not in included_txns_dict:
                txns_to_include.append(sorted_tx_id)
                total_weight += sorted_txn['weight']
                total_fees += sorted_txn['fees']
                included_txns_dict[sorted_tx_id] = 'Included'

                ''' if parent txns for a txn have not been included in the list, we include them. We
                don't need to worry about adding the parent txns fees and weight since they'll be included in the child txn.
                If they have already been included in the list, then we need to subtract
                their fees and weight since the newly added child txn's fees and weight will already 
                include the parents' fees and weight:
                '''
                for parent_txn in sorted_txn['parent_txids']:
                    if parent_txn not in included_txns_dict:
                        txns_to_include.append(parent_txn)
                        included_txns_dict[parent_txn] = 'Included'

                    else:
                        total_fees -= mempool_txns_dict_copy[parent_txn]['fees']
                        total_weight -= mempool_txns_dict_copy[parent_txn]['weight']

            txns_to_include.reverse() # to ensure that parents are included before children in the final list
            included_txns.extend(txns_to_include)
        else:
            break

    print(f"total weight: {total_weight}")
    print(f"total fees: {total_fees}")
    print(f"total txns: {len(included_txns)}")

    return included_txns

def main():

    mempool_txns = read_mempool()
    build_mempool_dictionary(mempool_txns)

    # Using multithreaded code to speed things up
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(calculate_total_fee_rate, mempool_txns_dict)
    
    # with open('result.json', 'w') as fp:
    #     json.dump(mempool_txns_dict, fp)

    final_txns = build_final_list_of_txns()
    block_file = open("block.txt", "w")
    for txn in final_txns:
        block_file.write(txn + "\n")
    block_file.close()

main()
