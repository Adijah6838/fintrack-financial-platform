# FINTRACK: Financial Platform UI & Analytics

## Project Description
A high-fidelity, responsive financial platform that allows users to manage accounts, execute financial transactions, and review suspicious activity. This project focuses on seamless REST API integration, complex state management, and premium UI/UX design, alongside a data-heavy administrative dashboard for monitoring platform health.

## Technologies Used
- **Frontend:** HTML5, CSS3 (Flexbox/Grid, Glassmorphism), Vanilla JavaScript (ES6+).
- **Libraries & Data Viz:** Bootstrap 5, Chart.js (Bar charts, Doughnut charts), Bootstrap Icons.
- **Backend Integration:** REST API (Python/Flask).
- **Testing:** Pytest (25 automated tests).

## Objective Success Criteria

### Challenge 1: Customer Financial Dashboard
1. **Authentication:** Users must authenticate via JWT; unauthorized users are redirected.
2. **State Management:** The "Total Net Worth" must calculate and update dynamically based on the sum of all active account balances.
3. **API Integration:** Form submissions must use the `Idempotency-Key` header to prevent duplicate financial transactions on network retries.
4. **UX Loading States:** Data fetching must display skeleton loaders instead of blank screens to improve perceived performance.
5. **Responsive Design:** The interface must be fully functional on mobile (375px) and desktop (1440px).

### Challenge 2: Admin Analytics & Fraud Review UI
1. **RBAC (Role-Based Access Control):** Only users with the `ADMIN` role can access this dashboard (verified via JWT claims).
2. **Data Visualization:** A Bar chart must render transaction volume (last 7 days) and a Doughnut chart must render the status breakdown (Success/Failed/Pending).
3. **Fraud Review Workflow:** Admin must be able to click "Confirm" or "Dismiss" on a fraud alert, triggering a PATCH request that updates the UI state instantly.
4. **Real-time Metrics:** All stat cards (Total Users, Total Volume, High-Risk Alerts) must be populated from a real-time aggregate database endpoint, with zero hardcoded values.

## How to Run the Working Reference Implementation Locally
1. Clone this repository.
2. Ensure Python 3.10+ is installed.
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
