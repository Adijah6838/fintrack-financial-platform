document.addEventListener('DOMContentLoaded', () => {
    fetchAdminData();
});

async function fetchAdminData() {
    try {
        const { response, data } = await apiFetch('/api/admin/overview');

        if (response.ok) {
            renderStats(data.data.stats);
            renderCharts(data.data.stats, data.data.charts.volume_by_day);
            renderTables(data.data.recent_transactions, data.data.recent_audit_logs);
        } else {
            showAlert(data.message || 'Failed to load admin data.', 'danger');
        }
    } catch (error) {
        showAlert('Failed to connect to server.', 'danger');
    }
}

function renderStats(stats) {
    const container = document.getElementById('statsRow');
    container.innerHTML = `
        <div class="col-md-3 mb-3">
            <div class="stat-card">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="stat-label">Total Users</div>
                        <h3 class="stat-value">${stats.total_users}</h3>
                    </div>
                    <div class="icon-box bg-primary bg-opacity-10 text-primary">
                        <i class="bi bi-people"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="stat-card">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="stat-label">Active Accounts</div>
                        <h3 class="stat-value">${stats.active_accounts}</h3>
                    </div>
                    <div class="icon-box bg-success bg-opacity-10 text-success">
                        <i class="bi bi-wallet2"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="stat-card">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="stat-label">Total Volume</div>
                        <h3 class="stat-value">$${parseFloat(stats.total_volume).toLocaleString(undefined, {minimumFractionDigits: 2})}</h3>
                    </div>
                    <div class="icon-box bg-info bg-opacity-10 text-info">
                        <i class="bi bi-currency-dollar"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="stat-card">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="stat-label">High Risk Alerts</div>
                        <h3 class="stat-value">${stats.high_risk_alerts}</h3>
                    </div>
                    <div class="icon-box bg-danger bg-opacity-10 text-danger">
                        <i class="bi bi-exclamation-triangle"></i>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderCharts(stats, volumeData) {
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = '#64748b';

    // 1. Transaction Volume Bar Chart
    const ctxVolume = document.getElementById('volumeChart').getContext('2d');
    
    // Create gradient for the bars
    let gradient = ctxVolume.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, '#3b82f6');
    gradient.addColorStop(1, '#93c5fd');

    const labels = volumeData.map(item => item.date);
    const amounts = volumeData.map(item => item.amount);

    new Chart(ctxVolume, {
        type: 'bar',
        data: {
            labels: labels.length ? labels : ['No Data'],
            datasets: [{
                label: 'Volume ($)',
                data: amounts.length ? amounts : [0],
                backgroundColor: gradient,
                borderRadius: 6,
                maxBarThickness: 50,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0f172a',
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: false
                }
            },
            scales: {
                y: { 
                    beginAtZero: true, 
                    grid: { borderDash: [4, 4], color: '#f1f5f9' },
                    border: { display: false },
                    ticks: { callback: (value) => '$' + value }
                },
                x: { 
                    grid: { display: false },
                    border: { display: false }
                }
            }
        }
    });

    // 2. Transaction Status Doughnut Chart
    const totalTxns = stats.successful_transactions + stats.failed_transactions + stats.pending_transactions;
    document.getElementById('chartTotalTxn').innerText = totalTxns;

    const ctxStatus = document.getElementById('statusChart').getContext('2d');
    new Chart(ctxStatus, {
        type: 'doughnut',
        data: {
            labels: ['Successful', 'Failed', 'Pending'],
            datasets: [{
                data: [stats.successful_transactions, stats.failed_transactions, stats.pending_transactions],
                backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '80%',
            plugins: { legend: { display: false } }
        }
    });
}

function renderTables(transactions, logs) {
    // 1. Recent Transactions
    const txnBody = document.getElementById('recentTxnsTable');
    txnBody.innerHTML = '';
    
    if (transactions.length === 0) {
        txnBody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-muted">No transactions found.</td></tr>';
    } else {
        transactions.forEach(t => {
            const badge = t.status === 'COMPLETED' ? 'bg-soft-success' : (t.status === 'FAILED' ? 'bg-soft-danger' : 'bg-soft-warning');
            
            // Format Date to a nice short string (e.g. "Nov 4, 08:00")
            const dateObj = new Date(t.created_at);
            const timeStr = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

            txnBody.innerHTML += `
                <tr>
                    <td>
                        <div class="fw-medium text-dark">${t.reference}</div>
                        <div class="text-muted small" style="font-size: 0.75rem;">${timeStr}</div>
                    </td>
                    <td class="text-muted">${t.type}</td>
                    <td class="fw-medium">$${t.amount}</td>
                    <td class="text-end"><span class="badge ${badge}">${t.status}</span></td>
                </tr>
            `;
        });
    }

    // 2. Recent Audit Logs
    const logBody = document.getElementById('recentLogsTable');
    logBody.innerHTML = '';
    
    if (logs.length === 0) {
        logBody.innerHTML = '<tr><td colspan="2" class="text-center py-4 text-muted">No logs found.</td></tr>';
    } else {
        logs.forEach(l => {
            // Format Date
            const dateObj = new Date(l.created_at);
            const timeStr = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

            logBody.innerHTML += `
                <tr>
                    <td>
                        <span class="badge bg-soft-secondary border border-secondary border-opacity-10">${l.event}</span>
                        <div class="text-muted mt-1" style="font-size: 0.75rem;">${timeStr}</div>
                    </td>
                    <td class="text-muted small">${l.description}</td>
                </tr>
            `;
        });
    }
}