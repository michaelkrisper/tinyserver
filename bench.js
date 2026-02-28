const http = require('http');

const url = process.argv[2] || 'http://localhost:80/';
const concurrency = 100; // number of concurrent workers
const duration = 10; // seconds

let totalRequests = 0;
let errors = 0;
let running = true;

const agent = new http.Agent({
    keepAlive: false, // Force recreation of connections to match typical fast tests
    maxSockets: concurrency
});

console.log(`Starting benchmark against ${url}`);
console.log(`Concurrency: ${concurrency} workers, Duration: ${duration}s...`);

const start = Date.now();

function makeRequest(workerId) {
    if (!running) return;

    const req = http.get(url, { agent }, (res) => {
        res.on('data', () => { }); // Consume data
        res.on('end', () => {
            totalRequests++;
            makeRequest(workerId); // Fire next request
        });
    });

    req.on('error', (err) => {
        errors++;
        makeRequest(workerId);
    });
}

// Start workers
for (let i = 0; i < concurrency; i++) {
    makeRequest(i);
}

// Stop after duration
setTimeout(() => {
    running = false;
    const elapsed = (Date.now() - start) / 1000;
    const rps = (totalRequests / elapsed).toFixed(2);

    console.log('\n--- Benchmark Results ---');
    console.log(`Total Requests: ${totalRequests}`);
    console.log(`Failed Requests: ${errors}`);
    console.log(`Time taken: ${elapsed} seconds`);
    console.log(`Requests Per Second (RPS): ${rps}`);

    process.exit(0);
}, duration * 1000);
