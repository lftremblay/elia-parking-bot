# Chrome Extension Integration Specification
## Option 1: Direct File Access for Vacation Dates

### Overview
Chrome extension will write vacation dates directly to `vacation_dates.txt` file in the bot's directory.

### File Requirements
- **Location**: Same directory as `production_api_bot.py`
- **Filename**: `vacation_dates.txt`
- **Format**: Comma-separated dates in YYYY-MM-DD format
- **Example**: `2025-12-24,2025-12-25,2026-01-01`

### Chrome Extension Implementation

#### 1. Manifest Permissions
Add to `manifest.json`:
```json
{
  "name": "Elia Parking Assistant",
  "permissions": [
    "activeTab",
    "storage"
  ],
  "web_accessible_resources": [{
    "resources": ["vacation_dates.txt"],
    "matches": ["<all_urls>"]
  }]
}
```

#### 2. File Writing Function
```javascript
// Function to write vacation dates to file
async function writeVacationDates(dates) {
  try {
    // Format dates as comma-separated string
    const datestring = dates.join(',');
    
    // Create blob with vacation dates
    const blob = new Blob([datestring], { type: 'text/plain' });
    
    // Create download link and trigger download
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'vacation_dates.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log('Vacation dates written to vacation_dates.txt');
  } catch (error) {
    console.error('Failed to write vacation dates:', error);
  }
}
```

#### 3. Date Detection Logic
```javascript
// Function to detect vacation dates from Elia UI
function detectVacationDates() {
  const vacationDates = [];
  
  // Look for vacation/skip indicators in Elia interface
  // This depends on how Elia displays vacation days
  
  // Example: Look for elements with vacation class
  const vacationElements = document.querySelectorAll('.vacation-day, .skip-day, [data-vacation="true"]');
  
  vacationElements.forEach(element => {
    const date = element.getAttribute('data-date') || 
                 element.textContent.match(/\d{4}-\d{2}-\d{2}/);
    if (date) {
      vacationDates.push(date);
    }
  });
  
  return vacationDates;
}
```

#### 4. Integration Points
```javascript
// Call this when user marks/unmarks vacation days
function onVacationDayToggle() {
  const vacationDates = detectVacationDates();
  writeVacationDates(vacationDates);
}

// Also call on page load to ensure file is current
document.addEventListener('DOMContentLoaded', function() {
  // Monitor for changes in vacation indicators
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.target.classList.contains('vacation-day') || 
          mutation.target.classList.contains('skip-day')) {
        onVacationDayToggle();
      }
    });
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['class', 'data-vacation']
  });
});
```

### Bot Integration (Already Complete)
✅ Bot reads `vacation_dates.txt` on each run
✅ Handles missing file gracefully
✅ Logs found vacation dates
✅ Skips booking on vacation dates

### Testing Procedure
1. Create test file: `vacation_dates.txt` with `2025-12-24`
2. Run bot: Should skip Dec 24th
3. Modify file: Add `2025-12-25`
4. Run bot: Should skip both Dec 24th and 25th
5. Delete file: Bot should warn and book all weekdays

### Error Handling
- Extension: Log errors to console, retry on failure
- Bot: Continue with warning if file missing/invalid
- File: Validate date format before writing

### Security Considerations
- File access limited to bot directory
- Date format validation prevents injection
- No sensitive data stored in file

### Maintenance
- Monitor Elia UI changes that affect vacation detection
- Update selectors if interface changes
- Log file operations for debugging

### Next Steps
1. Implement file writing in extension
2. Test with sample vacation dates
3. Verify bot reads and skips correctly
4. Deploy to production environment
