# GitHub Actions Secrets Setup

To set up the GitHub Actions for midnight execution, you need to configure the following secrets in your GitHub repository:

## Required Secrets

1. **ELIA_GRAPHQL_TOKEN** - Your Elia API authentication token
2. **EMAIL_ADDRESS** - Your email address for notifications
3. **SMTP_PASSWORD** - Your SMTP password (or leave empty for Videotron internal)
4. **SMTP_HOST** - SMTP server (e.g., smtp-int.int.videotron.com)
5. **SMTP_PORT** - SMTP port (e.g., 25)
6. **ELIA_EMAIL** - Your Elia account email
7. **TOTP_SECRET** - Your 2FA secret for Microsoft authentication
8. **MICROSOFT_USERNAME** - Your Microsoft account email

## Setup Steps

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each secret above
4. Add the exact values from your `.env` file

## Schedule Configuration

The workflow is configured to run:
- **Cron:** `0 5 * * 1-5` (Monday-Friday at 5:00 UTC)
- **Local Time:** Midnight Eastern Time (adjust for DST)
- **Manual:** Can also be triggered manually via **Actions** tab

## Time Zone Notes

- 5:00 UTC = Midnight EST (UTC-5)
- 4:00 UTC = Midnight EDT (UTC-4) 
- The schedule uses UTC to ensure consistent timing
- GitHub Actions runs exactly on schedule (no 18-minute delays!)

## Testing

1. Push the workflow to GitHub
2. Go to **Actions** tab
3. Click **"Parking Bot Midnight Run"**
4. Click **"Run workflow"** to test manually
5. Check logs to verify everything works

## Monitoring

- Check the **Actions** tab daily for execution results
- Email notifications will be sent for success/failure
- Logs are saved as artifacts for debugging
