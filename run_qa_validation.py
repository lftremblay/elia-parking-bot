#!/usr/bin/env python3
"""
Cloud Authentication QA Validation Runner
Execute comprehensive QA testing for Story 1.1 Cloud Authentication Foundation
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import QA suite
from qa.cloud_auth_qa import run_qa_validation
from qa.report_generator import generate_qa_report


async def main():
    """Main QA validation runner"""
    print("🚀 Starting Cloud Authentication Foundation QA Validation")
    print("=" * 60)
    
    # Check environment
    print("🔍 Environment Check:")
    print(f"  Python Version: {sys.version}")
    print(f"  Working Directory: {os.getcwd()}")
    print(f"  Project Root: {project_root}")
    
    # Check required files
    required_files = [
        "src/cloud/cloud_auth_manager.py",
        "src/cloud/error_handler.py",
        "cloud_auth_config.py",
        "auth_manager.py",
        "local_env_template.env"
    ]
    
    print("\n📁 File Check:")
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files. QA validation cannot proceed.")
        return False
    
    # Run QA validation
    print("\n🧪 Running QA Validation Tests...")
    print("=" * 60)
    
    try:
        results = await run_qa_validation()
        
        # Save results to file
        results_file = project_root / "qa_results.json"
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Generate comprehensive QA report
        print("\n📄 Generating QA Report...")
        report_file = generate_qa_report(results, str(project_root / "Cloud_Authentication_QA_Report.md"))
        print(f"📋 QA Report saved to: {report_file}")
        
        return results['meets_requirements']
        
    except Exception as e:
        print(f"\n❌ QA validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run QA validation
    success = asyncio.run(main())
    
    # Print final result
    print("\n" + "=" * 60)
    if success:
        print("🎉 QA VALIDATION PASSED - Cloud Authentication Foundation is READY!")
        print("✅ Story 1.1 meets all requirements and is ready for production.")
        print("📋 Detailed report has been generated for your review.")
    else:
        print("❌ QA VALIDATION FAILED - Issues found that need to be addressed.")
        print("⚠️  Please review the QA report and fix the identified issues.")
        print("📋 Detailed report has been generated with specific recommendations.")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
