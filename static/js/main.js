document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('sslCheckForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Show loading
        loading.classList.remove('d-none');
        results.innerHTML = '';

        const formData = new FormData(form);

        try {
            const response = await fetch('/check_ssl', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                results.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                return;
            }

            displayResults(data.results);
        } catch (error) {
            results.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        } finally {
            loading.classList.add('d-none');
        }
    });

    function displayResults(sslResults) {
        const resultsHtml = sslResults.map(result => {
            const statusClass = result.status === 'valid' ? 'status-valid' : 'status-error';
            const daysRemainingClass = result.days_remaining > 30 ? 'text-success' :
                result.days_remaining > 7 ? 'text-warning' : 'text-danger';

            // Tạo URL với https://
            const domainUrl = `https://${result.domain}`;

            return `
                <div class="card result-card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h5 class="card-title mb-0">
                                <a href="${domainUrl}" target="_blank" class="domain-link">
                                    ${result.domain}
                                    <i class="fas fa-external-link-alt ms-2"></i>
                                </a>
                            </h5>
                            <span class="ssl-status ${statusClass}">${result.status}</span>
                        </div>
                        ${result.error ? `
                            <p class="text-danger mb-0">${result.error}</p>
                        ` : `
                            <div class="row">
                                <div class="col-md-6">
                                    <p class="mb-1"><strong>Issuer:</strong> ${result.issuer}</p>
                                    <p class="mb-1"><strong>Valid From:</strong> ${result.valid_from}</p>
                                    <p class="mb-1"><strong>Valid To:</strong> ${result.valid_to}</p>
                                </div>
                                <div class="col-md-6">
                                    <p class="mb-1 ${daysRemainingClass}">
                                        <strong>Days Remaining:</strong> ${result.days_remaining}
                                    </p>
                                </div>
                            </div>
                        `}
                    </div>
                </div>
            `;
        }).join('');

        results.innerHTML = resultsHtml;
    }
}); 