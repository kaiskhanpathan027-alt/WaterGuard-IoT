/**
 * Chart.js Integration for Water Quality Monitoring Dashboard
 */

document.addEventListener('DOMContentLoaded', function () {
    const trendCanvas = document.getElementById('trendChart');
    const statusCanvas = document.getElementById('statusChart');

    if (!trendCanvas && !statusCanvas) return;

    // Fetch dynamic chart payload from backend API
    const isGlobal = window.location.pathname.includes('/admin');
    const apiUrl = `/api/dashboard-charts?scope=${isGlobal ? 'all' : 'user'}`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            initStatusChart(data.status_distribution);
            initTrendChart(data.trends);
        })
        .catch(err => {
            console.error('Failed to load chart data:', err);
        });

    let trendChartInstance = null;

    function initStatusChart(dist) {
        if (!statusCanvas || typeof Chart === 'undefined') return;

        const ctx = statusCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: dist.labels,
                datasets: [{
                    data: dist.data,
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { family: 'Inter', size: 12, weight: '500' },
                            padding: 16,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const val = context.parsed;
                                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                                return ` ${context.label}: ${val} tests (${pct}%)`;
                            }
                        }
                    }
                },
                cutout: '68%'
            }
        });
    }

    function initTrendChart(trend) {
        if (!trendCanvas || typeof Chart === 'undefined') return;

        const ctx = trendCanvas.getContext('2d');
        const labels = trend.labels.length > 0 ? trend.labels : ['No Data'];
        const sampleNames = trend.sample_names || [];

        trendChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'WQI Score (0-100)',
                        data: trend.wqi,
                        borderColor: '#0284c7',
                        backgroundColor: 'rgba(2, 132, 199, 0.1)',
                        borderWidth: 3,
                        tension: 0.35,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'pH Level',
                        data: trend.ph,
                        borderColor: '#10b981',
                        borderWidth: 2,
                        borderDash: [4, 4],
                        tension: 0.3,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Turbidity (NTU)',
                        data: trend.turbidity,
                        borderColor: '#f59e0b',
                        borderWidth: 2,
                        tension: 0.3,
                        yAxisID: 'y'
                    },
                    {
                        label: 'TDS (mg/L)',
                        data: trend.tds,
                        borderColor: '#8b5cf6',
                        borderWidth: 2,
                        tension: 0.3,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            font: { family: 'Inter', size: 11, weight: '600' },
                            usePointStyle: true,
                            padding: 12
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: function (items) {
                                const idx = items[0].dataIndex;
                                return sampleNames[idx] ? `${sampleNames[idx]} (${items[0].label})` : items[0].label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { font: { family: 'Inter', size: 10 } }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'WQI / pH / Turbidity', font: { size: 10 } },
                        suggestedMin: 0,
                        suggestedMax: 100,
                        grid: { color: '#f1f5f9' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'TDS (mg/L)', font: { size: 10 } },
                        suggestedMin: 0,
                        suggestedMax: 1500,
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }

    // Toggle filter buttons for Trend Chart
    window.toggleChartDataset = function (datasetIndex) {
        if (!trendChartInstance) return;
        const meta = trendChartInstance.getDatasetMeta(datasetIndex);
        meta.hidden = meta.hidden === null ? !trendChartInstance.data.datasets[datasetIndex].hidden : null;
        trendChartInstance.update();
    };
});
