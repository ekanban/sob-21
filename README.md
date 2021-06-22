# Summer Of Bitcoin

I've used an approach of maximizing fee rate (fees/weight) by keeping in mind that if a child txn is included in the block then it means 
that all of its parents will also have to be included in the block. Hence it makes sense to calculate fee rate for a txn by taking into 
account the total fees and total weight (i.e. include fees and weight of all parent txns too).

### Final Output

Total txns in block: 3263  
Total weight: 3992360  
Total fees: 5795436

### Note

I came across [this interesting paper](https://ieeexplore.ieee.org/abstract/document/8946174) regarding efficient miner strategies while researching for the solution. Readers
might find this interesting and I would love to try and implement this some day.
