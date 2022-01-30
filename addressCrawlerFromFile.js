import transactions from 'file://C:/Users/rafavrech/Downloads/bkp/transactions.js';
import transactions1 from 'file://C:/Users/rafavrech/Downloads/bkp/transactions1.js';
import transactions2 from 'file://C:/Users/rafavrech/Downloads/bkp/transactions2.js';
import transactions3 from 'file://C:/Users/rafavrech/Downloads/bkp/transactions3.js';
import transactions4 from 'file://C:/Users/rafavrech/Downloads/bkp/transactions4.js';
import transactions5 from 'file://C:/Users/rafavrech/Downloads/bkp/transactions5.js';


// { "pagador": [""] "recebedor": [""], "signature": "", "value":, "hash": "" }

const allTransactionsArray = [...transactions, ...transactions1, ...transactions2, ...transactions3, ...transactions4, ...transactions5];

const allAddressesMap = new Map();

allTransactionsArray.forEach(transaction => {
    const signatureStart = transaction.signature.substr(7, 65);
    if (allAddressesMap.get(signatureStart)) {
        allAddressesMap.get(signatureStart).push(transaction)
    } else {
        allAddressesMap.set(signatureStart, transaction)
    }
})

console.log('acabou')