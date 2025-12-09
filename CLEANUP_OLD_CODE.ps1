# Cleanup Script - Remove Unused Old Code
# This script removes all old bot versions, test files, and unused documentation

Write-Host "🧹 Starting cleanup of unused old code..." -ForegroundColor Cyan

# OLD BOT FILES (Browser-based - no longer used)
$oldBots = @(
    "robust_production_bot.py",
    "production_parking_bot.py",
    "smart_production_bot.py",
    "enterprise_api_bot.py",
    "fixed_booking_bot.py",
    "api_bot_orchestrator.py",
    "bot_orchestrator.py",
    "browser_automation.py",
    "main.py",
    "minimal_reserve.py",
    "patched_reserve.py"
)

# OLD API/AUTH FILES (Replaced by fixed_graphql_client.py)
$oldApiFiles = @(
    "elia_api_client.py",
    "elia_graphql_client.py",
    "elia_reservation_flow.py",
    "auth_manager.py",
    "auth_timeout_fix.py",
    "improved_auth_flow.py",
    "cloud_auth_config.py"
)

# DISCOVERY/DEBUG FILES (No longer needed)
$discoveryFiles = @(
    "alternative_auth_discovery.py",
    "alternative_auth_discovery_report.json",
    "api_discovery.py",
    "capture_graphql_queries.py",
    "discover_graphql_auth.py",
    "graphql_discovery.py",
    "extract_token.py",
    "debug_floor_spaces.py",
    "debug_user_id.py",
    "debug_imports_and_auth.py",
    "debug_syntax_error.py",
    "debug_totp_secret.py",
    "comprehensive_debug.py",
    "diagnostics.py"
)

# TEST FILES (Old tests)
$testFiles = @(
    "test_production_bot.py",
    "test_robust_bot.py",
    "test_smart_bot.py",
    "test_executive_booking.py",
    "test_tomorrow_booking.py",
    "test_tomorrow_exact.py",
    "test_current_token.py",
    "test_auth.bat",
    "test_auth_debug.py",
    "test_auth_timeout_fix.py",
    "test_browser.py",
    "test_cloud_auth_disable.py",
    "test_cloud_auth_integration.py",
    "test_cloud_auth_timeout_fix.py",
    "test_cloud_integration.py",
    "test_complete_auth_fix.py",
    "test_end_to_end_reservation.py",
    "test_health_monitoring_fix.py",
    "test_hello.py",
    "test_mfa_fixes.py",
    "test_mfa_import.py",
    "test_playwright.py",
    "test_playwright_default_timeout.py",
    "test_playwright_fix.py",
    "test_playwright_version.py",
    "test_sso.bat",
    "test_sso_flow.py",
    "test_story_1_2_structure.py",
    "test_applied_fixes.py",
    "comprehensive_e2e_test.py",
    "quick_e2e_validation.py",
    "story_1_2_e2e_test_suite.py",
    "local_test_simple.py",
    "simulate_reservation.py",
    "check_specific_booking.py",
    "verify_booking.py"
)

# UTILITY/HELPER FILES (No longer needed)
$utilityFiles = @(
    "analyze_function_structure.py",
    "browser_health_monitor.py",
    "check_browser.py",
    "check_browser_syntax.py",
    "check_browser_syntax_utf8.py",
    "check_if_elif.py",
    "check_indentation.py",
    "check_time.py",
    "cleanup_old_workflows.py",
    "error_recovery_manager.py",
    "examine_issue.py",
    "examine_try_blocks.py",
    "final_cleanup.py",
    "find_matching_if.py",
    "fix_elif_indent.py",
    "fix_indentation.py",
    "fix_logger_indent.py",
    "fix_orphaned_elif.py",
    "local_github_simulation.py",
    "notifier.py",
    "performance_optimizer.py",
    "pre-commit-check.py",
    "qr_decoder.py",
    "quick_auth_test.bat",
    "quick_auth_test.py",
    "quick_start.bat",
    "quick_syntax_check.py",
    "real_auth_test.bat",
    "real_auth_test.py",
    "remove_dead_code.py",
    "run_qa_validation.py",
    "scheduler.py",
    "setup_api_bot.py",
    "simple_qr_guide.py",
    "spot_detector.py",
    "update_totp_secret.py",
    "validate_github_workflow.py",
    "validate_import_fix.py"
)

# OLD DOCUMENTATION (Outdated)
$oldDocs = @(
    "API_FIRST_APPROACH.md",
    "API_SUCCESS_SUMMARY.md",
    "AUTHENTICATION_FIX_SUMMARY.md",
    "BOOKING_ANALYSIS.md",
    "BROWSER_EXTENSION_COMPLETE.md",
    "CLOUD_AUTH_DEPLOYMENT.md",
    "CRITICAL_IMPORT_FIX_SUMMARY.md",
    "Cloud_Authentication_QA_Report.md",
    "DEPLOYMENT_CHECKLIST.md",
    "DEPLOYMENT_GUIDE.md",
    "DEPLOYMENT_STRATEGY.md",
    "DISCOVERY_PROGRESS.md",
    "ELIA_APP_STRUCTURE.md",
    "ELIA_PLATFORM_INFO.md",
    "GITHUB_WORKFLOW_QA_INTEGRATION.md",
    "LOCAL_TESTING_GUIDE.md",
    "MFA_RESERVATION_E2E_TEST_REPORT.md",
    "MISSION_ACCOMPLISHED.md",
    "PLAYWRIGHT_TROUBLESHOOTING.md",
    "PRODUCTION_DEPLOYMENT_GUIDE.md",
    "PROJECT_SUMMARY.md",
    "QUICKSTART.md",
    "Story-1-1-Cloud-Authentication-Foundation.md",
    "Story-1-2-End-to-End-Reservation-Flow.md",
    "TOKEN_ROBUSTNESS_ANALYSIS.md",
    "WORKFLOW_CLEANUP_COMPLETE.md",
    "WORKFLOW_CLEANUP_SUMMARY.md",
    "WORKFLOW_FIX_SUMMARY.md",
    "WORKFLOW_STATUS.md",
    "browser_extension_token_automation.md",
    "day1_setup_checklist.md",
    "graphql_auth_discovery_strategy.md",
    "local_testing_summary.md",
    "mobile_app_auth_analysis_plan.md"
)

# COMMIT MESSAGE FILES
$commitFiles = @(
    "button_click_fix_commit.txt",
    "cloud_auth_disable_commit.txt",
    "cloud_auth_fix_commit.txt",
    "commit_message.txt",
    "default_timeout_commit.txt",
    "fix_commit_message.txt",
    "infinite_loop_fix_commit.txt",
    "playwright_fix_commit.txt",
    "quebecor_button_fix_commit.txt"
)

# OLD CONFIG/DATA FILES
$oldConfigFiles = @(
    "config.json",
    "local_env_template.env",
    "api_github_actions_workflow.yml",
    "download_browser.ps1",
    "install.bat",
    "trigger.txt",
    "qa_results.json",
    "story_1_2_structure_test_report.json",
    "parking_bot.log"
)

# DIRECTORIES TO REMOVE
$oldDirs = @(
    "api_discovery",
    "bmad-agent-windsurf-main",
    "browser_data",
    "logs",
    "qa",
    "screenshots",
    "screenshots logs 58",
    "session_data",
    "src",
    "test_browser_data",
    "tests",
    "webbundles",
    "%AppData%",
    "%AppData% - Copie"
)

# Function to safely remove files
function Remove-SafelyFile {
    param($file)
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✅ Deleted: $file" -ForegroundColor Green
    }
}

# Function to safely remove directories
function Remove-SafelyDir {
    param($dir)
    if (Test-Path $dir) {
        Remove-Item $dir -Recurse -Force
        Write-Host "  ✅ Deleted directory: $dir" -ForegroundColor Green
    }
}

# Delete old bot files
Write-Host "`n🤖 Removing old bot files..." -ForegroundColor Yellow
foreach ($file in $oldBots) {
    Remove-SafelyFile $file
}

# Delete old API/auth files
Write-Host "`n🔐 Removing old API/auth files..." -ForegroundColor Yellow
foreach ($file in $oldApiFiles) {
    Remove-SafelyFile $file
}

# Delete discovery/debug files
Write-Host "`n🔍 Removing discovery/debug files..." -ForegroundColor Yellow
foreach ($file in $discoveryFiles) {
    Remove-SafelyFile $file
}

# Delete test files
Write-Host "`n🧪 Removing test files..." -ForegroundColor Yellow
foreach ($file in $testFiles) {
    Remove-SafelyFile $file
}

# Delete utility files
Write-Host "`n🛠️ Removing utility files..." -ForegroundColor Yellow
foreach ($file in $utilityFiles) {
    Remove-SafelyFile $file
}

# Delete old documentation
Write-Host "`n📄 Removing old documentation..." -ForegroundColor Yellow
foreach ($file in $oldDocs) {
    Remove-SafelyFile $file
}

# Delete commit message files
Write-Host "`n📝 Removing commit message files..." -ForegroundColor Yellow
foreach ($file in $commitFiles) {
    Remove-SafelyFile $file
}

# Delete old config files
Write-Host "`n⚙️ Removing old config files..." -ForegroundColor Yellow
foreach ($file in $oldConfigFiles) {
    Remove-SafelyFile $file
}

# Delete old directories
Write-Host "`n📁 Removing old directories..." -ForegroundColor Yellow
foreach ($dir in $oldDirs) {
    Remove-SafelyDir $dir
}

# Delete empty file
if (Test-Path "{") {
    Remove-Item "{" -Force
    Write-Host "  ✅ Deleted: {" -ForegroundColor Green
}

Write-Host "`n✅ Cleanup complete!" -ForegroundColor Green
Write-Host "`n📊 Remaining files:" -ForegroundColor Cyan
Write-Host "  ✅ production_api_bot.py (Active API bot)"
Write-Host "  ✅ fixed_graphql_client.py (GraphQL client)"
Write-Host "  ✅ .env (Environment variables)"
Write-Host "  ✅ requirements.txt (Dependencies)"
Write-Host "  ✅ .github/workflows/ (Active workflows)"
Write-Host "  ✅ elia-token-extension/ (Browser extension)"
Write-Host "  ✅ README.md (Main documentation)"
Write-Host "  ✅ WORKFLOWS_CLEANED.md (Recent docs)"
Write-Host "  ✅ BOT_COMMAND_FIX.md (Recent docs)"
Write-Host "  ✅ MISSING_FILES_FIXED.md (Recent docs)"

Write-Host "`n🎉 Repository is now clean and organized!" -ForegroundColor Green
