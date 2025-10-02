#!/usr/bin/env python3
"""
Basic load testing tool to compare against your DDoS script
"""

import requests
import threading
import time
import argparse
from datetime import datetime


class LoadTester:
    def __init__(self, target_url, num_threads=10, duration=60):
        self.target_url = target_url
        self.num_threads = num_threads
        self.duration = duration
        self.running = False
        self.stats = {
            'requests_sent': 0,
            'success_count': 0,
            'error_count': 0,
            'total_response_time': 0
        }
        self.lock = threading.Lock()

    def send_request(self):
        """Send a single request to the target"""
        try:
            start_time = time.time()
            response = requests.get(self.target_url, timeout=10)
            end_time = time.time()

            with self.lock:
                self.stats['requests_sent'] += 1
                if 200 <= response.status_code < 400:
                    self.stats['success_count'] += 1
                else:
                    self.stats['error_count'] += 1
                self.stats['total_response_time'] += (end_time - start_time)

            print(f"[{self.stats['requests_sent']}] {response.status_code} - {self.target_url}")

        except Exception as e:
            with self.lock:
                self.stats['requests_sent'] += 1
                self.stats['error_count'] += 1
            print(f"[{self.stats['requests_sent']}] ERROR: {str(e)[:50]}")

    def worker_thread(self):
        """Worker thread that sends requests"""
        while self.running:
            self.send_request()
            time.sleep(0.1)  # Small delay to prevent overwhelming

    def start_test(self):
        """Start the load test"""
        print(f"Starting load test on {self.target_url}")
        print(f"Threads: {self.num_threads}")
        print(f"Duration: {self.duration} seconds")
        print("Press Ctrl+C to stop early")
        print("-" * 50)

        self.running = True
        threads = []

        for i in range(self.num_threads):
            thread = threading.Thread(target=self.worker_thread)
            thread.daemon = True
            thread.start()
            threads.append(thread)
            time.sleep(0.01)  # Small delay between starting threads

        start_time = time.time()
        try:
            while self.running and (time.time() - start_time) < self.duration:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nTest interrupted by user")

        self.stop_test()

    def stop_test(self):
        """Stop the load test and show results"""
        print("\nStopping load test...")
        self.running = False
        time.sleep(2)  # Give threads time to finish

        # Calculate statistics
        total_time = time.time() - (time.time() - self.duration) if hasattr(self, 'start_time') else self.duration
        avg_response_time = self.stats['total_response_time'] / self.stats['requests_sent'] if self.stats[
                                                                                                   'requests_sent'] > 0 else 0

        print("\n" + "=" * 50)
        print("LOAD TEST RESULTS")
        print("=" * 50)
        print(f"Target URL: {self.target_url}")
        print(f"Test Duration: {total_time:.2f} seconds")
        print(f"Threads: {self.num_threads}")
        print("-" * 30)
        print(f"Total Requests: {self.stats['requests_sent']}")
        print(f"Successful Requests: {self.stats['success_count']}")
        print(f"Failed Requests: {self.stats['error_count']}")
        print(f"Success Rate: {(self.stats['success_count'] / self.stats['requests_sent'] * 100):.2f}%" if self.stats[
                                                                                                               'requests_sent'] > 0 else "Success Rate: 0%")
        print(f"Average Response Time: {avg_response_time:.3f} seconds")
        print(f"Requests Per Second: {self.stats['requests_sent'] / total_time:.2f}")
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='Basic Load Testing Tool')
    parser.add_argument('url', help='Target URL to test')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Test duration in seconds (default: 60)')

    args = parser.parse_args()

    tester = LoadTester(args.url, args.threads, args.duration)
    tester.start_test()


if __name__ == "__main__":
    main()
