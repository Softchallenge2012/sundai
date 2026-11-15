# Sundai: AI-Powered Nonprofit Growth & Engagement Suite

## Background
Nonprofit organizations and advocacy groups often face severe resource constraints when trying to scale their impact. Securing critical funding requires extensive hours of manual prospect research, tracking foundation giving criteria, and crafting tailored outreach to program officers. Simultaneously, building trustworthy digital infrastructure—such as secure donation portals, payment processing, and automated receipt delivery—traditionally demands expensive engineering overhead or fragmented tools. 

Sundai bridges this gap by leveraging autonomous coding agents and modern cloud infrastructure to automate both philanthropic fundraising operations and donor engagement loops.

## Mission
To empower nonprofits, charities, and mission-driven builders with intelligent, autonomous workflows that streamline grant acquisition, automate supporter outreach, and establish secure, frictionless payment and data infrastructure with minimal manual overhead.

---

## Functionality

### Module 1: Cold Outreach to Program Officers
Automates prospect research, data enrichment, personalized drafting, and tracking of grant communications.
* **Prospect Discovery & Data Ingestion:** Directs your coding agent using [Research, data and AI](https://docs.egbe.ai/infrastructure/research-and-data/) capabilities to search grant databases (such as Candid/Foundation Directory) and foundation websites, scraping giving ranges, priorities, past grantees, and contact details into a structured `grants/prospects.json` artifact.
* **Drafting Tailored Outreach:** Cross-references your nonprofit’s core mission against each foundation’s specific guidelines using [Customer acquisition](https://docs.egbe.ai/guides/acquisition/) and [Advertising and outreach](https://docs.egbe.ai/infrastructure/advertising-and-outreach/) scripts to generate customized Letters of Inquiry (LOIs) and introduction emails.
* **Execution & Follow-up:** Integrates email delivery and CRM endpoints via [Analytics and email](https://docs.egbe.ai/infrastructure/analytics-and-email/) services to send communications and logs responses, while scheduling [Recurring work](https://docs.egbe.ai/guides/continuity/) check-ins to track deadlines and reply statuses.

### Module 2: Custom Donor Portal & Payment Flow
Builds a secure landing page for supporters, integrates recurring/one-time contributions, and ensures a smooth checkout experience.
* **Scaffolding & Frontend Build:** Instructs coding agents via the [Engineering Loop](https://docs.egbe.ai/guides/engineering-loop/) to build responsive web apps (using Next.js, React, or Tailwind CSS) featuring impact metrics, campaign stories, and custom donation tiers ($50, $250, $1,000, or custom amounts).
* **Payment Integration:** Wires up managed **Stripe checkout** infrastructure via [Accounts and payments](https://docs.egbe.ai/infrastructure/accounts-and-payments/) to handle secure credit card, Apple Pay, and ACH transactions with custom metadata and recurring monthly giving options.
* **Database & Automated Receipts:** Provisions secure data storage through [Hosting and data](https://docs.egbe.ai/infrastructure/hosting-and-data/) to log donor profiles and transaction IDs, triggering instant tax-exempt receipts and gratitude notes via [Analytics and email](https://docs.egbe.ai/infrastructure/analytics-and-email/).
* **End-to-End Verification:** Runs verification playbooks to simulate test-mode transactions, verify webhook delivery, and ensure receipts land correctly in inboxes prior to production deployment.

---

## Technical Details & Architecture

Sundai is structured as a modular, agent-driven repository utilizing modern web frameworks and cloud infrastructure components:

* **Frontend Frameworks:** Responsive single-page applications and donor portals built using React / Next.js or static HTML/Tailwind.
* **Agentic Orchestration:** Powered by coding agents directed through custom scripts and structured data artifacts (`grants/prospects.json`).
* **Payment & Transaction Layer:** Managed **Stripe** infrastructure handling secure multi-payment methods (Cards, Apple Pay, ACH) and webhook event verification.
* **Data & Hosting Infrastructure:** Secure backend database provisioning for donor profile management, transaction logging, and automated notification triggers.
