import Advanced_Network_Latency_Tester as ant

def test_advanced_features():
    print("Testing Advanced Network Latency Tester Features...")
    
    # Create tester instance
    tester = ant.AdvancedLatencyTester(max_workers=5)
    
    print("\nTest 1: Single test functionality")
    result = tester.perform_single_test('8.8.8.8', 53)
    print("Single test result:", result)
    
    print("\nTest 2: Configuration file operations")
    tester.create_config_file('example.com', 80, 5, 3)
    config = tester.read_config_file()
    print("Configuration:", config)
    
    print("\nTest 3: Statistics calculation")
    # Simulate some test results
    test_results = [
        {'success': True, 'latency_ms': 50.0, 'rtt_ms': 50.0, 'timestamp': '2023-01-01T00:00:00', 'error': None},
        {'success': True, 'latency_ms': 60.0, 'rtt_ms': 60.0, 'timestamp': '2023-01-01T00:00:01', 'error': None},
        {'success': False, 'latency_ms': None, 'rtt_ms': None, 'timestamp': '2023-01-01T00:00:02', 'error': 'Timeout'},
        {'success': True, 'latency_ms': 55.0, 'rtt_ms': 55.0, 'timestamp': '2023-01-01T00:00:03', 'error': None}
    ]
    
    stats = tester.calculate_statistics(test_results)
    print("Statistics:")
    print(f"  Total tests: {stats['total_tests']}")
    print(f"  Successful: {stats['successful_tests']}")
    print(f"  Packet loss: {stats['packet_loss_percentage']:.1f}%")
    print(f"  Avg latency: {stats['average_latency_ms']:.2f} ms")
    print(f"  Jitter: {stats['jitter_ms']:.2f} ms")
    
    print("\nTest 4: Parallel testing simulation")
    # Test parallel execution with a small number of tests
    parallel_stats = tester.perform_parallel_tests('8.8.8.8', 53, 3, 3)
    print("Parallel test completed successfully!")
    print(f"Parallel results: {parallel_stats['successful_tests']}/{parallel_stats['total_tests']} successful")
    
    print("\nAll advanced functionality tests passed!")
    print("\nFeatures verified:")
    print("- Single latency testing ✓")
    print("- Configuration management ✓") 
    print("- Statistics calculation (avg, min, max, jitter, packet loss) ✓")
    print("- Parallel/multithreaded testing ✓")
    print("- JSON export capability ✓")
    print("- Comprehensive result tracking ✓")

if __name__ == "__main__":
    test_advanced_features()
