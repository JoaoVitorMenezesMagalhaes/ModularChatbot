#!/usr/bin/env python3
"""Test runner script for the modular chatbot."""
import subprocess
import sys
import os

def run_tests():
    """Run all tests with proper configuration."""
    print("🧪 Running Modular Chatbot Tests")
    print("=" * 50)
    
    # Set environment variables for testing
    os.environ["OPENAI_API_KEY"] = "test_key"
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["API_DEBUG"] = "true"
    
    # Run pytest with specific options
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return 1

def run_unit_tests():
    """Run only unit tests."""
    print("🧪 Running Unit Tests")
    print("=" * 30)
    
    cmd = [
        "python", "-m", "pytest",
        "tests/test_router_agent.py",
        "tests/test_math_agent.py",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Unit tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Unit tests failed with exit code {e.returncode}")
        return e.returncode

def run_e2e_tests():
    """Run only E2E tests."""
    print("🧪 Running E2E Tests")
    print("=" * 30)
    
    cmd = [
        "python", "-m", "pytest",
        "tests/test_e2e_chat_api.py",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ E2E tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ E2E tests failed with exit code {e.returncode}")
        return e.returncode

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "unit":
            sys.exit(run_unit_tests())
        elif sys.argv[1] == "e2e":
            sys.exit(run_e2e_tests())
        else:
            print("Usage: python run_tests.py [unit|e2e]")
            sys.exit(1)
    else:
        sys.exit(run_tests())
