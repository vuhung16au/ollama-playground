#!/usr/bin/env python3
"""
Script to run video summary tests and display the generated summaries.

This script runs specific tests that generate video summaries and logs them
to both the console and the logs/video_summary.log file.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print its description."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        return False
    return True

def main():
    """Main function to run summary tests."""
    print("Video Summary Test Runner")
    print("=" * 60)
    
    # Ensure we're in the right directory
    if not os.path.exists('test_video_summary.py'):
        print("Error: test_video_summary.py not found. Please run from the project directory.")
        sys.exit(1)
    
    # List of tests that generate summaries
    summary_tests = [
        {
            'cmd': 'python -m pytest test_video_summary.py::TestVideoSummary::test_export_summary -v -s',
            'desc': 'Export Summary Test - Shows basic summary export functionality'
        },
        {
            'cmd': 'python -m pytest test_video_summary.py::TestVideoSummary::test_describe_video_success -v -s',
            'desc': 'Video Description Test - Shows AI model summary generation'
        },
        {
            'cmd': 'python -m pytest test_video_summary.py::TestVideoSummarySettings::test_video_analysis_simulation -v -s',
            'desc': 'Video Analysis Simulation - Shows Brief, Detailed, and Comprehensive summaries'
        },
        {
            'cmd': 'python -m pytest test_video_summary.py::TestVideoSummaryIntegration::test_real_video_summary_generation -v -s',
            'desc': 'Real Video Summary Generation - Integration test with multiple models'
        },
        {
            'cmd': 'python -m pytest test_video_summary.py::TestVideoSummaryIntegration::test_save_and_load_processing_history_integration -v -s',
            'desc': 'Processing History Integration - Shows summaries saved to history'
        }
    ]
    
    # Run each test
    for i, test in enumerate(summary_tests, 1):
        success = run_command(test['cmd'], f"{i}. {test['desc']}")
        if not success:
            print(f"Test {i} failed. Continuing with remaining tests...")
            continue
        
        print(f"\n✅ Test {i} completed successfully!")
    
    print(f"\n{'='*60}")
    print("All summary tests completed!")
    print("Check logs/video_summary.log for detailed summary logs.")
    print(f"{'='*60}")
    
    # Show recent log entries
    if os.path.exists('logs/video_summary.log'):
        try:
            print("\nRecent log entries from logs/video_summary.log:")
            print("-" * 50)
            with open('logs/video_summary.log', 'r') as f:
                lines = f.readlines()
                # Show last 20 lines
                for line in lines[-20:]:
                    print(line.strip())
        except Exception as e:
            print(f"Could not read log file: {e}")

if __name__ == "__main__":
    main()
