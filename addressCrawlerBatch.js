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


const balanceUrl = `https://blockchain.info/balance`;
const batchSize = 128;
let i;

for (i = 0; i < addresses.length; i += batchSize ) {
    try {
        console.log(`----${i}/${addresses.length}----`);

        const addressesList = addresses.slice(i, i + batchSize).join(',');
        
        await checkAddresses(`${balanceUrl}?active=${addressesList}`);

        console.log(`Finished`);
    } catch(err) {
        printError(err, "Error in iterating addresses", `On index: ${i}`)
    }
}

async function checkAddresses(path) {
    await axios.get(path).then(async balanceResponse => {
        Object.entries(balanceResponse.data).forEach(entry => {
            const addressBalance =  {
                address: entry[0],
                final_balance: entry[1].final_balance,
                n_tx: entry[1].n_tx,
                total_received: entry[1].total_received
            };

            if (addressBalance.final_balance > 10000) {
                console.log(`[${addressBalance.address}] BALANCE  \t\t \t\t${addressBalance.final_balance}`);

                sendTelegram(JSON.stringify(addressBalance));
            }
        });

        
    })
    .catch(err => printError(err, "Error checking address", ''))
}

async function sendTelegram(text) {
    axios.get('https://api.telegram.org/bot5028712266:AAEzHPjmSuLB843CR4O8xXI0IOSvPikhCKo/sendMessage?chat_id=-1001415988305&text=' + text)
        .catch(err => printError(err, "Error when sendTelegram()"))
}

function printProgress(progress) {
    process.stdout.clearLine();
    process.stdout.cursorTo(0);
    process.stdout.write(progress);
}


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