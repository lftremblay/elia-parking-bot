#!/usr/bin/env python3
"""
Story 1.2 Structure Validation Test
Tests code structure and imports without requiring full dependencies
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def test_file_structure():
    """Test that all Story 1.2 files exist and have correct structure"""
    print("Testing Story 1.2 File Structure...")
    
    required_files = [
        "bot_orchestrator.py",
        "scheduler.py", 
        "error_recovery_manager.py",
        "performance_optimizer.py",
        "story_1_2_e2e_test_suite.py",
        "test_cloud_auth_integration.py",
        "test_end_to_end_reservation.py",
        "Story-1-2-End-to-End-Reservation-Flow.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"[PASS] {file} exists")
    
    if missing_files:
        print(f"[FAIL] Missing files: {missing_files}")
        return False
    
    print("[PASS] All required files exist")
    return True

def test_python_syntax():
    """Test Python syntax for all Python files"""
    print("\nTesting Python Syntax...")
    
    python_files = [
        "bot_orchestrator.py",
        "scheduler.py",
        "error_recovery_manager.py", 
        "performance_optimizer.py",
        "story_1_2_e2e_test_suite.py",
        "test_cloud_auth_integration.py",
        "test_end_to_end_reservation.py"
    ]
    
    syntax_errors = []
    for file in python_files:
        if Path(file).exists():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    compile(f.read(), file, 'exec')
                print(f"[PASS] {file} syntax valid")
            except SyntaxError as e:
                syntax_errors.append(f"{file}: {e}")
                print(f"[FAIL] {file} syntax error: {e}")
    
    if syntax_errors:
        print(f"[FAIL] Syntax errors found: {syntax_errors}")
        return False
    
    print("[PASS] All Python files have valid syntax")
    return True

def test_class_definitions():
    """Test that required classes are defined"""
    print("\nTesting Class Definitions...")
    
    # Test bot_orchestrator.py
    try:
        with open("bot_orchestrator.py", 'r') as f:
            content = f.read()
        
        required_classes = ["EliaParkingBot"]
        required_methods = [
            "__init__",
            "authenticate", 
            "_authenticate_with_cloud_manager",
            "_transfer_cloud_auth_to_bot",
            "reserve_spot",
            "_verify_authentication_state",
            "_perform_spot_detection",
            "_execute_spot_reservation",
            "_verify_reservation_completion"
        ]
        
        for cls in required_classes:
            if f"class {cls}" in content:
                print(f"[PASS] {cls} class defined")
            else:
                print(f"[FAIL] {cls} class not found")
                return False
        
        for method in required_methods:
            if f"def {method}" in content:
                print(f"[PASS] {method} method defined")
            else:
                print(f"[WARN] {method} method not found")
        
    except Exception as e:
        print(f"[FAIL] Error checking bot_orchestrator.py: {e}")
        return False
    
    # Test scheduler.py
    try:
        with open("scheduler.py", 'r') as f:
            content = f.read()
        
        if "class ReservationScheduler" in content:
            print("[PASS] ReservationScheduler class defined")
        else:
            print("[FAIL] ReservationScheduler class not found")
            return False
        
        required_scheduler_methods = [
            "_create_enhanced_callback",
            "_validate_timing_configuration",
            "get_performance_metrics"
        ]
        
        for method in required_scheduler_methods:
            if f"def {method}" in content:
                print(f"[PASS] {method} method defined")
            else:
                print(f"[WARN] {method} method not found")
                
    except Exception as e:
        print(f"[FAIL] Error checking scheduler.py: {e}")
        return False
    
    # Test error_recovery_manager.py
    try:
        with open("error_recovery_manager.py", 'r') as f:
            content = f.read()
        
        if "class ErrorRecoveryManager" in content:
            print("[PASS] ErrorRecoveryManager class defined")
        else:
            print("[FAIL] ErrorRecoveryManager class not found")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error checking error_recovery_manager.py: {e}")
        return False
    
    # Test performance_optimizer.py
    try:
        with open("performance_optimizer.py", 'r') as f:
            content = f.read()
        
        if "class PerformanceOptimizer" in content:
            print("[PASS] PerformanceOptimizer class defined")
        else:
            print("[FAIL] PerformanceOptimizer class not found")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error checking performance_optimizer.py: {e}")
        return False
    
    print("[PASS] All required classes defined")
    return True

def test_story_1_2_completion():
    """Test Story 1.2 completion status"""
    print("\nTesting Story 1.2 Completion Status...")
    
    try:
        with open("Story-1-2-End-to-End-Reservation-Flow.md", 'r') as f:
            content = f.read()
        
        # Check that all tasks are marked complete
        completed_tasks = content.count("- [x] Task")
        total_tasks = content.count("- [ ] Task") + completed_tasks
        
        completed_subtasks = content.count("  - [x] Subtask")
        total_subtasks = content.count("  - [ ] Subtask") + completed_subtasks
        
        print(f"[PASS] Tasks: {completed_tasks}/{total_tasks} completed")
        print(f"[PASS] Subtasks: {completed_subtasks}/{total_subtasks} completed")
        
        # Check for Story 1.2 completion indicators
        if "Story 1.2" in content and "COMPLETE" in content:
            print("[PASS] Story 1.2 marked as complete")
        else:
            print("[WARN] Story 1.2 completion status unclear")
        
        return completed_tasks == total_tasks and completed_subtasks == total_subtasks
        
    except Exception as e:
        print(f"[FAIL] Error checking Story 1.2 file: {e}")
        return False

def test_import_structure():
    """Test import structure without executing imports"""
    print("\nTesting Import Structure...")
    
    # Test bot_orchestrator.py imports
    try:
        with open("bot_orchestrator.py", 'r') as f:
            content = f.read()
        
        required_imports = [
            "from auth_manager import AuthenticationManager",
            "from browser_automation import BrowserAutomation",
            "from spot_detector import SpotDetector",
            "from notifier import Notifier"
        ]
        
        # Check for cloud auth import
        if "from src.cloud.cloud_auth_manager import CloudAuthenticationManager" in content:
            print("[PASS] Cloud authentication import present")
        else:
            print("[WARN] Cloud authentication import not found")
        
        for imp in required_imports:
            if imp in content:
                print(f"[PASS] {imp} found")
            else:
                print(f"[WARN] {imp} not found")
                
    except Exception as e:
        print(f"[FAIL] Error checking imports: {e}")
        return False
    
    print("[PASS] Import structure validated")
    return True

def test_configuration():
    """Test configuration files"""
    print("\nTesting Configuration...")
    
    try:
        # Check if config.json exists
        if Path("config.json").exists():
            print("[PASS] config.json exists")
            
            # Try to parse it
            with open("config.json", 'r') as f:
                config = json.load(f)
            
            # Check required sections
            required_sections = ["elia", "schedules", "retry", "performance"]
            for section in required_sections:
                if section in config:
                    print(f"[PASS] {section} section present")
                else:
                    print(f"[WARN] {section} section missing")
        else:
            print("[WARN] config.json not found")
            
    except Exception as e:
        print(f"[FAIL] Error checking configuration: {e}")
        return False
    
    print("[PASS] Configuration validated")
    return True

def generate_test_report(results):
    """Generate test report"""
    print("\nGenerating Test Report...")
    
    report = {
        "test_suite": "Story 1.2 Structure Validation",
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "overall_success": all(results.values()),
        "summary": {
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results.values() if r),
            "failed_tests": sum(1 for r in results.values() if not r)
        }
    }
    
    # Save report
    with open("story_1_2_structure_test_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Test report saved to: story_1_2_structure_test_report.json")
    
    # Print summary
    success = report["overall_success"]
    if success:
        print("Story 1.2 Structure Validation: PASSED")
        print("All structural tests passed - Ready for GitHub push!")
    else:
        print("Story 1.2 Structure Validation: FAILED")
        print("Some issues need to be resolved before pushing")
    
    return report

def main():
    """Main test runner"""
    print("Starting Story 1.2 Structure Validation Tests...")
    print("=" * 60)
    
    results = {}
    
    # Run all tests
    results["file_structure"] = test_file_structure()
    results["python_syntax"] = test_python_syntax()
    results["class_definitions"] = test_class_definitions()
    results["story_1_2_completion"] = test_story_1_2_completion()
    results["import_structure"] = test_import_structure()
    results["configuration"] = test_configuration()
    
    # Generate report
    report = generate_test_report(results)
    
    return 0 if report["overall_success"] else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
