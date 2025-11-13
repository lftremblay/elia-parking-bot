#!/usr/bin/env python3
"""
Comprehensive QA Syntax Validator
Catches syntax errors BEFORE GitHub Actions deployment
"""

import ast
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
from loguru import logger

class QASyntaxValidator:
    """Comprehensive syntax validation for all Python files"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent
        self.results = {
            "validation_session": "QA Syntax Validation",
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "syntax_errors": [],
            "import_errors": [],
            "critical_issues": [],
            "warnings": [],
            "overall_success": False
        }
        
    def validate_all_files(self) -> Dict[str, Any]:
        """Validate all Python files in the project"""
        print("🔍 Starting Comprehensive QA Syntax Validation...")
        print("=" * 60)
        
        # Find all Python files
        python_files = self._find_python_files()
        self.results["total_files"] = len(python_files)
        
        print(f"📁 Found {len(python_files)} Python files to validate")
        
        # Validate each file
        for file_path in python_files:
            self._validate_single_file(file_path)
        
        # Calculate final results
        self._calculate_final_results()
        
        # Generate report
        self._generate_report()
        
        return self.results
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        
        # Common patterns to exclude
        exclude_patterns = {
            '__pycache__', '.git', '.venv', '.venv310', 'node_modules',
            '.pytest_cache', '.mypy_cache', 'dist', 'build'
        }
        
        for file_path in self.project_root.rglob("*.py"):
            # Skip excluded directories
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue
            
            # Only include files in our project directory
            if file_path.is_file():
                python_files.append(file_path)
        
        return sorted(python_files)
    
    def _validate_single_file(self, file_path: Path):
        """Validate a single Python file for syntax and import issues"""
        relative_path = str(file_path.relative_to(self.project_root))
        
        try:
            # Test 1: Syntax validation
            syntax_ok, syntax_error = self._check_syntax(file_path)
            if not syntax_ok:
                self.results["syntax_errors"].append({
                    "file": relative_path,
                    "error": syntax_error,
                    "type": "syntax_error"
                })
                self.results["invalid_files"] += 1
                return
            
            # Test 2: Import validation
            import_ok, import_errors = self._check_imports(file_path)
            if not import_ok:
                self.results["import_errors"].extend([
                    {"file": relative_path, "error": error, "type": "import_error"}
                    for error in import_errors
                ])
                self.results["invalid_files"] += 1
                return
            
            # Test 3: Critical issue detection
            critical_issues = self._check_critical_issues(file_path)
            if critical_issues:
                self.results["critical_issues"].extend([
                    {"file": relative_path, "issue": issue, "type": "critical_issue"}
                    for issue in critical_issues
                ])
                self.results["invalid_files"] += 1
                return
            
            # Test 4: Warning detection (non-blocking)
            warnings = self._check_warnings(file_path)
            if warnings:
                self.results["warnings"].extend([
                    {"file": relative_path, "warning": warning, "type": "warning"}
                    for warning in warnings
                ])
            
            # File passed all tests
            self.results["valid_files"] += 1
            print(f"✅ {relative_path}")
            
        except Exception as e:
            self.results["syntax_errors"].append({
                "file": relative_path,
                "error": f"Validation failed: {str(e)}",
                "type": "validation_error"
            })
            self.results["invalid_files"] += 1
            print(f"❌ {relative_path} - Validation error: {e}")
    
    def _check_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Check Python syntax using AST parsing"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST to check syntax
            ast.parse(content)
            return True, None
            
        except SyntaxError as e:
            error_msg = f"Line {e.lineno}: {e.msg}"
            if e.text:
                error_msg += f" | Code: {e.text.strip()}"
            return False, error_msg
            
        except Exception as e:
            return False, f"File read error: {str(e)}"
    
    def _check_imports(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Check for common import issues"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to analyze imports
            tree = ast.parse(content)
            
            # Check for common problematic imports
            import_issues = self._analyze_imports(tree)
            errors.extend(import_issues)
            
            # Check for undefined variables in imports (common issue)
            undefined_issues = self._check_undefined_imports(tree, content)
            errors.extend(undefined_issues)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Import analysis failed: {str(e)}"]
    
    def _analyze_imports(self, tree: ast.AST) -> List[str]:
        """Analyze import statements for potential issues"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Check for known problematic imports
                    if alias.name in ['Page', 'Browser', 'BrowserContext']:
                        if not self._has_playwright_import(tree):
                            issues.append(f"Imported '{alias.name}' without Playwright import")
            
            elif isinstance(node, ast.ImportFrom):
                if node.module and 'playwright' in node.module:
                    # Check for proper Playwright import structure
                    if not self._has_proper_playwright_handling(tree):
                        issues.append("Playwright import without proper error handling")
        
        return issues
    
    def _has_playwright_import(self, tree: ast.AST) -> bool:
        """Check if Playwright is properly imported"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'playwright' in node.module:
                    return True
        return False
    
    def _has_proper_playwright_handling(self, tree: ast.AST) -> bool:
        """Check if Playwright imports have proper error handling"""
        content = ast.get_source_segment(open(__file__).read(), tree) if hasattr(ast, 'get_source_segment') else ""
        return 'try:' in content and 'playwright' in content
    
    def _check_undefined_imports(self, tree: ast.AST, content: str) -> List[str]:
        """Check for usage of imported types that might not be available"""
        issues = []
        
        # Look for usage of Playwright types
        playwright_types = ['Page', 'Browser', 'BrowserContext']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id in playwright_types:
                    # Check if this type is properly imported with error handling
                    if not self._has_safe_playwright_import(content):
                        issues.append(f"Used '{node.id}' without safe import handling")
        
        return issues
    
    def _has_safe_playwright_import(self, content: str) -> bool:
        """Check if Playwright imports have safe try/except handling"""
        return 'try:' in content and 'from playwright.async_api import' in content and 'except ImportError' in content
    
    def _check_critical_issues(self, file_path: Path) -> List[str]:
        """Check for critical issues that would cause runtime failures"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for incomplete try/except blocks
            incomplete_try = self._check_incomplete_try_blocks(content)
            issues.extend(incomplete_try)
            
            # Check for undefined variables in critical paths
            undefined_vars = self._check_undefined_variables(content)
            issues.extend(undefined_vars)
            
            # Check for async/await issues
            async_issues = self._check_async_issues(content)
            issues.extend(async_issues)
            
        except Exception as e:
            issues.append(f"Critical issue analysis failed: {str(e)}")
        
        return issues
    
    def _check_incomplete_try_blocks(self, content: str) -> List[str]:
        """Check for incomplete try/except blocks"""
        issues = []
        lines = content.split('\n')
        
        try_count = 0
        except_count = 0
        finally_count = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('try:'):
                try_count += 1
            elif stripped.startswith('except') or stripped.startswith('except:'):
                except_count += 1
            elif stripped.startswith('finally') or stripped.startswith('finally:'):
                finally_count += 1
        
        if try_count > (except_count + finally_count):
            issues.append(f"Incomplete try blocks: {try_count} try blocks vs {except_count + finally_count} except/finally blocks")
        
        return issues
    
    def _check_undefined_variables(self, content: str) -> List[str]:
        """Check for usage of potentially undefined variables"""
        issues = []
        
        # Common undefined variables in our codebase
        critical_vars = ['Page', 'Browser', 'BrowserContext']
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for var in critical_vars:
                if f'{var}' in line and 'import' not in line and 'def' not in line:
                    # Check if it's used in a type hint or function parameter
                    if ':' in line and f'{var}' in line.split(':')[-1]:
                        if 'try:' not in content[:content.find(line)]:
                            issues.append(f"Line {line_num}: Used '{var}' without safe import")
        
        return issues
    
    def _check_async_issues(self, content: str) -> List[str]:
        """Check for async/await related issues"""
        issues = []
        
        # Check for await without async
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            if 'await' in line and 'async def' not in content[:content.find(line)]:
                # This is a simplified check - could be improved
                if 'def ' not in line and 'class ' not in line:
                    issues.append(f"Line {line_num}: Possible await without async function")
        
        return issues
    
    def _check_warnings(self, file_path: Path) -> List[str]:
        """Check for non-blocking warnings"""
        warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for long lines
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                if len(line) > 120:
                    warnings.append(f"Line {line_num}: Very long line ({len(line)} chars)")
            
            # Check for TODO/FIXME comments
            if 'TODO' in content or 'FIXME' in content:
                warnings.append("Contains TODO/FIXME comments")
            
        except Exception:
            pass  # Warnings are non-critical
        
        return warnings[:5]  # Limit warnings to avoid noise
    
    def _calculate_final_results(self):
        """Calculate final validation results"""
        total_issues = (
            len(self.results["syntax_errors"]) +
            len(self.results["import_errors"]) +
            len(self.results["critical_issues"])
        )
        
        self.results["overall_success"] = (
            total_issues == 0 and
            self.results["valid_files"] == self.results["total_files"]
        )
        
        self.results["success_rate"] = (
            (self.results["valid_files"] / self.results["total_files"] * 100)
            if self.results["total_files"] > 0 else 0
        )
    
    def _generate_report(self):
        """Generate and save validation report"""
        print("\n" + "=" * 60)
        print("📊 QA SYNTAX VALIDATION REPORT")
        print("=" * 60)
        
        # Summary
        print(f"📁 Total Files: {self.results['total_files']}")
        print(f"✅ Valid Files: {self.results['valid_files']}")
        print(f"❌ Invalid Files: {self.results['invalid_files']}")
        print(f"📈 Success Rate: {self.results.get('success_rate', 0):.1f}%")
        print(f"🎯 Overall Status: {'✅ PASS' if self.results['overall_success'] else '❌ FAIL'}")
        
        # Issues
        if self.results["syntax_errors"]:
            print(f"\n🚨 SYNTAX ERRORS ({len(self.results['syntax_errors'])}):")
            for error in self.results["syntax_errors"][:5]:  # Show first 5
                print(f"  ❌ {error['file']}: {error['error']}")
        
        if self.results["import_errors"]:
            print(f"\n🔍 IMPORT ERRORS ({len(self.results['import_errors'])}):")
            for error in self.results["import_errors"][:5]:  # Show first 5
                print(f"  ❌ {error['file']}: {error['error']}")
        
        if self.results["critical_issues"]:
            print(f"\n⚠️ CRITICAL ISSUES ({len(self.results['critical_issues'])}):")
            for issue in self.results["critical_issues"][:5]:  # Show first 5
                print(f"  ⚠️ {issue['file']}: {issue['issue']}")
        
        if self.results["warnings"]:
            print(f"\n💡 WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"][:3]:  # Show first 3
                print(f"  💡 {warning['file']}: {warning['warning']}")
        
        # Save detailed report
        report_path = self.project_root / "qa_syntax_validation_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Recommendations
        if self.results["overall_success"]:
            print("\n🎉 EXCELLENT! All files passed syntax validation!")
            print("✅ Ready for GitHub deployment")
        else:
            print("\n🔧 ISSUES FOUND - Fix before deploying to GitHub!")
            print("❌ Deploying now will cause GitHub Actions failures")
            print("🔧 Fix the issues above and re-run validation")

def main():
    """Main validation function"""
    print("🚀 QA Syntax Validator for Elia Parking Bot")
    print("Prevents GitHub Actions failures by catching issues early!")
    print("=" * 60)
    
    validator = QASyntaxValidator()
    results = validator.validate_all_files()
    
    if results["overall_success"]:
        print("\n🎉 VALIDATION PASSED - Ready for deployment!")
        return 0
    else:
        print("\n❌ VALIDATION FAILED - Fix issues before deployment!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
