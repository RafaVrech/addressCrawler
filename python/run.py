import blockcypher


address = blockcypher.get_address_full('1BTCorgHwCg6u2YSAWKgS17qUad6kHmtQW')

if(address['balance'] > 0):
  print ('balance: ' + str(address['balance']))
  
  for transaction in address['txs']:
    if(transaction['input']['addresses'])
  
