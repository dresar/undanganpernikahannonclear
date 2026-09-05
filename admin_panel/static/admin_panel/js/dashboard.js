// Dashboard JavaScript functionality

// Chart.js configuration for revenue chart
let revenueChart;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeRevenueChart();
    initializeModals();
    initializeFormHandlers();
    updateRealTimeData();
});

// Initialize revenue chart
function initializeRevenueChart() {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;

    // Get data from Django template variables (passed from view)
    const chartData = window.chartData || {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        data: [1200000, 1900000, 3000000, 5000000, 2300000, 3200000]
    };

    revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Revenue (Rp)',
                data: chartData.data,
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: 'white'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: 'white',
                        callback: function(value) {
                            return 'Rp ' + value.toLocaleString('id-ID');
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: 'white'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

// Modal functionality
function initializeModals() {
    // Get all modal elements
    const modals = {
        createOrder: document.getElementById('createOrderModal'),
        addTemplate: document.getElementById('addTemplateModal'),
        processPayment: document.getElementById('processPaymentModal')
    };

    // Add event listeners for modal close buttons
    Object.values(modals).forEach(modal => {
        if (modal) {
            const closeBtn = modal.querySelector('.close-modal');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => closeModal(modal.id));
            }

            // Close modal when clicking outside
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    closeModal(modal.id);
                }
            });
        }
    });

    // ESC key to close modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal:not(.hidden)');
            if (openModal) {
                closeModal(openModal.id);
            }
        }
    });
}

// Form handlers
function initializeFormHandlers() {
    // Create Order Form
    const createOrderForm = document.getElementById('createOrderForm');
    if (createOrderForm) {
        createOrderForm.addEventListener('submit', handleCreateOrder);
    }

    // Add Template Form
    const addTemplateForm = document.getElementById('addTemplateForm');
    if (addTemplateForm) {
        addTemplateForm.addEventListener('submit', handleAddTemplate);
    }

    // Process Payment Form
    const processPaymentForm = document.getElementById('processPaymentForm');
    if (processPaymentForm) {
        processPaymentForm.addEventListener('submit', handleProcessPayment);
    }
}

// Modal control functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        const firstInput = modal.querySelector('input, select, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
        
        // Reset form if exists
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }
    }
}

// Form submission handlers
function handleCreateOrder(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Creating...';
    submitBtn.disabled = true;
    
    // Submit to Django backend
    fetch('/admin-panel/orders/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Order created successfully!', 'success');
            closeModal('createOrderModal');
            refreshDashboardData();
        } else {
            showNotification(data.message || 'Error creating order', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Network error occurred', 'error');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

function handleAddTemplate(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Uploading...';
    submitBtn.disabled = true;
    
    // Submit to Django backend
    fetch('/admin-panel/templates/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Template added successfully!', 'success');
            closeModal('addTemplateModal');
            refreshDashboardData();
        } else {
            showNotification(data.message || 'Error adding template', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Network error occurred', 'error');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

function handleProcessPayment(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Processing...';
    submitBtn.disabled = true;
    
    // Submit to Django backend
    fetch('/admin-panel/payments/process/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Payment processed successfully!', 'success');
            closeModal('processPaymentModal');
            refreshDashboardData();
        } else {
            showNotification(data.message || 'Error processing payment', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Network error occurred', 'error');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// Order management functions
function viewOrder(orderId) {
    window.location.href = `/admin-panel/orders/${orderId}/`;
}

function editOrder(orderId) {
    window.location.href = `/admin-panel/orders/${orderId}/edit/`;
}

// Utility functions
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full ${
        type === 'success' ? 'bg-green-600 text-white' :
        type === 'error' ? 'bg-red-600 text-white' :
        type === 'warning' ? 'bg-yellow-600 text-white' :
        'bg-blue-600 text-white'
    }`;
    
    notification.innerHTML = `
        <div class="flex items-center space-x-2">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function refreshDashboardData() {
    // Refresh dashboard statistics and recent data
    fetch('/admin-panel/dashboard/refresh/', {
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateDashboardStats(data.stats);
            updateRecentOrders(data.recent_orders);
            updateRecentActivities(data.recent_activities);
            updateRevenueChart(data.chart_data);
        }
    })
    .catch(error => {
        console.error('Error refreshing dashboard:', error);
    });
}

function updateDashboardStats(stats) {
    // Update quick stats
    const statElements = {
        'total-orders': stats.total_orders,
        'monthly-revenue': stats.monthly_revenue,
        'total-templates': stats.total_templates,
        'total-users': stats.total_users
    };
    
    Object.entries(statElements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

function updateRecentOrders(orders) {
    // Update recent orders table
    const tbody = document.querySelector('#recent-orders-table tbody');
    if (tbody && orders) {
        tbody.innerHTML = orders.map(order => `
            <tr class="border-b border-gray-800 hover:bg-gray-800/50">
                <td class="py-3 px-4 text-white">#${order.id}</td>
                <td class="py-3 px-4 text-white">${order.customer_name}</td>
                <td class="py-3 px-4 text-white">${order.template_name || 'No Template'}</td>
                <td class="py-3 px-4 text-white">Rp ${order.total_amount.toLocaleString('id-ID')}</td>
                <td class="py-3 px-4">
                    <span class="${getStatusClass(order.status)} px-2 py-1 rounded-full text-xs">${order.status}</span>
                </td>
                <td class="py-3 px-4">
                    <button onclick="viewOrder('${order.id}')" class="text-blue-400 hover:text-blue-300 mr-2">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="editOrder('${order.id}')" class="text-yellow-400 hover:text-yellow-300">
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }
}

function updateRecentActivities(activities) {
    // Update recent activities
    const container = document.querySelector('#recent-activities');
    if (container && activities) {
        container.innerHTML = activities.map(activity => `
            <div class="activity-item p-3 rounded-lg">
                <div class="flex items-center space-x-3">
                    <div class="w-2 h-2 ${getActivityColor(activity.action)} rounded-full"></div>
                    <div class="flex-1">
                        <p class="text-sm text-white">${activity.description}</p>
                        <p class="text-xs text-gray-400">${activity.time_ago}</p>
                    </div>
                </div>
            </div>
        `).join('');
    }
}

function updateRevenueChart(chartData) {
    if (revenueChart && chartData) {
        revenueChart.data.labels = chartData.labels;
        revenueChart.data.datasets[0].data = chartData.data;
        revenueChart.update();
    }
}

function getStatusClass(status) {
    const statusClasses = {
        'paid': 'bg-green-900 text-green-300',
        'pending': 'bg-yellow-900 text-yellow-300',
        'failed': 'bg-red-900 text-red-300',
        'completed': 'bg-green-900 text-green-300',
        'processing': 'bg-blue-900 text-blue-300'
    };
    return statusClasses[status] || 'bg-gray-900 text-gray-300';
}

function getActivityColor(action) {
    const actionColors = {
        'create': 'bg-green-500',
        'update': 'bg-blue-500',
        'delete': 'bg-red-500',
        'login': 'bg-purple-500'
    };
    return actionColors[action] || 'bg-yellow-500';
}

// Real-time data updates
function updateRealTimeData() {
    // Update dashboard data every 30 seconds
    setInterval(() => {
        refreshDashboardData();
    }, 30000);
}

// Export functions for global access
window.dashboardFunctions = {
    openModal,
    closeModal,
    viewOrder,
    editOrder,
    refreshDashboardData
};