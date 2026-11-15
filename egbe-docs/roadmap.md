# Egbe Operating Roadmap

## Current status
- Workspace established for project setup.
- Egbe secure connection is pending the private `OS_API_KEY`.
- Session logging is intentionally enabled in the project settings for this workspace, but final remote activation remains pending authorisation from the private Egbe connection.
- Recurring operational tasks were created with explicit approval and follow the weekly cadence during active outreach/campaign windows.

## Recommended milestone sequence

### Milestone 1: Secure Egbe connection and verification
- Save the private `OS_API_KEY` in `.env.local` and keep it ignored by git.
- Verify project identity and available Egbe limits.
- Enable session logging only after explicit consent and successful verification.

### Milestone 2: Cold outreach engine for program officers
- Research foundations and grantmaking priorities.
- Capture structured prospect records in `grants/prospects.json`.
- Prepare LOI/introduction email templates by mission fit and officer priority.
- Track outreach status, follow-ups, and reply windows.

### Milestone 3: Donor portal and payment flow
- Define the donor landing page user journey.
- Build a responsive donor portal experience.
- Integrate Stripe for one-time and recurring donations.
- Store donor profiles and payment metadata securely.

### Milestone 4: Receipts and stewardship automation
- Trigger immediate tax-exempt receipt email.
- Send gratitude notes and post-donation follow-up.
- Keep stewardship records and status logs in the project workspace.

### Milestone 5: Launch and operating review
- Validate the full funnel from donor page to receipt.
- Run grant outreach tests and response tracking.
- Review conversion, response rate, and donor retention metrics.

## Review cadence
- Approved default operating cadence: weekly review during active outreach/campaign windows.
- Use this cadence for grant prospecting, campaign launches, donor conversion pushes, and stewardship bursts.
- Every review should answer: what shipped, what blocked us, what is next, and what decision is needed.

## Decision checkpoint
- I will not create a recurring reporting loop or scheduled task until you explicitly approve it.
