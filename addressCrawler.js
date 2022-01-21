import axios from 'axios';
import axiosRetry from 'axios-retry';
import addresses from './addresses.js';

axiosRetry(axios, {
    retries: 999999, // number of retries
    retryDelay: (retryCount) => {
        console.log(`Retry attempt: ${retryCount}`);
        return 500; // time interval between retries
    }
});

const runEmptyWallets = true;
const globalAddress = '1Pq6Ygv3kdMVX2TdNhUSPadxaShiGJUAoS';

var balanceUrl = `https://chain.so/api/v2/get_address_balance/BTC/${globalAddress}`;
var txUrl = `https://chain.so/api/v2/get_tx_spent/BTC/${globalAddress}`;
var balance = 0;
var currentNoTransactions = 0;
var noTransactions = 0;
var i;

for (i in addresses) {
    console.log(`[${addresses[i]}] ----${i}/${addresses.length}----> Starting`);
    balanceUrl = `https://chain.so/api/v2/get_address_balance/BTC/${addresses[i]}`;
    txUrl = `https://chain.so/api/v2/get_tx_spent/BTC/${addresses[i]}`;
    noTransactions = await getNoOfTransactions();
    currentNoTransactions = 0;

    await checkAddress();
    console.log(`[${addresses[i]}] Finished <----------`);
}

async function checkAddress() {
    await axios.get(balanceUrl).then(async balanceResponse => {
        balance = balanceResponse.data.data.confirmed_balance;
        console.log(`[${addresses[i]}] BALANCE  \t\t \t\t${balance}`);

        if (runEmptyWallets || balance > 0.0003) {
            const transactions = await gatherAllTransactions();
            console.log(`[${addresses[i]}] TRANSACTIONS_NO \t\t \t\t${transactions.length}`);

            await checkTransactions(transactions);
        }
    }).catch(err => {
        console.log(`
        Error checking address: ${err.message}
        Call response was:
        ${transactionResponse.data}
        `);
    })
}

async function gatherAllTransactions(from) {
    return await axios.get(from ? `${txUrl}/${from}` : txUrl)
        .then(async transactionResponse => {
            if (transactionResponse.data.data.txs.length == 0)
                return transactionResponse.data.data.txs;

            currentNoTransactions += transactionResponse.data.data.txs.length;
            printProgress(`[${addresses[i]}] +${transactionResponse.data.data.txs.length} transactions (${currentNoTransactions}/${noTransactions})`);

            const lastTxId = transactionResponse.data.data.txs.at(-1).txid;
            const furtherTransactions = await gatherAllTransactions(lastTxId);
            return [...furtherTransactions, ...transactionResponse.data.data.txs]
        })
        .catch(err => {
            console.error(`
            Error checking transactions: ${err.message}
            Call response was:
            ${transactionResponse.data}
            `);
        });
}

async function checkTransactions(transactions) {
    const transactionMap = mapTransactions(transactions);
    searchForDuplicates(transactionMap);
}

function mapTransactions(transactions) {
    var transactionMap = {};
    transactions.forEach(splitTransaction => {
        var mapEntry = transactionMap[splitTransaction.txid] || {};
        if (splitTransaction.witness)
            if (mapEntry.witnesses) {
                mapEntry.witnesses.push(splitTransaction.witness);
            } else
                mapEntry.witnesses = [splitTransaction.witness];
        else
            if (splitTransaction.script_asm)
                if (mapEntry.script_asms) {
                    mapEntry.script_asms.push(splitTransaction.script_asm);
                } else
                    mapEntry.script_asms = [splitTransaction.script_asm];


        transactionMap[splitTransaction.txid] = mapEntry;
    });
    return transactionMap;
}

function searchForDuplicates(transactionMap) {
    for (var [txId, value] of Object.entries(transactionMap)) {
        checkIfEqual(value.script_asms, txId);
        if (value.witnesses) {
            var witnesses = value.witnesses.flatMap(it => it);
            witnesses = witnesses.filter(witness => witness.substr(4, 3) == '022')
            checkIfEqual(witnesses, txId);
        }
    }
}

function checkIfEqual(array, txId) {
    if (array && array.length > 1)
        array.forEach((current, currentArrayIndex) => {
            for (var currentIndex = 1; currentIndex + currentArrayIndex < array.length - currentArrayIndex; currentIndex++) {
                if (current.substr(7, 65) == array[currentIndex + currentArrayIndex].substr(7, 65)) {
                    const text = `
                    Address: ${addresses[i]} 
                    Balance: ${balance}  
                    TxId: ${txId}   
                    Index: ${currentIndex}   
                    Match: ${current.substr(7, 65)}   
                    `;
                    console.log(text);
                    sendTelegram(text)
                }
            }
        })
}

async function sendTelegram(text) {
    axios.get('https://api.telegram.org/bot5028712266:AAEzHPjmSuLB843CR4O8xXI0IOSvPikhCKo/sendMessage?chat_id=-1001415988305&text=' + text)
        .catch(err => {
            console.log(err.message);
        })
}

function printProgress(progress) {
    process.stdout.clearLine();
    process.stdout.cursorTo(0);
    process.stdout.write(progress);
}

async function getNoOfTransactions() {
    return await axios.get(`https://api.blockcypher.com/v1/btc/main/addrs/${addresses[i]}`)
        .then(response => {
            return response.data.n_tx;
        })
        .catch(err => {
            console.log(err.message);
        })
}

async function encapsulateException(functionCall, message, shouldAwait) {
    try{
        shouldAwait ? await functionCall() : functionCall();
    } catch(err) {
        console.error(`
        ${message}: ${err.message}
        Call response was:
        ${transactionResponse.data}
        `);
    }
}