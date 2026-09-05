// Template Editor Utilities
// Helper functions and utilities for the template editor

class TemplateUtils {
    constructor() {
        this.debounceTimers = new Map();
        this.apiEndpoints = {
            save: '/template_editor/save/',
            load: '/template_editor/load/',
            export: '/template_editor/export/',
            components: '/template_editor/api/components/',
            palettes: '/template_editor/api/palettes/',
            fonts: '/template_editor/api/fonts/',
            aiGenerate: '/template_editor/api/ai/generate/'
        };
    }
    
    // Debounce function to limit API calls
    debounce(func, delay, key = 'default') {
        if (this.debounceTimers.has(key)) {
            clearTimeout(this.debounceTimers.get(key));
        }
        
        const timer = setTimeout(() => {
            func();
            this.debounceTimers.delete(key);
        }, delay);
        
        this.debounceTimers.set(key, timer);
    }
    
    // Generate unique ID
    generateId(prefix = 'id') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    // Get CSRF token for Django
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Fallback: try to get from meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        return csrfMeta ? csrfMeta.getAttribute('content') : '';
    }
    
    // Make API request with proper headers
    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    // Save template data
    async saveTemplate(templateData) {
        try {
            const response = await this.apiRequest(this.apiEndpoints.save, {
                method: 'POST',
                body: JSON.stringify(templateData)
            });
            
            this.showNotification('Template saved successfully!', 'success');
            return response;
        } catch (error) {
            this.showNotification('Failed to save template', 'error');
            throw error;
        }
    }
    
    // Load template data
    async loadTemplate(templateId) {
        try {
            const response = await this.apiRequest(`${this.apiEndpoints.load}${templateId}/`);
            this.showNotification('Template loaded successfully!', 'success');
            return response;
        } catch (error) {
            this.showNotification('Failed to load template', 'error');
            throw error;
        }
    }
    
    // Export template
    async exportTemplate(templateId, format = 'html') {
        try {
            const response = await this.apiRequest(`${this.apiEndpoints.export}${templateId}/?format=${format}`);
            
            if (format === 'html') {
                this.downloadFile(response.html, `template_${templateId}.html`, 'text/html');
            } else if (format === 'zip') {
                // Handle zip download
                window.open(`${this.apiEndpoints.export}${templateId}/?format=zip`);
            }
            
            this.showNotification('Template exported successfully!', 'success');
            return response;
        } catch (error) {
            this.showNotification('Failed to export template', 'error');
            throw error;
        }
    }
    
    // Download file
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
    }
    
    // Show notification
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;
        
        // Add to container or create one
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto remove
        const timer = setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
        
        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            clearTimeout(timer);
            notification.remove();
        });
        
        // Animate in
        requestAnimationFrame(() => {
            notification.classList.add('notification-show');
        });
    }
    
    // Validate template data
    validateTemplate(templateData) {
        const errors = [];
        
        if (!templateData.name || templateData.name.trim() === '') {
            errors.push('Template name is required');
        }
        
        if (!templateData.html || templateData.html.trim() === '') {
            errors.push('Template HTML content is required');
        }
        
        if (templateData.name && templateData.name.length > 100) {
            errors.push('Template name must be less than 100 characters');
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }
    
    // Sanitize HTML content
    sanitizeHTML(html) {
        const div = document.createElement('div');
        div.innerHTML = html;
        
        // Remove script tags
        const scripts = div.querySelectorAll('script');
        scripts.forEach(script => script.remove());
        
        // Remove dangerous attributes
        const dangerousAttrs = ['onload', 'onerror', 'onclick', 'onmouseover', 'onfocus', 'onblur'];
        const allElements = div.querySelectorAll('*');
        
        allElements.forEach(element => {
            dangerousAttrs.forEach(attr => {
                if (element.hasAttribute(attr)) {
                    element.removeAttribute(attr);
                }
            });
        });
        
        return div.innerHTML;
    }
    
    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Get responsive preview sizes
    getResponsiveSizes() {
        return {
            desktop: { width: 1200, height: 800, name: 'Desktop' },
            tablet: { width: 768, height: 1024, name: 'Tablet' },
            mobile: { width: 375, height: 667, name: 'Mobile' }
        };
    }
    
    // Apply responsive view
    applyResponsiveView(viewType) {
        const sizes = this.getResponsiveSizes();
        const size = sizes[viewType];
        
        if (!size) return;
        
        const previewFrame = document.getElementById('preview-frame');
        if (previewFrame) {
            previewFrame.style.width = size.width + 'px';
            previewFrame.style.height = size.height + 'px';
            previewFrame.style.maxWidth = '100%';
            previewFrame.style.margin = '0 auto';
        }
        
        // Update active button
        const buttons = document.querySelectorAll('.responsive-btn');
        buttons.forEach(btn => btn.classList.remove('active'));
        
        const activeBtn = document.querySelector(`[data-view="${viewType}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }
    
    // Generate CSS from template data
    generateCSS(templateData) {
        let css = '';
        
        // Base styles
        css += `
            body {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            
            .template-container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
        `;
        
        // Add custom CSS if exists
        if (templateData.css) {
            css += '\n' + templateData.css;
        }
        
        // Add responsive styles
        css += `
            @media (max-width: 768px) {
                body {
                    padding: 10px;
                }
                
                .template-container {
                    padding: 20px;
                }
                
                .columns-component {
                    flex-direction: column;
                }
                
                .column {
                    margin-bottom: 20px;
                }
            }
        `;
        
        return css;
    }
    
    // Generate complete HTML document
    generateCompleteHTML(templateData) {
        const css = this.generateCSS(templateData);
        
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${templateData.name || 'Wedding Invitation'}</title>
    <style>
        ${css}
    </style>
</head>
<body>
    <div class="template-container">
        ${templateData.html || ''}
    </div>
    
    <script>
        // Basic interactivity
        document.addEventListener('DOMContentLoaded', function() {
            // RSVP button functionality
            const rsvpButtons = document.querySelectorAll('.btn-component');
            rsvpButtons.forEach(button => {
                button.addEventListener('click', function() {
                    alert('RSVP functionality would be implemented here');
                });
            });
            
            // Smooth scrolling for anchor links
            const anchorLinks = document.querySelectorAll('a[href^="#"]');
            anchorLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth' });
                    }
                });
            });
        });
    </script>
</body>
</html>`;
    }
    
    // Local storage helpers
    saveToLocalStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
            return false;
        }
    }
    
    loadFromLocalStorage(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Failed to load from localStorage:', error);
            return null;
        }
    }
    
    removeFromLocalStorage(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Failed to remove from localStorage:', error);
            return false;
        }
    }
    
    // Auto-save functionality
    setupAutoSave(getDataCallback, interval = 30000) {
        setInterval(() => {
            const data = getDataCallback();
            if (data) {
                this.saveToLocalStorage('template_autosave', {
                    ...data,
                    timestamp: Date.now()
                });
            }
        }, interval);
    }
    
    // Check for auto-saved data
    checkAutoSave() {
        const autoSaveData = this.loadFromLocalStorage('template_autosave');
        
        if (autoSaveData && autoSaveData.timestamp) {
            const timeDiff = Date.now() - autoSaveData.timestamp;
            const hoursDiff = timeDiff / (1000 * 60 * 60);
            
            if (hoursDiff < 24) { // Show recovery option if less than 24 hours old
                return autoSaveData;
            }
        }
        
        return null;
    }
    
    // Show recovery dialog
    showRecoveryDialog(autoSaveData, onRecover, onDiscard) {
        const modal = document.createElement('div');
        modal.className = 'recovery-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Recover Auto-saved Template</h3>
                </div>
                <div class="modal-body">
                    <p>We found an auto-saved version of your template from ${new Date(autoSaveData.timestamp).toLocaleString()}.</p>
                    <p>Would you like to recover it?</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" id="discard-recovery">Discard</button>
                    <button class="btn btn-primary" id="recover-template">Recover</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('#recover-template').addEventListener('click', () => {
            onRecover(autoSaveData);
            modal.remove();
        });
        
        modal.querySelector('#discard-recovery').addEventListener('click', () => {
            onDiscard();
            this.removeFromLocalStorage('template_autosave');
            modal.remove();
        });
    }
    
    // Initialize utilities
    init() {
        // Add notification styles if not present
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .notification-container {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    max-width: 400px;
                }
                
                .notification {
                    background: white;
                    border-radius: 6px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    margin-bottom: 10px;
                    opacity: 0;
                    transform: translateX(100%);
                    transition: all 0.3s ease;
                }
                
                .notification-show {
                    opacity: 1;
                    transform: translateX(0);
                }
                
                .notification-content {
                    padding: 16px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                
                .notification-success {
                    border-left: 4px solid #10b981;
                }
                
                .notification-error {
                    border-left: 4px solid #ef4444;
                }
                
                .notification-info {
                    border-left: 4px solid #3b82f6;
                }
                
                .notification-close {
                    background: none;
                    border: none;
                    font-size: 18px;
                    cursor: pointer;
                    color: #6b7280;
                    margin-left: 10px;
                }
                
                .recovery-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10001;
                }
                
                .recovery-modal .modal-content {
                    background: white;
                    border-radius: 8px;
                    max-width: 500px;
                    width: 90%;
                }
                
                .recovery-modal .modal-header {
                    padding: 20px 20px 0;
                }
                
                .recovery-modal .modal-body {
                    padding: 20px;
                }
                
                .recovery-modal .modal-footer {
                    padding: 0 20px 20px;
                    text-align: right;
                }
                
                .recovery-modal .btn {
                    margin-left: 10px;
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Initialize utilities when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.templateUtils = new TemplateUtils();
    window.templateUtils.init();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TemplateUtils;
}