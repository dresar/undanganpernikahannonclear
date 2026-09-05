// Template Editor Components
// Drag and drop components for the template editor

class TemplateComponents {
    constructor() {
        this.components = {
            text: {
                name: 'Text Block',
                icon: 'fas fa-font',
                html: '<div class="text-component editable" contenteditable="true">Click to edit text</div>',
                css: '.text-component { padding: 10px; margin: 5px; border: 1px dashed #ccc; min-height: 30px; }'
            },
            heading: {
                name: 'Heading',
                icon: 'fas fa-heading',
                html: '<h2 class="heading-component editable" contenteditable="true">Your Heading</h2>',
                css: '.heading-component { padding: 10px; margin: 10px 0; font-size: 2em; font-weight: bold; }'
            },
            image: {
                name: 'Image',
                icon: 'fas fa-image',
                html: '<div class="image-component"><img src="https://via.placeholder.com/300x200" alt="Placeholder" style="max-width: 100%; height: auto;"><div class="image-caption editable" contenteditable="true">Image caption</div></div>',
                css: '.image-component { text-align: center; margin: 10px 0; } .image-caption { font-style: italic; margin-top: 5px; }'
            },
            button: {
                name: 'Button',
                icon: 'fas fa-mouse-pointer',
                html: '<button class="btn-component editable" contenteditable="true">Click Me</button>',
                css: '.btn-component { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px; } .btn-component:hover { background: #0056b3; }'
            },
            divider: {
                name: 'Divider',
                icon: 'fas fa-minus',
                html: '<hr class="divider-component">',
                css: '.divider-component { border: none; height: 2px; background: #ddd; margin: 20px 0; }'
            },
            container: {
                name: 'Container',
                icon: 'fas fa-square',
                html: '<div class="container-component"><p class="editable" contenteditable="true">Container content</p></div>',
                css: '.container-component { padding: 20px; margin: 10px 0; border: 2px dashed #ccc; min-height: 100px; background: #f9f9f9; }'
            },
            columns: {
                name: 'Two Columns',
                icon: 'fas fa-columns',
                html: '<div class="columns-component"><div class="column"><p class="editable" contenteditable="true">Left column</p></div><div class="column"><p class="editable" contenteditable="true">Right column</p></div></div>',
                css: '.columns-component { display: flex; gap: 20px; margin: 10px 0; } .column { flex: 1; padding: 15px; border: 1px dashed #ccc; min-height: 100px; }'
            },
            list: {
                name: 'List',
                icon: 'fas fa-list',
                html: '<ul class="list-component"><li class="editable" contenteditable="true">List item 1</li><li class="editable" contenteditable="true">List item 2</li><li class="editable" contenteditable="true">List item 3</li></ul>',
                css: '.list-component { padding: 10px; margin: 10px 0; } .list-component li { margin: 5px 0; padding: 5px; }'
            },
            quote: {
                name: 'Quote',
                icon: 'fas fa-quote-left',
                html: '<blockquote class="quote-component"><p class="editable" contenteditable="true">"Your inspiring quote goes here"</p><cite class="editable" contenteditable="true">- Author Name</cite></blockquote>',
                css: '.quote-component { padding: 20px; margin: 20px 0; border-left: 4px solid #007bff; background: #f8f9fa; font-style: italic; } .quote-component cite { display: block; margin-top: 10px; font-weight: bold; }'
            },
            video: {
                name: 'Video',
                icon: 'fas fa-video',
                html: '<div class="video-component"><div class="video-placeholder"><i class="fas fa-play-circle"></i><p>Click to add video</p></div></div>',
                css: '.video-component { margin: 20px 0; text-align: center; } .video-placeholder { padding: 60px; border: 2px dashed #ccc; background: #f9f9f9; } .video-placeholder i { font-size: 3em; color: #007bff; margin-bottom: 10px; }'
            }
        };
        
        this.initializeComponents();
        this.setupDragAndDrop();
    }
    
    initializeComponents() {
        const componentsContainer = document.getElementById('components-list');
        if (!componentsContainer) return;
        
        Object.keys(this.components).forEach(key => {
            const component = this.components[key];
            const componentElement = this.createComponentElement(key, component);
            componentsContainer.appendChild(componentElement);
        });
    }
    
    createComponentElement(key, component) {
        const div = document.createElement('div');
        div.className = 'component-item';
        div.draggable = true;
        div.dataset.componentType = key;
        
        div.innerHTML = `
            <i class="${component.icon}"></i>
            <span>${component.name}</span>
        `;
        
        return div;
    }
    
    setupDragAndDrop() {
        const componentsContainer = document.getElementById('components-list');
        const previewContainer = document.getElementById('preview-content');
        
        if (!componentsContainer || !previewContainer) return;
        
        // Handle drag start
        componentsContainer.addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('component-item')) {
                e.dataTransfer.setData('text/plain', e.target.dataset.componentType);
                e.dataTransfer.effectAllowed = 'copy';
            }
        });
        
        // Handle drop zone
        previewContainer.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            previewContainer.classList.add('drag-over');
        });
        
        previewContainer.addEventListener('dragleave', (e) => {
            if (!previewContainer.contains(e.relatedTarget)) {
                previewContainer.classList.remove('drag-over');
            }
        });
        
        previewContainer.addEventListener('drop', (e) => {
            e.preventDefault();
            previewContainer.classList.remove('drag-over');
            
            const componentType = e.dataTransfer.getData('text/plain');
            if (componentType && this.components[componentType]) {
                this.addComponentToPreview(componentType, e.clientX, e.clientY);
            }
        });
    }
    
    addComponentToPreview(componentType, x = null, y = null) {
        const component = this.components[componentType];
        const previewContent = document.getElementById('preview-content');
        
        if (!component || !previewContent) return;
        
        // Create component wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'component-wrapper';
        wrapper.dataset.componentType = componentType;
        
        // Add component HTML
        wrapper.innerHTML = `
            <div class="component-controls">
                <button class="btn-edit" title="Edit"><i class="fas fa-edit"></i></button>
                <button class="btn-delete" title="Delete"><i class="fas fa-trash"></i></button>
                <button class="btn-move-up" title="Move Up"><i class="fas fa-arrow-up"></i></button>
                <button class="btn-move-down" title="Move Down"><i class="fas fa-arrow-down"></i></button>
            </div>
            ${component.html}
        `;
        
        // Add component to preview
        previewContent.appendChild(wrapper);
        
        // Add CSS to the preview
        this.addComponentCSS(componentType);
        
        // Setup component controls
        this.setupComponentControls(wrapper);
        
        // Update live preview
        if (window.updateLivePreview) {
            window.updateLivePreview();
        }
        
        // Make text elements editable
        this.makeTextEditable(wrapper);
    }
    
    addComponentCSS(componentType) {
        const component = this.components[componentType];
        if (!component.css) return;
        
        const styleId = `component-style-${componentType}`;
        let styleElement = document.getElementById(styleId);
        
        if (!styleElement) {
            styleElement = document.createElement('style');
            styleElement.id = styleId;
            styleElement.textContent = component.css;
            document.head.appendChild(styleElement);
        }
    }
    
    setupComponentControls(wrapper) {
        const controls = wrapper.querySelector('.component-controls');
        
        // Edit button
        controls.querySelector('.btn-edit').addEventListener('click', () => {
            this.editComponent(wrapper);
        });
        
        // Delete button
        controls.querySelector('.btn-delete').addEventListener('click', () => {
            if (confirm('Are you sure you want to delete this component?')) {
                wrapper.remove();
                if (window.updateLivePreview) {
                    window.updateLivePreview();
                }
            }
        });
        
        // Move up button
        controls.querySelector('.btn-move-up').addEventListener('click', () => {
            const prev = wrapper.previousElementSibling;
            if (prev) {
                wrapper.parentNode.insertBefore(wrapper, prev);
                if (window.updateLivePreview) {
                    window.updateLivePreview();
                }
            }
        });
        
        // Move down button
        controls.querySelector('.btn-move-down').addEventListener('click', () => {
            const next = wrapper.nextElementSibling;
            if (next) {
                wrapper.parentNode.insertBefore(next, wrapper);
                if (window.updateLivePreview) {
                    window.updateLivePreview();
                }
            }
        });
    }
    
    makeTextEditable(wrapper) {
        const editableElements = wrapper.querySelectorAll('.editable');
        
        editableElements.forEach(element => {
            element.addEventListener('blur', () => {
                if (window.updateLivePreview) {
                    window.updateLivePreview();
                }
            });
            
            element.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    element.blur();
                }
            });
        });
    }
    
    editComponent(wrapper) {
        const componentType = wrapper.dataset.componentType;
        const component = this.components[componentType];
        
        // Create edit modal
        const modal = document.createElement('div');
        modal.className = 'component-edit-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Edit ${component.name}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>HTML:</label>
                        <textarea id="edit-html" rows="5">${wrapper.innerHTML.replace(/<div class="component-controls">.*?<\/div>/, '')}</textarea>
                    </div>
                    <div class="form-group">
                        <label>CSS:</label>
                        <textarea id="edit-css" rows="5">${component.css || ''}</textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary modal-cancel">Cancel</button>
                    <button class="btn btn-primary modal-save">Save</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Handle modal events
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.remove();
        });
        
        modal.querySelector('.modal-cancel').addEventListener('click', () => {
            modal.remove();
        });
        
        modal.querySelector('.modal-save').addEventListener('click', () => {
            const newHTML = modal.querySelector('#edit-html').value;
            const newCSS = modal.querySelector('#edit-css').value;
            
            // Update component
            wrapper.innerHTML = `
                <div class="component-controls">
                    <button class="btn-edit" title="Edit"><i class="fas fa-edit"></i></button>
                    <button class="btn-delete" title="Delete"><i class="fas fa-trash"></i></button>
                    <button class="btn-move-up" title="Move Up"><i class="fas fa-arrow-up"></i></button>
                    <button class="btn-move-down" title="Move Down"><i class="fas fa-arrow-down"></i></button>
                </div>
                ${newHTML}
            `;
            
            // Update CSS
            if (newCSS) {
                const styleId = `component-style-${componentType}-custom`;
                let styleElement = document.getElementById(styleId);
                
                if (!styleElement) {
                    styleElement = document.createElement('style');
                    styleElement.id = styleId;
                    document.head.appendChild(styleElement);
                }
                
                styleElement.textContent = newCSS;
            }
            
            // Re-setup controls and editable elements
            this.setupComponentControls(wrapper);
            this.makeTextEditable(wrapper);
            
            // Update live preview
            if (window.updateLivePreview) {
                window.updateLivePreview();
            }
            
            modal.remove();
        });
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    getPreviewHTML() {
        const previewContent = document.getElementById('preview-content');
        if (!previewContent) return '';
        
        // Clone the content and remove controls
        const clone = previewContent.cloneNode(true);
        const controls = clone.querySelectorAll('.component-controls');
        controls.forEach(control => control.remove());
        
        return clone.innerHTML;
    }
    
    loadTemplate(templateData) {
        const previewContent = document.getElementById('preview-content');
        if (!previewContent || !templateData.html) return;
        
        previewContent.innerHTML = templateData.html;
        
        // Re-setup components
        const wrappers = previewContent.querySelectorAll('.component-wrapper');
        wrappers.forEach(wrapper => {
            this.setupComponentControls(wrapper);
            this.makeTextEditable(wrapper);
        });
        
        // Add custom CSS if exists
        if (templateData.css) {
            const styleElement = document.createElement('style');
            styleElement.id = 'template-custom-css';
            styleElement.textContent = templateData.css;
            document.head.appendChild(styleElement);
        }
    }
}

// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.templateComponents = new TemplateComponents();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TemplateComponents;
}