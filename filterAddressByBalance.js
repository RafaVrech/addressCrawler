import addresses from './addresses.js';
import axios from 'axios';
import axiosRetry from 'axios-retry';

axiosRetry(axios, {
    retries: 999999, // number of retries
    retryDelay: (retryCount) => {
        console.log(`Retry attempt: ${retryCount}`);
        return 500; // time interval between retries
    }
});

const addressesWithBalance = [];

const uniqueAddresses = [...new Set(addresses)];

for (var i in uniqueAddresses) {
    try {
        console.log(`[${uniqueAddresses[i]}] ----${(parseInt(i) + 1)}/${uniqueAddresses.length}----> Starting`);
        await checkAddress(uniqueAddresses[i]);
    } catch(err) {
        printError(err, "Error in iterating addresses", `On address: addresses[${i}] -> ${uniqueAddresses[i]}`)
    }
}

async function checkAddress(address) {
    var balanceUrl = `https://chain.so/api/v2/get_address_balance/BTC/${address}`;
    await axios.get(balanceUrl).then(async balanceResponse => {
        var balance = balanceResponse.data.data.confirmed_balance;
        console.log(`[${address}] BALANCE  \t\t \t\t${balance}`);

        if (balance > 0.0003) {
            addressesWithBalance.push(uniqueAddresses[i]);
        }
    })
    .catch(err => printError(err, "Error checking address",
   ))
}

console.log('Printando os que tem saldo ----->>>');
if(addressesWithBalance && addressesWithBalance.length > 0) {
    console.log(addressesWithBalance);
    await sendTelegram(addressesWithBalance);
}
console.log('<<<<< -------Printando os que tem saldo');

async function printError(error, message, data) {
    var aditionalData;
    if (data)
        aditionalData =
            `Aditional data:
            ${data}`;

    console.error(`
        ${message}: ${error.message}
        ${aditionalData}
        `);
}

async function sendTelegram(text) {
    axios.get('https://api.telegram.org/bot5028712266:AAEzHPjmSuLB843CR4O8xXI0IOSvPikhCKo/sendMessage?chat_id=-1001415988305&text=' + text)
        .catch(err => printError(err, "Error when sendTelegram()"))
}