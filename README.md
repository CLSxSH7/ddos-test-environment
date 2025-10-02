# DDoS Test Environment

This is a controlled test environment for validating the effectiveness of DDoS penetration testing tools in authorized
scenarios.

## Overview

This environment provides:

- A test web server that simulates a real application
- Various endpoints with different resource requirements
- Monitoring capabilities to observe attack impact
- A comparison load tester to benchmark your DDoS tool

## Components

1. `server.py` - Test web server with multiple endpoints
2. `load_tester.py` - Basic load testing tool for comparison
3. `requirements.txt` - Dependencies for the test environment
4. `static/` - Static files for the web server
5. `logs/` - Server log files

## Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

2. **Start the test server**:
   ```bash
   python server.py

3. **Verify server is running**:
   Open browser to: http://localhost:8000
   Check API stats: http://localhost:8000/api/stats

## Test Server Endpoints

`GET /` - Main page (simple HTML response)

`GET /api/stats` - Real-time server statistics (JSON)

`GET /api/status` - API status endpoint (JSON)

`GET /health` - Health check (lightweight JSON)

`GET /slow` - Deliberately slow response (2 seconds delay)

`GET /heavy` - CPU-intensive processing

# Monitoring During Testing

## Server-Side Monitoring

**1. Real-time Request Log:**

**In server terminal**
[2023-07-15 14:30:15] REQUEST GET / from 127.0.0.1

**2. Live Statistics:**

```bash
Visit `http://localhost:8000/api/stats` in browser
```

**3. Log File Analysis**
tail -f logs/server.log

**4. System Resource Monitoring:**

`Linux/macOS:`

```bash
htop
iotop
```

`Windows:`

```bash
Use Task Manager or Resource Monitor
```

# Using the Comparison Load Tester

## Running the Load Tester

python load_tester.py http://localhost:8000 -t 20 -d 30

**Command Breakdown:**

- `python load_tester.py` - Execute the load tester script
- `http://localhost:8000` - Target URL to test
- `-t 20` - Thread count: 20 concurrent threads
- `-d 30` - Duration: Run test for 30 seconds

## Command Line Options

| Option | Long Form  | Description                  | Default |
|--------|------------|------------------------------|---------|
| -t     | --threads  | Number of concurrent threads | 10      |
| -d     | --duration | Test duration in seconds     | 60      |

## Additional Examples

`Basic test with defaults (10 threads, 60 seconds)`

   ```bash
   python load_tester.py http://localhost:8000
   ```

`High concurrency, short duration`

   ```bash
   python load_tester.py http://localhost:8000 -t 50 -d 15
   ```

`Low concurrency, long duration`

   ```bash
   python load_tester.py http://localhost:8000 -t 5 -d 120
   ```

`Test specific endpoint`

   ```bash
   python load_tester.py http://localhost:8000/slow -t 15 -d 45
   ```

## Understanding the Output

When you run the load tester, you'll see real-time output:

```
Starting load test on http://localhost:8000
Threads: 20
Duration: 30 seconds
--------------------------------------------------
[1] 200 - http://localhost:8000
[2] 200 - http://localhost:8000
[3] 200 - http://localhost:8000
...
==================================================
LOAD TEST RESULTS
==================================================
Target URL: http://localhost:8000
Test Duration: 30.00 seconds
Threads: 20
------------------------------
Total Requests: 1250
Successful Requests: 1200
Failed Requests: 50
Success Rate: 96.00%
Average Response Time: 0.245 seconds
Requests Per Second: 41.67
==================================================
```

## Benchmarking Your DDoS Tool

To effectively compare tools:

1. Run baseline test:
   ```bash
   python load_tester.py http://localhost:8000 -t 25 -d 60
   ```
   `Note: 41.67 requests/second, 96% success rate`

2. Run your DDoS tool with same parameters:

- Configure for 25 threads
- Run for approximately 60 seconds
- Compare results

3. Analyze differences:

- Request rates
- Success/failure patterns
- Resource utilization
- Attack sophistication

# Key Metrics to Watch

- Requests per second: How many requests are being handled
- Error rates: Connection failures or timeouts
- Response times: Latency under load
- Memory usage: Server resource consumption
- CPU utilization: Processing capacity

# Recommended Testing Approach

## Phase 1: Validation

- Start with 5-10 threads
- Verify requests are being received
- Check server response stability

## Phase 2: Baseline

- Increase to 20-30 threads
- Run for 1-2 minutes
- Record baseline performance metrics

## Phase 3: Stress Testing

- Gradually increase thread count
- Monitor system resource usage
- Identify breaking points
- Test different endpoints

## Phase 4: Comparison

- Run load tester with specific parameters
- Run DDoS tool with same parameters
- Compare effectiveness and resource usage

# Safety Guidelines

## Resource Management

- Monitor system resources continuously
- Set reasonable thread limits (start low, increase gradually)
- Have a quick stop mechanism ready
- Watch for system instability signs

## Emergency Procedures

1. Graceful Stop: Ctrl+C in the DDoS tool terminal
2. Force Kill (if unresponsive):

   `Find process`
   ```bash
   ps aux | grep python
   ```
   `Kill process`
   ```bash
   kill -9 <process_id>]
   ```
3. Server Restart: Stop and restart server.py if needed

## Testing Boundaries

- Only test on localhost (127.0.0.1)
- Never expose this server to external networks
- Keep testing sessions brief and controlled
- Stop immediately if system becomes unstable

# Example Test Results

## Normal Operation

```bash
Requests Processed: 1,250
Success Rate: 99.2%
Avg Response Time: 0.045s
```

## Under DDoS Load

```bash
Requests Processed: 8,450
Success Rate: 76.3%
Avg Response Time: 1.23s
Error Count: 2,003 (23.7%)
```

## Log Analysis

[TIMESTAMP] REQUEST METHOD PATH from IP_ADDRESS

## Analyzing Attack Impact

`Count requests per second`

```bash
grep "REQUEST" logs/server.log | cut -c2-21 | uniq -c
```

`Count errors`

```bash
grep "ERROR" logs/server.log | wc -l
```

`Monitor specific time period`

```bash
grep "2023-07-15 14:30" logs/server.log
```

## Troubleshooting

1. Port Already in Use:
   OSError: [Errno 98] Address already in use

- Kill existing process or change port in server.py

2. Connection Refused:

- Verify server is running
- Check port (should be 8000)
- Confirm localhost binding

3. High Error Rates:

- Reduce thread count
- Check system resources
- Verify endpoint availability

## Recovery Steps

1. Stop all testing tools
2. Restart the test server
3. Clear logs if needed
   ```bash
   > logs/server.log
   ```
4. Begin testing again with reduced load