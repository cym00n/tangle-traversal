import json
import urllib2
import time

# All tx hashes
allTxs = set()
# All txs with values
fullTxs = set()

def makeRequest(command):
    stringified = json.dumps(command)

    headers = {'content-type': 'application/json'}

    request = urllib2.Request(url="http://localhost:14265", data=stringified, headers=headers)
    returnData = urllib2.urlopen(request).read()

    jsonData = json.loads(returnData)
    return jsonData


def getTotalValues():
    # All addresses with balances
    fullAddresses = []
    addressesSet = set()

    totalValue = 0
    totalAmount = 0
    ##
    ##  For all confirmed txs, get the total sum of sent txs per address
    ##
    for item in fullTxs:
        tx = json.loads(item)
        totalValue += int(tx['value'])

        if (int(tx['value']) > 0):
            totalAmount += int(tx['value'])

        addressesSet.add(tx['address'])



        found = False
        for address in fullAddresses:
            if address['address'] == tx['address']:
                found = True
                address['value'] += int(tx['value'])

        if not found:
            newAddress = {
                'address': tx['address'],
                'value': int(tx['value'])
            }
            fullAddresses.append(newAddress)

    print "Total Sum of Tokens transacted: ", totalAmount
    print "Tangle Transaction Balance (should be 0): ", totalValue

    with open('./genesis.json') as data:
        genesis = json.load(data)

    ##
    ##   Add the Genesis Balances to all the addresses
    ##
    genesisTotal = 0
    for account in genesis:
        genesisTotal += int(account[1])

        found = False
        for item in fullAddresses:
            if item['address'] == account[0]:
                found = True
                item['value'] += int(account[1])
                break

        if not found:
            newAddress = {
                'address': account[0],
                'value': int(account[1])
            }
            fullAddresses.append(newAddress)


    ##
    ##   Check if an account has a negative balance
    ##
    for address in fullAddresses:
        if address['value'] < 0:
            print "NEGATIVE!", address['address']
            print "VALUE: ", address['value']

    supposedTotal = (3 ** 33 - 1) / 2
    print "Addresses with balance:", len(fullAddresses)
    print "Total Amount of IOTA Tokens: ", genesisTotal
    print "Total equals supposed total (0 yes, >0 no): ", (genesisTotal - supposedTotal)
    fullAddresses[:] = (value for value in fullAddresses if value['value'] > 0)
    print "Unique # of Addresses:", len(addressesSet)


def traverse(txs):

    txs = txs
    traverse = True
    while (traverse):

        commandTrytes = {
            'command': 'getTrytes',
            'hashes': txs
        }

        allTrytes = makeRequest(commandTrytes)

        commandAnalyze = {
            'command': 'analyzeTransactions',
            'trytes': allTrytes['trytes']
        }

        allAnalyzed = makeRequest(commandAnalyze)

        currentSet = set()
        numTxs = len(allTxs)
        txList = []

        for tx in allAnalyzed['transactions']:
            if tx['hash'] in allTxs:
                fullTxs.add(json.dumps(tx))

            currentSet.add(tx['branchTransaction'])
            currentSet.add(tx['trunkTransaction'])

            currentNumTxs = len(allTxs)
            allTxs.add(tx['branchTransaction'])

            if len(allTxs) > currentNumTxs:
                txList.append(tx['branchTransaction'])

            currentNumTxs = len(allTxs)
            allTxs.add(tx['trunkTransaction'])

            if len(allTxs) > currentNumTxs:
                txList.append(tx['trunkTransaction'])

        if numTxs == len(allTxs):
            print "\nFinal Confirmed Txs: ", len(allTxs)
            getTotalValues()
            traverse = False
            return

        print '\n';
        print "Confirmed Txs: ", len(allTxs)

        txs = txList

def main():
    commandNodeInfo = {
        'command': 'getNodeInfo'
    }
    nodeInfo = makeRequest(commandNodeInfo)

    commandGetMilestone = {
        'command': 'getMilestone',
        'index': nodeInfo['milestoneIndex']
    }

    milestone = makeRequest(commandGetMilestone)

    tip = []
    tip.append(milestone['milestone'])

    allTxs.add(milestone['milestone'])

    traverse(tip)

if __name__ == '__main__':
    main()
