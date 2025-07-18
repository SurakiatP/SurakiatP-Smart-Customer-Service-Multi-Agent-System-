import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all tests with coverage"""
    
    print("🧪 Running Customer Service AI Tests...")
    
    # Ensure we're in project root
    project_root = Path(__file__).parent.parent
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=True)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)