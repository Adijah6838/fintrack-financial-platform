let userAccounts = [];

// Fetch accounts when page loads
document.addEventListener('DOMContentLoaded', () => {
    fetchAccounts();
    updateFormFields(); // Initialize transaction form
});

async function fetchAccounts() {
    try {
        const { response, data } = await apiFetch('/api/accounts');
        
        if (response.ok) {
            userAccounts = data.data;
            renderAccounts();
            populateAccountDropdowns();
        }
    } catch (error) {
        showAlert('Failed to load accounts.', 'danger');
    }
}

function renderAccounts() {
    const container = document.getElementById('accountsContainer');
    container.innerHTML = '';

    if (userAccounts.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <h4 class="text-muted">You don't have any accounts yet.</h4>
                <p>Click "Create New Account" to get started.</p>
            </div>
        `;
        return;
    }

    userAccounts.forEach(acc => {
        const isActive = acc.status === 'ACTIVE';
        const statusBadge = isActive ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-danger">Frozen</span>';
        
        container.innerHTML += `
            <div class="col-md-4 mb-4">
                <div class="card h-100 shadow-sm border-0 stat-card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h6 class="text-muted mb-0">${acc.account_type}</h6>
                            ${statusBadge}
                        </div>
                        <h2 class="card-title fw-bold">$${acc.balance}</h2>
                        <p class="card-text text-muted small mb-0">Account: ****${acc.account_number.slice(-4)}</p>
                        <p class="card-text text-muted small">Number: ${acc.account_number}</p>
                    </div>
                </div>
            </div>
        `;
    });
}

function populateAccountDropdowns() {
    const sourceSelect = document.getElementById('sourceAccount');
    const destSelect = document.getElementById('destAccount');
    
    sourceSelect.innerHTML = '';
    destSelect.innerHTML = '';

    userAccounts.forEach(acc => {
        const option = `<option value="${acc.account_number}">${acc.account_type} (${acc.account_number}) - $${acc.balance}</option>`;
        sourceSelect.innerHTML += option;
        destSelect.innerHTML += option;
    });
}

async function createAccount() {
    try {
        const { response, data } = await apiFetch('/api/accounts', {
            method: 'POST',
            body: JSON.stringify({ account_type: 'PERSONAL' })
        });

        if (response.ok) {
            showAlert('Account created successfully!', 'success');
            fetchAccounts(); // Reload the cards
        } else {
            showAlert(data.message, 'danger');
        }
    } catch (error) {
        showAlert('An error occurred.', 'danger');
    }
}

function updateFormFields() {
    const type = document.getElementById('txnType').value;
    const sourceDiv = document.getElementById('sourceAccountDiv');
    const destDiv = document.getElementById('destAccountDiv');
    const destLabel = document.querySelector('label[for="destAccountDiv"]') || destDiv.previousElementSibling;

    if (type === 'DEPOSIT') {
        sourceDiv.style.display = 'none';
        destDiv.style.display = 'block';
    } else if (type === 'WITHDRAWAL') {
        sourceDiv.style.display = 'block';
        destDiv.style.display = 'none';
    } else if (type === 'TRANSFER') {
        sourceDiv.style.display = 'block';
        destDiv.style.display = 'block';
    }
}

// Handle Transaction Submission
document.getElementById('transactionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.innerText = 'Processing...';

    const type = document.getElementById('txnType').value;
    const amount = parseFloat(document.getElementById('txnAmount').value);
    
    // Generate a unique idempotency key for the request using crypto
    const idempotencyKey = crypto.randomUUID();

    let payload = { amount: amount };
    
    if (type === 'DEPOSIT') {
        payload.destination_account_number = document.getElementById('destAccount').value;
    } else if (type === 'WITHDRAWAL') {
        payload.source_account_number = document.getElementById('sourceAccount').value;
    } else if (type === 'TRANSFER') {
        payload.source_account_number = document.getElementById('sourceAccount').value;
        payload.destination_account_number = document.getElementById('destAccount').value;
    }

    try {
        const { response, data } = await apiFetch(`/api/transactions/${type.toLowerCase()}`, {
            method: 'POST',
            headers: { 'Idempotency-Key': idempotencyKey },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            showAlert(`Successfully completed ${type}!`, 'success');
            document.getElementById('txnAmount').value = '';
            fetchAccounts(); // Refresh balances
        } else {
            showAlert(data.message, 'danger');
        }
    } catch (error) {
        showAlert('Transaction failed.', 'danger');
    } finally {
        btn.disabled = false;
        btn.innerText = 'Submit Transaction';
    }
});