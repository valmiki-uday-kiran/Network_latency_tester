import socket
import time
import os
import threading
import statistics
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class AdvancedLatencyTester:
    def __init__(self, max_workers=15):
        self.results = {}  # Dictionary to store comprehensive test results
        self.test_history = []  # List to store historical test data
        self.max_workers = max_workers  # Maximum threads for parallel testing
        
    def perform_single_test(self, host, port, timeout=5):
        """
        Perform a single latency test and return detailed metrics.
        
        Args:
            host (str): Target hostname or IP address
            port (int): Target port number
            timeout (int): Connection timeout in seconds
            
        Returns:
            dict: Detailed test results including RTT, success status, and timestamp
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(timeout)
            
            start_time = time.time()
            client_socket.connect((host, port))
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            client_socket.close()
            
            return {
                'success': True,
                'latency_ms': latency_ms,
                'rtt_ms': latency_ms,  # RTT is same as latency for TCP connections
                'timestamp': datetime.now().isoformat(),
                'error': None
            }
            
        except socket.timeout:
            return {
                'success': False,
                'latency_ms': float('inf'),
                'rtt_ms': float('inf'),
                'timestamp': datetime.now().isoformat(),
                'error': 'Connection timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'latency_ms': None,
                'rtt_ms': None,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def perform_parallel_tests(self, host, port, num_tests=10, timeout=5):
        """
        Perform multiple latency tests in parallel using threading.
        
        Args:
            host (str): Target hostname or IP address
            port (int): Target port number
            num_tests (int): Number of tests to perform
            timeout (int): Connection timeout in seconds
            
        Returns:
            dict: Comprehensive test statistics
        """
        test_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all test tasks
            future_to_test = {
                executor.submit(self.perform_single_test, host, port, timeout): i 
                for i in range(num_tests)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_test):
                test_id = future_to_test[future]
                try:
                    result = future.result()
                    test_results.append(result)
                except Exception as e:
                    test_results.append({
                        'success': False,
                        'latency_ms': None,
                        'rtt_ms': None,
                        'timestamp': datetime.now().isoformat(),
                        'error': str(e)
                    })
        
        return self.calculate_statistics(test_results)

    def calculate_statistics(self, test_results):
        """
        Calculate comprehensive statistics from test results.
        
        Args:
            test_results (list): List of individual test results
            
        Returns:
            dict: Comprehensive statistics including jitter, packet loss, etc.
        """
        successful_tests = [r for r in test_results if r['success']]
        failed_tests = [r for r in test_results if not r['success']]
        
        latencies = [r['latency_ms'] for r in successful_tests]
        
        # Calculate basic statistics
        stats = {
            'total_tests': len(test_results),
            'successful_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'packet_loss_percentage': (len(failed_tests) / len(test_results)) * 100 if test_results else 0,
            'test_timestamp': datetime.now().isoformat()
        }
        
        if successful_tests:
            stats.update({
                'average_latency_ms': statistics.mean(latencies),
                'min_latency_ms': min(latencies),
                'max_latency_ms': max(latencies),
                'median_latency_ms': statistics.median(latencies),
                'std_dev_latency_ms': statistics.stdev(latencies) if len(latencies) > 1 else 0,
            })
            
            # Calculate jitter (mean deviation of latency differences)
            if len(latencies) > 1:
                differences = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
                stats['jitter_ms'] = statistics.mean(differences)
            else:
                stats['jitter_ms'] = 0
        else:
            # Set default values when no successful tests
            stats.update({
                'average_latency_ms': float('inf'),
                'min_latency_ms': float('inf'),
                'max_latency_ms': float('inf'),
                'median_latency_ms': float('inf'),
                'std_dev_latency_ms': 0,
                'jitter_ms': 0
            })
        
        stats['individual_results'] = test_results
        return stats

    def record_comprehensive_result(self, test_id, statistics):
        """
        Record comprehensive test results with detailed statistics.
        
        Args:
            test_id (str): Identifier for the test result
            statistics (dict): Comprehensive test statistics
        """
        self.results[test_id] = statistics
        self.test_history.append({
            'test_id': test_id,
            'timestamp': statistics['test_timestamp'],
            'statistics': statistics
        })
        
        print(f"Comprehensive test recorded - ID: {test_id}")
        print(f"  Successful tests: {statistics['successful_tests']}/{statistics['total_tests']}")
        print(f"  Packet loss: {statistics['packet_loss_percentage']:.2f}%")
        if statistics['successful_tests'] > 0:
            print(f"  Avg latency: {statistics['average_latency_ms']:.2f} ms")
            print(f"  Jitter: {statistics['jitter_ms']:.2f} ms")

    def display_comprehensive_results(self):
        """
        Display all recorded comprehensive test results.
        """
        if not self.results:
            print("No comprehensive test results recorded yet.")
            return
        
        print("\nComprehensive Test Results:")
        print("=" * 80)
        for test_id, stats in self.results.items():
            print(f"Test ID: {test_id}")
            print(f"Timestamp: {stats['test_timestamp']}")
            print(f"Successful: {stats['successful_tests']}/{stats['total_tests']} "
                  f"({stats['packet_loss_percentage']:.2f}% loss)")
            if stats['successful_tests'] > 0:
                print(f"Avg Latency: {stats['average_latency_ms']:.2f} ms")
                print(f"Min Latency: {stats['min_latency_ms']:.2f} ms")
                print(f"Max Latency: {stats['max_latency_ms']:.2f} ms")
                print(f"Jitter: {stats['jitter_ms']:.2f} ms")
                print(f"Std Dev: {stats['std_dev_latency_ms']:.2f} ms")
            print("-" * 40)

    def export_results_json(self, filename="network_test_results.json"):
        """
        Export all test results to a JSON file.
        
        Args:
            filename (str): Output filename
        """
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'test_results': self.results,
            'test_history': self.test_history
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Results exported to {filename}")

    def create_config_file(self, host, port, num_tests=10, timeout=5):
        """
        Create a configuration file with test parameters.
        
        Args:
            host (str): Target hostname or IP address
            port (int): Target port number
            num_tests (int): Default number of tests
            timeout (int): Default timeout in seconds
        """
        config = {
            'host': host,
            'port': port,
            'default_num_tests': num_tests,
            'default_timeout': timeout,
            'config_created': datetime.now().isoformat()
        }
        
        with open("config.json", 'w') as file:
            json.dump(config, file, indent=2)
        
        print("Configuration file created")

    def read_config_file(self):
        """
        Read configuration from file.
        
        Returns:
            dict: Configuration parameters or None if file doesn't exist
        """
        try:
            with open("config.json", 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("Configuration file not found.")
            return None
        except json.JSONDecodeError:
            print("Configuration file is corrupted.")
            return None

    def menu(self):
        """
        Enhanced menu with comprehensive testing options.
        """
        while True:
            print("\n=== Advanced Network Latency Tester ===")
            print("1. Perform Single Latency Test")
            print("2. Perform Comprehensive Parallel Test")
            print("3. Display Comprehensive Results")
            print("4. Export Results to JSON")
            print("5. Update Configuration")
            print("6. View Configuration")
            print("7. View Test History")
            print("0. Exit")

            choice = input("Enter your choice: ").strip()

            if choice == '1':
                config = self.read_config_file() or {}
                host = config.get('host') or input("Enter host: ")
                port = config.get('port') or int(input("Enter port: "))
                
                result = self.perform_single_test(host, port)
                test_id = f"single_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.record_comprehensive_result(test_id, {
                    'total_tests': 1,
                    'successful_tests': 1 if result['success'] else 0,
                    'failed_tests': 0 if result['success'] else 1,
                    'packet_loss_percentage': 0 if result['success'] else 100,
                    'average_latency_ms': result['latency_ms'],
                    'min_latency_ms': result['latency_ms'],
                    'max_latency_ms': result['latency_ms'],
                    'median_latency_ms': result['latency_ms'],
                    'std_dev_latency_ms': 0,
                    'jitter_ms': 0,
                    'test_timestamp': result['timestamp'],
                    'individual_results': [result]
                })

            elif choice == '2':
                config = self.read_config_file() or {}
                host = config.get('host') or input("Enter host: ")
                port = config.get('port') or int(input("Enter port: "))
                num_tests = config.get('default_num_tests') or int(input("Number of tests (default 10): ") or "10")
                timeout = config.get('default_timeout') or int(input("Timeout in seconds (default 5): ") or "5")
                
                print(f"\nPerforming {num_tests} parallel tests to {host}:{port}...")
                stats = self.perform_parallel_tests(host, port, num_tests, timeout)
                test_id = f"parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.record_comprehensive_result(test_id, stats)

            elif choice == '3':
                self.display_comprehensive_results()

            elif choice == '4':
                filename = input("Enter export filename (default: network_test_results.json): ") or "network_test_results.json"
                self.export_results_json(filename)

            elif choice == '5':
                host = input("Enter host: ")
                port = int(input("Enter port: "))
                num_tests = int(input("Default number of tests: ") or "10")
                timeout = int(input("Default timeout (seconds): ") or "5")
                self.create_config_file(host, port, num_tests, timeout)

            elif choice == '6':
                config = self.read_config_file()
                if config:
                    print("\nCurrent Configuration:")
                    for key, value in config.items():
                        print(f"  {key}: {value}")
                else:
                    print("No configuration found.")

            elif choice == '7':
                if not self.test_history:
                    print("No test history available.")
                else:
                    print("\nTest History (most recent first):")
                    for history in reversed(self.test_history[-10:]):  # Show last 10 tests
                        print(f"{history['timestamp']} - {history['test_id']}")

            elif choice == '0':
                print("Exiting Advanced Network Latency Tester.")
                break

            else:
                print("Invalid choice. Please try again.")

# Example usage:
if __name__ == "__main__":
    tester = AdvancedLatencyTester(max_workers=15)  # Increased thread pool for better performance
    tester.menu()
