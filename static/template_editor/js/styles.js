// Template Editor Styles Manager
// Handles color palettes, typography, and layout options

class TemplateStyles {
    constructor() {
        this.colorPalettes = {
            classic: {
                name: 'Classic',
                colors: {
                    primary: '#2c3e50',
                    secondary: '#3498db',
                    accent: '#e74c3c',
                    background: '#ffffff',
                    text: '#2c3e50',
                    muted: '#7f8c8d'
                }
            },
            romantic: {
                name: 'Romantic',
                colors: {
                    primary: '#e91e63',
                    secondary: '#f8bbd9',
                    accent: '#ad1457',
                    background: '#fce4ec',
                    text: '#880e4f',
                    muted: '#c2185b'
                }
            },
            elegant: {
                name: 'Elegant',
                colors: {
                    primary: '#212121',
                    secondary: '#757575',
                    accent: '#ffd700',
                    background: '#fafafa',
                    text: '#212121',
                    muted: '#9e9e9e'
                }
            },
            nature: {
                name: 'Nature',
                colors: {
                    primary: '#2e7d32',
                    secondary: '#66bb6a',
                    accent: '#ff8f00',
                    background: '#f1f8e9',
                    text: '#1b5e20',
                    muted: '#4caf50'
                }
            },
            ocean: {
                name: 'Ocean',
                colors: {
                    primary: '#006064',
                    secondary: '#26c6da',
                    accent: '#ff5722',
                    background: '#e0f2f1',
                    text: '#004d40',
                    muted: '#00acc1'
                }
            },
            sunset: {
                name: 'Sunset',
                colors: {
                    primary: '#d84315',
                    secondary: '#ff8a65',
                    accent: '#ffc107',
                    background: '#fff3e0',
                    text: '#bf360c',
                    muted: '#ff7043'
                }
            }
        };
        
        this.fontFamilies = {
            serif: {
                name: 'Serif',
                family: 'Georgia, "Times New Roman", serif',
                weights: ['400', '700'],
                description: 'Classic and elegant'
            },
            sansSerif: {
                name: 'Sans Serif',
                family: '"Helvetica Neue", Arial, sans-serif',
                weights: ['300', '400', '600', '700'],
                description: 'Modern and clean'
            },
            script: {
                name: 'Script',
                family: '"Dancing Script", cursive',
                weights: ['400', '700'],
                description: 'Handwritten style'
            },
            display: {
                name: 'Display',
                family: '"Playfair Display", serif',
                weights: ['400', '700', '900'],
                description: 'Bold and dramatic'
            },
            modern: {
                name: 'Modern',
                family: '"Roboto", sans-serif',
                weights: ['300', '400', '500', '700'],
                description: 'Contemporary and versatile'
            }
        };
        
        this.layoutOptions = {
            centered: {
                name: 'Centered',
                css: 'text-align: center; max-width: 800px; margin: 0 auto;',
                description: 'Center-aligned content'
            },
            fullWidth: {
                name: 'Full Width',
                css: 'width: 100%; margin: 0;',
                description: 'Full width layout'
            },
            sidebar: {
                name: 'Sidebar',
                css: 'display: grid; grid-template-columns: 1fr 300px; gap: 20px;',
                description: 'Main content with sidebar'
            },
            columns: {
                name: 'Two Columns',
                css: 'display: grid; grid-template-columns: 1fr 1fr; gap: 30px;',
                description: 'Two equal columns'
            },
            magazine: {
                name: 'Magazine',
                css: 'display: grid; grid-template-columns: 2fr 1fr; gap: 25px;',
                description: 'Magazine-style layout'
            }
        };
        
        this.initializeStyles();
    }
    
    initializeStyles() {
        this.renderColorPalettes();
        this.renderFontFamilies();
        this.renderLayoutOptions();
        this.setupEventListeners();
    }
    
    renderColorPalettes() {
        const container = document.getElementById('color-palettes');
        if (!container) return;
        
        container.innerHTML = '';
        
        Object.keys(this.colorPalettes).forEach(key => {
            const palette = this.colorPalettes[key];
            const paletteElement = this.createPaletteElement(key, palette);
            container.appendChild(paletteElement);
        });
    }
    
    createPaletteElement(key, palette) {
        const div = document.createElement('div');
        div.className = 'palette-item';
        div.dataset.paletteKey = key;
        
        const colorsHTML = Object.keys(palette.colors).map(colorKey => {
            return `<div class="color-swatch" style="background-color: ${palette.colors[colorKey]}" title="${colorKey}: ${palette.colors[colorKey]}"></div>`;
        }).join('');
        
        div.innerHTML = `
            <div class="palette-header">
                <h4>${palette.name}</h4>
            </div>
            <div class="palette-colors">
                ${colorsHTML}
            </div>
            <button class="btn btn-sm btn-primary apply-palette">Apply</button>
        `;
        
        return div;
    }
    
    renderFontFamilies() {
        const container = document.getElementById('font-families');
        if (!container) return;
        
        container.innerHTML = '';
        
        Object.keys(this.fontFamilies).forEach(key => {
            const font = this.fontFamilies[key];
            const fontElement = this.createFontElement(key, font);
            container.appendChild(fontElement);
        });
    }
    
    createFontElement(key, font) {
        const div = document.createElement('div');
        div.className = 'font-item';
        div.dataset.fontKey = key;
        
        div.innerHTML = `
            <div class="font-preview" style="font-family: ${font.family}">
                <h4>${font.name}</h4>
                <p class="font-sample">The quick brown fox jumps over the lazy dog</p>
                <small>${font.description}</small>
            </div>
            <button class="btn btn-sm btn-primary apply-font">Apply</button>
        `;
        
        return div;
    }
    
    renderLayoutOptions() {
        const container = document.getElementById('layout-options');
        if (!container) return;
        
        container.innerHTML = '';
        
        Object.keys(this.layoutOptions).forEach(key => {
            const layout = this.layoutOptions[key];
            const layoutElement = this.createLayoutElement(key, layout);
            container.appendChild(layoutElement);
        });
    }
    
    createLayoutElement(key, layout) {
        const div = document.createElement('div');
        div.className = 'layout-item';
        div.dataset.layoutKey = key;
        
        div.innerHTML = `
            <div class="layout-preview">
                <h4>${layout.name}</h4>
                <p>${layout.description}</p>
                <div class="layout-visual" data-layout="${key}"></div>
            </div>
            <button class="btn btn-sm btn-primary apply-layout">Apply</button>
        `;
        
        return div;
    }
    
    setupEventListeners() {
        // Color palette application
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('apply-palette')) {
                const paletteKey = e.target.closest('.palette-item').dataset.paletteKey;
                this.applyColorPalette(paletteKey);
            }
            
            if (e.target.classList.contains('apply-font')) {
                const fontKey = e.target.closest('.font-item').dataset.fontKey;
                this.applyFontFamily(fontKey);
            }
            
            if (e.target.classList.contains('apply-layout')) {
                const layoutKey = e.target.closest('.layout-item').dataset.layoutKey;
                this.applyLayout(layoutKey);
            }
        });
        
        // Custom color picker
        const customColorInputs = document.querySelectorAll('.custom-color-input');
        customColorInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.applyCustomColor(e.target.dataset.colorType, e.target.value);
            });
        });
    }
    
    applyColorPalette(paletteKey) {
        const palette = this.colorPalettes[paletteKey];
        if (!palette) return;
        
        const previewContent = document.getElementById('preview-content');
        if (!previewContent) return;
        
        // Create or update CSS variables
        const styleId = 'applied-color-palette';
        let styleElement = document.getElementById(styleId);
        
        if (!styleElement) {
            styleElement = document.createElement('style');
            styleElement.id = styleId;
            document.head.appendChild(styleElement);
        }
        
        const cssVariables = Object.keys(palette.colors).map(key => {
            return `--color-${key}: ${palette.colors[key]};`;
        }).join('\n');
        
        const css = `
            #preview-content {
                ${cssVariables}
            }
            
            #preview-content .text-component,
            #preview-content .heading-component,
            #preview-content .list-component {
                color: var(--color-text);
            }
            
            #preview-content .container-component {
                background-color: var(--color-background);
                border-color: var(--color-muted);
            }
            
            #preview-content .btn-component {
                background-color: var(--color-primary);
                color: var(--color-background);
            }
            
            #preview-content .btn-component:hover {
                background-color: var(--color-secondary);
            }
            
            #preview-content .quote-component {
                border-left-color: var(--color-accent);
                background-color: var(--color-background);
            }
            
            #preview-content .divider-component {
                background-color: var(--color-muted);
            }
        `;
        
        styleElement.textContent = css;
        
        // Update live preview
        if (window.updateLivePreview) {
            window.updateLivePreview();
        }
        
        // Show success message
        this.showMessage(`Applied ${palette.name} color palette`, 'success');
    }
    
    applyFontFamily(fontKey) {
        const font = this.fontFamilies[fontKey];
        if (!font) return;
        
        const styleId = 'applied-font-family';
        let styleElement = document.getElementById(styleId);
        
        if (!styleElement) {
            styleElement = document.createElement('style');
            styleElement.id = styleId;
            document.head.appendChild(styleElement);
        }
        
        const css = `
            #preview-content {
                font-family: ${font.family};
            }
            
            #preview-content .heading-component {
                font-family: ${font.family};
                font-weight: 700;
            }
        `;
        
        styleElement.textContent = css;
        
        // Load Google Fonts if needed
        if (font.family.includes('Dancing Script') || font.family.includes('Playfair Display') || font.family.includes('Roboto')) {
            this.loadGoogleFont(font.family);
        }
        
        // Update live preview
        if (window.updateLivePreview) {
            window.updateLivePreview();
        }
        
        // Show success message
        this.showMessage(`Applied ${font.name} font family`, 'success');
    }
    
    applyLayout(layoutKey) {
        const layout = this.layoutOptions[layoutKey];
        if (!layout) return;
        
        const previewContent = document.getElementById('preview-content');
        if (!previewContent) return;
        
        const styleId = 'applied-layout';
        let styleElement = document.getElementById(styleId);
        
        if (!styleElement) {
            styleElement = document.createElement('style');
            styleElement.id = styleId;
            document.head.appendChild(styleElement);
        }
        
        const css = `
            #preview-content {
                ${layout.css}
            }
            
            @media (max-width: 768px) {
                #preview-content {
                    display: block !important;
                    grid-template-columns: none !important;
                    max-width: 100% !important;
                }
            }
        `;
        
        styleElement.textContent = css;
        
        // Update live preview
        if (window.updateLivePreview) {
            window.updateLivePreview();
        }
        
        // Show success message
        this.showMessage(`Applied ${layout.name} layout`, 'success');
    }
    
    applyCustomColor(colorType, colorValue) {
        const styleId = 'custom-colors';
        let styleElement = document.getElementById(styleId);
        
        if (!styleElement) {
            styleElement = document.createElement('style');
            styleElement.id = styleId;
            document.head.appendChild(styleElement);
        }
        
        // Get existing CSS and update the specific color
        let existingCSS = styleElement.textContent || '';
        const colorVar = `--color-${colorType}: ${colorValue};`;
        
        // Replace existing color variable or add new one
        const regex = new RegExp(`--color-${colorType}:.*?;`, 'g');
        if (existingCSS.includes(`--color-${colorType}`)) {
            existingCSS = existingCSS.replace(regex, colorVar);
        } else {
            existingCSS += `\n#preview-content { ${colorVar} }`;
        }
        
        styleElement.textContent = existingCSS;
        
        // Update live preview
        if (window.updateLivePreview) {
            window.updateLivePreview();
        }
    }
    
    loadGoogleFont(fontFamily) {
        const fontName = fontFamily.split(',')[0].replace(/"/g, '').trim();
        const linkId = `google-font-${fontName.replace(/\s+/g, '-').toLowerCase()}`;
        
        if (document.getElementById(linkId)) return;
        
        const link = document.createElement('link');
        link.id = linkId;
        link.rel = 'stylesheet';
        link.href = `https://fonts.googleapis.com/css2?family=${fontName.replace(/\s+/g, '+')}:wght@300;400;500;700;900&display=swap`;
        document.head.appendChild(link);
    }
    
    showMessage(message, type = 'info') {
        const messageContainer = document.getElementById('message-container') || this.createMessageContainer();
        
        const messageElement = document.createElement('div');
        messageElement.className = `message message-${type}`;
        messageElement.textContent = message;
        
        messageContainer.appendChild(messageElement);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            messageElement.remove();
        }, 3000);
    }
    
    createMessageContainer() {
        const container = document.createElement('div');
        container.id = 'message-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
        `;
        document.body.appendChild(container);
        return container;
    }
    
    getCurrentStyles() {
        const styles = {};
        
        // Get applied color palette
        const colorPaletteStyle = document.getElementById('applied-color-palette');
        if (colorPaletteStyle) {
            styles.colorPalette = colorPaletteStyle.textContent;
        }
        
        // Get applied font family
        const fontFamilyStyle = document.getElementById('applied-font-family');
        if (fontFamilyStyle) {
            styles.fontFamily = fontFamilyStyle.textContent;
        }
        
        // Get applied layout
        const layoutStyle = document.getElementById('applied-layout');
        if (layoutStyle) {
            styles.layout = layoutStyle.textContent;
        }
        
        // Get custom colors
        const customColorsStyle = document.getElementById('custom-colors');
        if (customColorsStyle) {
            styles.customColors = customColorsStyle.textContent;
        }
        
        return styles;
    }
    
    loadStyles(styles) {
        if (!styles) return;
        
        // Apply color palette
        if (styles.colorPalette) {
            let styleElement = document.getElementById('applied-color-palette');
            if (!styleElement) {
                styleElement = document.createElement('style');
                styleElement.id = 'applied-color-palette';
                document.head.appendChild(styleElement);
            }
            styleElement.textContent = styles.colorPalette;
        }
        
        // Apply font family
        if (styles.fontFamily) {
            let styleElement = document.getElementById('applied-font-family');
            if (!styleElement) {
                styleElement = document.createElement('style');
                styleElement.id = 'applied-font-family';
                document.head.appendChild(styleElement);
            }
            styleElement.textContent = styles.fontFamily;
        }
        
        // Apply layout
        if (styles.layout) {
            let styleElement = document.getElementById('applied-layout');
            if (!styleElement) {
                styleElement = document.createElement('style');
                styleElement.id = 'applied-layout';
                document.head.appendChild(styleElement);
            }
            styleElement.textContent = styles.layout;
        }
        
        // Apply custom colors
        if (styles.customColors) {
            let styleElement = document.getElementById('custom-colors');
            if (!styleElement) {
                styleElement = document.createElement('style');
                styleElement.id = 'custom-colors';
                document.head.appendChild(styleElement);
            }
            styleElement.textContent = styles.customColors;
        }
    }
}

// Initialize styles when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.templateStyles = new TemplateStyles();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TemplateStyles;
}