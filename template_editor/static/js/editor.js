// Editor Undangan - JavaScript Functions
// Fungsi-fungsi untuk menangani semua fitur editor

// Global variables
let htmlEditor, cssEditor, jsEditor;
let currentTemplate = null;
let isGenerating = false;
let aiApiKey = 'YOUR_GEMINI_API_KEY'; // Ganti dengan API key Gemini yang valid

// Initialize semua fungsi saat DOM loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeEditors();
    initializeTabs();
    initializeColorPalette();
    initializeFontFamily();
    initializeDesignElements();
    initializeLayoutTemplates();
    initializeAI();
    initializeExport();
    initializeTemplateManagement();
    initializeNotifications();
    
    // Show welcome message
    setTimeout(() => {
        showNotification('🎨 Selamat datang di Editor Undangan Admin!', 'success');
    }, 1000);
});

// Initialize CodeMirror editors
function initializeEditors() {
    htmlEditor = CodeMirror.fromTextArea(document.getElementById('htmlCode'), {
        mode: 'htmlmixed',
        theme: 'dracula',
        lineNumbers: true,
        autoCloseTags: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 2,
        tabSize: 2,
        lineWrapping: true,
        extraKeys: {
            'Ctrl-Space': 'autocomplete',
            'F11': function(cm) {
                cm.setOption('fullScreen', !cm.getOption('fullScreen'));
            },
            'Esc': function(cm) {
                if (cm.getOption('fullScreen')) cm.setOption('fullScreen', false);
            }
        }
    });

    cssEditor = CodeMirror.fromTextArea(document.getElementById('cssCode'), {
        mode: 'css',
        theme: 'dracula',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 2,
        tabSize: 2,
        lineWrapping: true,
        extraKeys: {
            'Ctrl-Space': 'autocomplete',
            'F11': function(cm) {
                cm.setOption('fullScreen', !cm.getOption('fullScreen'));
            },
            'Esc': function(cm) {
                if (cm.getOption('fullScreen')) cm.setOption('fullScreen', false);
            }
        }
    });

    jsEditor = CodeMirror.fromTextArea(document.getElementById('jsCode'), {
        mode: 'javascript',
        theme: 'dracula',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 2,
        tabSize: 2,
        lineWrapping: true,
        extraKeys: {
            'Ctrl-Space': 'autocomplete',
            'F11': function(cm) {
                cm.setOption('fullScreen', !cm.getOption('fullScreen'));
            },
            'Esc': function(cm) {
                if (cm.getOption('fullScreen')) cm.setOption('fullScreen', false);
            }
        }
    });

    // Set default template content
    setDefaultTemplate();

    // Update preview on code change
    htmlEditor.on('change', debounce(updateLivePreview, 500));
    cssEditor.on('change', debounce(updateLivePreview, 500));
    jsEditor.on('change', debounce(updateLivePreview, 500));

    // Initial preview update
    updateLivePreview();
}

// Set default template
function setDefaultTemplate() {
    const defaultHtml = `<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Undangan Pernikahan</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;600;700&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-pink-100 to-purple-100 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden border border-pink-200">
        <div class="bg-gradient-to-r from-pink-500 to-purple-600 p-8 text-white text-center relative">
            <div class="absolute inset-0 bg-black opacity-10"></div>
            <div class="relative z-10">
                <div class="text-6xl mb-4">💕</div>
                <h1 class="text-3xl font-serif mb-2">Undangan Pernikahan</h1>
                <p class="text-pink-100">Dengan penuh sukacita, kami mengundang Anda</p>
            </div>
        </div>
        <div class="p-8 text-center">
            <div class="mb-8">
                <h2 class="text-4xl font-dancing text-gray-800 mb-4">John & Jane</h2>
                <p class="text-gray-600">Akan melangsungkan pernikahan pada:</p>
            </div>
            <div class="bg-gradient-to-r from-pink-50 to-purple-50 p-6 rounded-xl mb-8 border border-pink-200">
                <p class="font-semibold text-gray-800 text-lg mb-2">Sabtu, 25 Desember 2024</p>
                <p class="text-gray-600 mb-1">Pukul 10.00 WIB</p>
                <p class="text-gray-600 mb-1">Hotel Grand Ballroom</p>
                <p class="text-gray-600">Jl. Sudirman No. 123, Jakarta</p>
            </div>
            <button class="bg-gradient-to-r from-pink-500 to-purple-600 text-white px-8 py-3 rounded-full hover:from-pink-600 hover:to-purple-700 transition-all transform hover:scale-105 shadow-lg">
                💌 Konfirmasi Kehadiran
            </button>
        </div>
    </div>
</body>
</html>`;

    const defaultCss = `/* Custom CSS untuk undangan */
.font-dancing {
    font-family: 'Dancing Script', cursive;
}

.font-serif {
    font-family: 'Playfair Display', serif;
}

.invitation-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    box-shadow: 0 25px 50px rgba(0,0,0,0.15);
    backdrop-filter: blur(10px);
}

.couple-names {
    background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.date-info {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.3);
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.02);
    }
}

@keyframes float {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-10px);
    }
}

.animate-fade-in {
    animation: fadeInUp 0.8s ease-out;
}

.animate-pulse {
    animation: pulse 2s infinite;
}

.animate-float {
    animation: float 3s ease-in-out infinite;
}

/* Responsive design */
@media (max-width: 768px) {
    .max-w-md {
        max-width: 90%;
        margin: 1rem;
    }
    
    .text-4xl {
        font-size: 2rem;
    }
    
    .text-3xl {
        font-size: 1.5rem;
    }
    
    .p-8 {
        padding: 1.5rem;
    }
}`;

    const defaultJs = `// JavaScript untuk interaktivitas undangan
document.addEventListener('DOMContentLoaded', function() {
    // Animasi fade in untuk elemen
    const elements = document.querySelectorAll('.max-w-md > div');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        setTimeout(() => {
            el.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 300);
    });

    // Konfirmasi kehadiran dengan animasi
    const confirmBtn = document.querySelector('button');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Animasi button
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
            
            // Show modal konfirmasi
            showConfirmationModal();
        });
    }

    // Efek parallax sederhana
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('.max-w-md');
        if (parallax) {
            const speed = scrolled * 0.1;
            parallax.style.transform = \`translateY(\${speed}px)\`;
        }
    });

    // Efek hover pada card
    const card = document.querySelector('.max-w-md');
    if (card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02) translateY(-5px)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) translateY(0)';
        });
    }

    // Particle effect
    createParticleEffect();
});

// Modal konfirmasi kehadiran
function showConfirmationModal() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = \`
        <div class="bg-white rounded-2xl p-8 max-w-md mx-4 text-center transform scale-0 transition-transform duration-300">
            <div class="text-6xl mb-4">🎉</div>
            <h3 class="text-2xl font-bold text-gray-800 mb-4">Terima Kasih!</h3>
            <p class="text-gray-600 mb-6">Konfirmasi kehadiran Anda telah diterima. Kami sangat menantikan kehadiran Anda!</p>
            <button onclick="closeModal(this)" class="bg-gradient-to-r from-pink-500 to-purple-600 text-white px-6 py-3 rounded-full hover:from-pink-600 hover:to-purple-700 transition-all">
                Tutup
            </button>
        </div>
    \`;
    
    document.body.appendChild(modal);
    
    // Animate modal
    setTimeout(() => {
        modal.querySelector('div').style.transform = 'scale(1)';
    }, 100);
}

// Close modal
function closeModal(btn) {
    const modal = btn.closest('.fixed');
    modal.querySelector('div').style.transform = 'scale(0)';
    setTimeout(() => {
        modal.remove();
    }, 300);
}

// Particle effect
function createParticleEffect() {
    function createParticle() {
        const particle = document.createElement('div');
        particle.className = 'fixed w-2 h-2 bg-pink-400 rounded-full pointer-events-none opacity-70';
        particle.style.left = Math.random() * window.innerWidth + 'px';
        particle.style.top = window.innerHeight + 'px';
        particle.style.zIndex = '10';
        document.body.appendChild(particle);
        
        const animation = particle.animate([
            { 
                transform: 'translateY(0px) rotate(0deg)', 
                opacity: 0.7 
            },
            { 
                transform: \`translateY(-\${window.innerHeight + 100}px) rotate(360deg)\`, 
                opacity: 0 
            }
        ], {
            duration: 4000 + Math.random() * 2000,
            easing: 'linear'
        });
        
        animation.onfinish = () => particle.remove();
    }
    
    // Create particles periodically
    setInterval(createParticle, 800);
}`;

    htmlEditor.setValue(defaultHtml);
    cssEditor.setValue(defaultCss);
    jsEditor.setValue(defaultJs);
}

// Update live preview
function updateLivePreview() {
    const html = htmlEditor.getValue();
    const css = cssEditor.getValue();
    const js = jsEditor.getValue();

    // Extract body content from HTML
    const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
    const bodyContent = bodyMatch ? bodyMatch[1] : html;
    
    // Extract head content for additional scripts/styles
    const headMatch = html.match(/<head[^>]*>([\s\S]*?)<\/head>/i);
    const headContent = headMatch ? headMatch[1] : '';

    const previewContent = `
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Preview</title>
            ${headContent}
            <style>${css}</style>
        </head>
        <body>
            ${bodyContent}
            <script>${js}</script>
        </body>
        </html>
    `;

    const previewFrame = document.getElementById('livePreview');
    if (previewFrame) {
        previewFrame.srcdoc = previewContent;
    }
}

// Tab switching functionality
function initializeTabs() {
    const tabs = document.querySelectorAll('.editor-tab');
    const contents = document.querySelectorAll('.editor-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;

            // Remove active class from all tabs
            tabs.forEach(t => {
                t.classList.remove('active', 'border-blue-500', 'text-blue-400');
                t.classList.add('border-transparent');
            });

            // Add active class to clicked tab
            tab.classList.add('active', 'border-blue-500', 'text-blue-400');
            tab.classList.remove('border-transparent');

            // Hide all content
            contents.forEach(content => content.classList.add('hidden'));

            // Show target content
            const targetContent = document.getElementById(targetTab + 'Editor');
            if (targetContent) {
                targetContent.classList.remove('hidden');
                
                // Refresh CodeMirror editors when switching tabs
                setTimeout(() => {
                    if (targetTab === 'html') htmlEditor.refresh();
                    if (targetTab === 'css') cssEditor.refresh();
                    if (targetTab === 'js') jsEditor.refresh();
                    if (targetTab === 'preview') {
                        const previewFrame = document.getElementById('previewFrame');
                        if (previewFrame) {
                            previewFrame.srcdoc = document.getElementById('livePreview').srcdoc;
                        }
                    }
                }, 100);
            }
        });
    });
}

// Color palette functionality
function initializeColorPalette() {
    const colorInputs = {
        primary: document.getElementById('primaryColor'),
        secondary: document.getElementById('secondaryColor'),
        accent: document.getElementById('accentColor')
    };

    const hexInputs = {
        primary: document.getElementById('primaryColorHex'),
        secondary: document.getElementById('secondaryColorHex'),
        accent: document.getElementById('accentColorHex')
    };

    // Set default colors
    if (colorInputs.primary) colorInputs.primary.value = '#ec4899';
    if (colorInputs.secondary) colorInputs.secondary.value = '#8b5cf6';
    if (colorInputs.accent) colorInputs.accent.value = '#f59e0b';
    
    if (hexInputs.primary) hexInputs.primary.value = '#ec4899';
    if (hexInputs.secondary) hexInputs.secondary.value = '#8b5cf6';
    if (hexInputs.accent) hexInputs.accent.value = '#f59e0b';

    // Sync color picker with hex input
    Object.keys(colorInputs).forEach(key => {
        if (colorInputs[key] && hexInputs[key]) {
            colorInputs[key].addEventListener('change', (e) => {
                hexInputs[key].value = e.target.value;
                applyColorToCode(key, e.target.value);
            });

            hexInputs[key].addEventListener('change', (e) => {
                if (/^#[0-9A-F]{6}$/i.test(e.target.value)) {
                    colorInputs[key].value = e.target.value;
                    applyColorToCode(key, e.target.value);
                }
            });
        }
    });

    // Color palette selection
    document.querySelectorAll('.color-palette').forEach(palette => {
        palette.addEventListener('click', () => {
            const paletteId = palette.dataset.paletteId;
            // Apply predefined color palette
            applyColorPalette(paletteId);
        });
    });
}

// Apply color to code
function applyColorToCode(colorType, colorValue) {
    let css = cssEditor.getValue();
    
    // Color mapping for replacement
    const colorMap = {
        primary: ['#ec4899', '#f093fb', '#pink-500'],
        secondary: ['#8b5cf6', '#764ba2', '#purple-600'],
        accent: ['#f59e0b', '#fbbf24', '#amber-500']
    };

    if (colorMap[colorType]) {
        colorMap[colorType].forEach(oldColor => {
            css = css.replace(new RegExp(oldColor, 'gi'), colorValue);
        });
        
        // Also replace Tailwind classes
        if (colorType === 'primary') {
            css = css.replace(/from-pink-\d+/g, `from-[${colorValue}]`);
            css = css.replace(/to-purple-\d+/g, `to-[${colorValue}]`);
        }
        
        cssEditor.setValue(css);
        showNotification(`🎨 Warna ${colorType} berhasil diterapkan!`, 'success');
    }
}

// Apply predefined color palette
function applyColorPalette(paletteId) {
    const palettes = {
        '1': { primary: '#ec4899', secondary: '#8b5cf6', accent: '#f59e0b' },
        '2': { primary: '#ef4444', secondary: '#f97316', accent: '#eab308' },
        '3': { primary: '#3b82f6', secondary: '#06b6d4', accent: '#10b981' },
        '4': { primary: '#8b5cf6', secondary: '#ec4899', accent: '#f59e0b' },
        '5': { primary: '#10b981', secondary: '#059669', accent: '#34d399' }
    };
    
    if (palettes[paletteId]) {
        const palette = palettes[paletteId];
        
        // Update color inputs
        document.getElementById('primaryColor').value = palette.primary;
        document.getElementById('secondaryColor').value = palette.secondary;
        document.getElementById('accentColor').value = palette.accent;
        
        document.getElementById('primaryColorHex').value = palette.primary;
        document.getElementById('secondaryColorHex').value = palette.secondary;
        document.getElementById('accentColorHex').value = palette.accent;
        
        // Apply colors
        applyColorToCode('primary', palette.primary);
        applyColorToCode('secondary', palette.secondary);
        applyColorToCode('accent', palette.accent);
        
        showNotification('🎨 Palet warna berhasil diterapkan!', 'success');
    }
}

// Font family functionality
function initializeFontFamily() {
    document.querySelectorAll('.font-family-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const fontFamily = btn.dataset.font;
            applyFontToCode(fontFamily);
        });
    });

    // Font size slider
    const fontSizeSlider = document.getElementById('fontSize');
    const fontSizeValue = document.getElementById('fontSizeValue');

    if (fontSizeSlider && fontSizeValue) {
        fontSizeSlider.addEventListener('input', (e) => {
            const size = e.target.value;
            fontSizeValue.textContent = size + 'px';
            applyFontSizeToCode(size);
        });
    }
}

// Apply font to code
function applyFontToCode(fontFamily) {
    let css = cssEditor.getValue();
    let html = htmlEditor.getValue();
    
    // Add Google Fonts import if needed
    const fontImport = `@import url('https://fonts.googleapis.com/css2?family=${fontFamily.replace(/\s+/g, '+')}:wght@300;400;600;700&display=swap');`;
    
    if (!css.includes(fontFamily)) {
        css = fontImport + '\n\n' + css;
    }

    // Apply font to body or main elements
    const fontCSS = `\nbody, .invitation-card {\n    font-family: '${fontFamily}', sans-serif;\n}`;
    
    if (!css.includes('font-family')) {
        css += fontCSS;
    } else {
        css = css.replace(/font-family:[^;]+;/g, `font-family: '${fontFamily}', sans-serif;`);
    }

    cssEditor.setValue(css);
    showNotification(`🔤 Font ${fontFamily} berhasil diterapkan!`, 'success');
}

// Apply font size to code
function applyFontSizeToCode(size) {
    let css = cssEditor.getValue();
    
    if (!css.includes('font-size')) {
        css += `\n\nbody {\n    font-size: ${size}px;\n}`;
    } else {
        css = css.replace(/font-size:[^;]+;/g, `font-size: ${size}px;`);
    }

    cssEditor.setValue(css);
    showNotification(`📏 Ukuran font ${size}px berhasil diterapkan!`, 'success');
}

// Design elements functionality
function initializeDesignElements() {
    document.querySelectorAll('.element-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const element = btn.dataset.element;
            addDesignElement(element);
        });
    });
}

// Add design element
function addDesignElement(elementType) {
    let html = htmlEditor.getValue();
    let css = cssEditor.getValue();

    switch (elementType) {
        case 'text':
            const textElement = `\n    <div class="custom-text animate-fade-in">\n        <h3 class="text-xl font-semibold text-gray-800 mb-2">Teks Kustom</h3>\n        <p class="text-gray-600">Tambahkan teks kustom Anda di sini</p>\n    </div>`;
            html = html.replace('</body>', textElement + '\n</body>');
            css += `\n\n.custom-text {\n    padding: 1rem;\n    margin: 1rem 0;\n    text-align: center;\n    background: rgba(255,255,255,0.9);\n    border-radius: 0.5rem;\n    box-shadow: 0 4px 6px rgba(0,0,0,0.1);\n}`;
            break;
            
        case 'image':
            const imageElement = `\n    <div class="custom-image-container animate-fade-in">\n        <img src="https://via.placeholder.com/300x200/ec4899/ffffff?text=Gambar+Undangan" alt="Gambar Undangan" class="custom-image">\n    </div>`;
            html = html.replace('</body>', imageElement + '\n</body>');
            css += `\n\n.custom-image-container {\n    text-align: center;\n    margin: 1rem 0;\n}\n\n.custom-image {\n    max-width: 100%;\n    height: auto;\n    border-radius: 1rem;\n    box-shadow: 0 10px 25px rgba(0,0,0,0.15);\n    transition: transform 0.3s ease;\n}\n\n.custom-image:hover {\n    transform: scale(1.05);\n}`;
            break;
            
        case 'shape':
            const shapeElement = `\n    <div class="custom-shapes animate-fade-in">\n        <div class="shape-circle"></div>\n        <div class="shape-heart">💕</div>\n        <div class="shape-star">⭐</div>\n    </div>`;
            html = html.replace('</body>', shapeElement + '\n</body>');
            css += `\n\n.custom-shapes {\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    gap: 1rem;\n    margin: 2rem 0;\n}\n\n.shape-circle {\n    width: 50px;\n    height: 50px;\n    background: linear-gradient(45deg, #ec4899, #8b5cf6);\n    border-radius: 50%;\n    animation: pulse 2s infinite;\n}\n\n.shape-heart, .shape-star {\n    font-size: 2rem;\n    animation: float 3s ease-in-out infinite;\n}`;
            break;
            
        case 'border':
            css += `\n\n.max-w-md {\n    border: 3px solid transparent;\n    background: linear-gradient(white, white) padding-box,\n                linear-gradient(45deg, #ec4899, #8b5cf6, #f59e0b) border-box;\n    border-radius: 1rem;\n}`;
            break;
            
        case 'background':
            css += `\n\nbody {\n    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n    background-attachment: fixed;\n}\n\nbody::before {\n    content: '';\n    position: fixed;\n    top: 0;\n    left: 0;\n    width: 100%;\n    height: 100%;\n    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="%23ffffff" opacity="0.1"/></svg>') repeat;\n    pointer-events: none;\n    z-index: -1;\n}`;
            break;
            
        case 'animation':
            css += `\n\n@keyframes sparkle {\n    0%, 100% { opacity: 0; transform: scale(0); }\n    50% { opacity: 1; transform: scale(1); }\n}\n\n.max-w-md::after {\n    content: '✨';\n    position: absolute;\n    top: 10px;\n    right: 10px;\n    animation: sparkle 2s infinite;\n}\n\n.max-w-md {\n    position: relative;\n    animation: float 6s ease-in-out infinite;\n}`;
            break;
    }

    htmlEditor.setValue(html);
    cssEditor.setValue(css);
    showNotification(`✨ Elemen ${elementType} berhasil ditambahkan!`, 'success');
}

// Layout templates functionality
function initializeLayoutTemplates() {
    document.querySelectorAll('.layout-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const layout = btn.dataset.layout;
            applyLayoutTemplate(layout);
        });
    });
}

// Apply layout template
function applyLayoutTemplate(layoutType) {
    const templates = getLayoutTemplates();
    
    if (templates[layoutType]) {
        const template = templates[layoutType];
        htmlEditor.setValue(template.html);
        cssEditor.setValue(template.css);
        jsEditor.setValue(template.js);
        showNotification(`📐 Template ${layoutType} berhasil diterapkan!`, 'success');
    }
}

// Get layout templates
function getLayoutTemplates() {
    return {
        simple: {
            html: `<!DOCTYPE html>\n<html lang="id">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Undangan Sederhana</title>\n    <script src="https://cdn.tailwindcss.com"></script>\n</head>\n<body class="bg-gray-100 p-8">\n    <div class="max-w-md mx-auto bg-white p-8 rounded-lg shadow-lg text-center">\n        <h1 class="text-3xl font-bold mb-6 text-gray-800">Undangan</h1>\n        <h2 class="text-2xl mb-6 text-blue-600">John & Jane</h2>\n        <div class="mb-6">\n            <p class="text-lg font-semibold mb-2">25 Desember 2024</p>\n            <p class="text-gray-600">Pukul 10.00 WIB</p>\n            <p class="text-gray-600">Hotel Grand Ballroom</p>\n        </div>\n        <button class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-colors">\n            Konfirmasi Kehadiran\n        </button>\n    </div>\n</body>\n</html>`,
            css: `.invitation-card { background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }`,
            js: `console.log('Simple template loaded');`
        },
        elegant: {
            html: `<!DOCTYPE html>\n<html lang="id">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Undangan Elegan</title>\n    <script src="https://cdn.tailwindcss.com"></script>\n    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">\n</head>\n<body class="bg-gradient-to-br from-amber-50 to-amber-100 min-h-screen flex items-center justify-center p-4">\n    <div class="max-w-lg mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden border border-amber-200">\n        <div class="bg-gradient-to-r from-amber-400 to-amber-600 p-12 text-white text-center">\n            <div class="text-7xl mb-6">💍</div>\n            <h1 class="text-4xl font-serif mb-4">Undangan Pernikahan</h1>\n            <div class="w-32 h-0.5 bg-white mx-auto opacity-80"></div>\n        </div>\n        <div class="p-12 text-center">\n            <h2 class="text-5xl font-serif text-amber-800 mb-8">John & Jane</h2>\n            <div class="bg-amber-50 p-8 rounded-xl mb-8 border border-amber-200">\n                <p class="text-amber-800 font-semibold text-xl mb-3">Sabtu, 25 Desember 2024</p>\n                <p class="text-amber-700 text-lg mb-2">Pukul 10.00 WIB</p>\n                <p class="text-amber-700 text-lg">Hotel Grand Ballroom</p>\n            </div>\n            <button class="bg-amber-500 hover:bg-amber-600 text-white px-10 py-4 rounded-full font-semibold text-lg transition-all transform hover:scale-105">\n                Konfirmasi Kehadiran\n            </button>\n        </div>\n    </div>\n</body>\n</html>`,
            css: `@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap');\n\n.font-serif { font-family: 'Playfair Display', serif; }\n\n.invitation-card {\n    background: linear-gradient(135deg, #fef7cd 0%, #fbbf24 100%);\n    box-shadow: 0 25px 50px rgba(0,0,0,0.15);\n}`,
            js: `document.addEventListener('DOMContentLoaded', function() {\n    const card = document.querySelector('.max-w-lg');\n    card.style.transform = 'scale(0.9)';\n    card.style.opacity = '0';\n    \n    setTimeout(() => {\n        card.style.transition = 'all 0.8s ease-out';\n        card.style.transform = 'scale(1)';\n        card.style.opacity = '1';\n    }, 100);\n});`
        },
        modern: {
            html: `<!DOCTYPE html>\n<html lang="id">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Undangan Modern</title>\n    <script src="https://cdn.tailwindcss.com"></script>\n    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">\n</head>\n<body class="bg-gray-900 min-h-screen flex items-center justify-center p-4">\n    <div class="max-w-md mx-auto bg-gradient-to-br from-purple-900 to-blue-900 rounded-3xl shadow-2xl overflow-hidden">\n        <div class="relative p-12 text-white text-center">\n            <div class="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20"></div>\n            <div class="relative z-10">\n                <div class="text-6xl mb-6">💫</div>\n                <h1 class="text-3xl font-bold mb-4">WEDDING INVITATION</h1>\n                <div class="w-20 h-0.5 bg-gradient-to-r from-purple-400 to-blue-400 mx-auto"></div>\n            </div>\n        </div>\n        <div class="bg-white p-12 text-center">\n            <h2 class="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-8">\n                John & Jane\n            </h2>\n            <div class="space-y-3 mb-8">\n                <p class="font-semibold text-gray-800 text-xl">25.12.2024</p>\n                <p class="text-gray-600 text-lg">10:00 AM</p>\n                <p class="text-gray-600 text-lg">Grand Ballroom Hotel</p>\n            </div>\n            <button class="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-4 rounded-full font-semibold hover:from-purple-700 hover:to-blue-700 transition-all transform hover:scale-105 text-lg">\n                RSVP\n            </button>\n        </div>\n    </div>\n</body>\n</html>`,
            css: `@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');\n\nbody { font-family: 'Inter', sans-serif; }\n\n.invitation-card {\n    backdrop-filter: blur(20px);\n    border: 1px solid rgba(255,255,255,0.1);\n}\n\n@keyframes float {\n    0%, 100% { transform: translateY(0px); }\n    50% { transform: translateY(-10px); }\n}\n\n.floating { animation: float 3s ease-in-out infinite; }`,
            js: `document.addEventListener('DOMContentLoaded', function() {\n    const card = document.querySelector('.max-w-md');\n    card.classList.add('floating');\n});`
        },
        classic: {
            html: `<!DOCTYPE html>\n<html lang="id">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Undangan Klasik</title>\n    <script src="https://cdn.tailwindcss.com"></script>\n    <link href="https://fonts.googleapis.com/css2?family=Crimson+Text:wght@400;600&display=swap" rel="stylesheet">\n</head>\n<body class="bg-amber-50 min-h-screen flex items-center justify-center p-4">\n    <div class="max-w-lg mx-auto bg-white rounded-lg shadow-xl border-4 border-amber-200 overflow-hidden">\n        <div class="bg-amber-100 p-12 text-center border-b-4 border-amber-200">\n            <div class="text-7xl mb-6 text-amber-600">🌹</div>\n            <h1 class="text-3xl font-serif text-amber-800 mb-4">Undangan Pernikahan</h1>\n            <div class="flex justify-center items-center space-x-3">\n                <div class="w-12 h-0.5 bg-amber-400"></div>\n                <div class="w-3 h-3 bg-amber-400 rounded-full"></div>\n                <div class="w-12 h-0.5 bg-amber-400"></div>\n            </div>\n        </div>\n        <div class="p-12 text-center">\n            <div class="mb-8">\n                <p class="text-amber-700 mb-3 text-lg">Dengan penuh rasa syukur, kami mengundang</p>\n                <p class="text-amber-700 text-lg">Bapak/Ibu/Saudara/i untuk hadir dalam acara</p>\n            </div>\n            <h2 class="text-5xl font-serif text-amber-800 mb-8">John & Jane</h2>\n            <div class="bg-amber-50 p-8 rounded-xl border-2 border-amber-200 mb-8">\n                <p class="font-serif text-amber-800 font-semibold text-xl mb-3">Sabtu, 25 Desember 2024</p>\n                <p class="text-amber-700 text-lg mb-2">Pukul 10.00 WIB s/d selesai</p>\n                <p class="text-amber-700 text-lg mb-2">Hotel Grand Ballroom</p>\n                <p class="text-amber-700 text-lg">Jl. Sudirman No. 123, Jakarta</p>\n            </div>\n            <div class="text-amber-700 mb-8 text-lg">\n                <p class="mb-2">Merupakan suatu kehormatan bagi kami</p>\n                <p>apabila Bapak/Ibu/Saudara/i berkenan hadir</p>\n            </div>\n            <button class="bg-amber-500 hover:bg-amber-600 text-white px-10 py-4 rounded font-serif font-semibold text-lg transition-colors">\n                Konfirmasi Kehadiran\n            </button>\n        </div>\n    </div>\n</body>\n</html>`,
            css: `@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:wght@400;600&display=swap');\n\n.font-serif { font-family: 'Crimson Text', serif; }\n\n.invitation-card {\n    background: linear-gradient(135deg, #fef3c7 0%, #f59e0b 100%);\n    border: 3px solid #d97706;\n    box-shadow: 0 20px 40px rgba(217, 119, 6, 0.2);\n}`,
            js: `document.addEventListener('DOMContentLoaded', function() {\n    // Typewriter effect for names\n    const nameElement = document.querySelector('h2');\n    const originalText = nameElement.textContent;\n    nameElement.textContent = '';\n    \n    let i = 0;\n    function typeWriter() {\n        if (i < originalText.length) {\n            nameElement.textContent += originalText.charAt(i);\n            i++;\n            setTimeout(typeWriter, 100);\n        }\n    }\n    \n    setTimeout(typeWriter, 1000);\n});`
        }
    };
}

// AI Generation functionality
function initializeAI() {
    const aiBtn = document.getElementById('aiGenerateBtn');
    const aiModal = document.getElementById('aiModal');
    const closeAiModal = document.getElementById('closeAiModal');
    const cancelAiGenerate = document.getElementById('cancelAiGenerate');
    const startAiGenerate = document.getElementById('startAiGenerate');

    if (aiBtn) {
        aiBtn.addEventListener('click', () => {
            if (aiModal) aiModal.classList.remove('hidden');
        });
    }

    if (closeAiModal) {
        closeAiModal.addEventListener('click', () => {
            if (aiModal) aiModal.classList.add('hidden');
        });
    }

    if (cancelAiGenerate) {
        cancelAiGenerate.addEventListener('click', () => {
            if (aiModal) aiModal.classList.add('hidden');
        });
    }

    if (startAiGenerate) {
        startAiGenerate.addEventListener('click', () => {
            generateWithAI();
        });
    }
}

// Generate with AI (Simulated - replace with real Gemini API)
function generateWithAI() {
    if (isGenerating) return;
    
    isGenerating = true;
    const startBtn = document.getElementById('startAiGenerate');
    const originalText = startBtn.textContent;
    
    startBtn.textContent = '🔄 Generating...';
    startBtn.disabled = true;

    // Get user inputs
    const prompt = document.getElementById('aiDetailPrompt')?.value || '';
    const eventType = document.getElementById('eventType')?.value || 'wedding';
    const designStyle = document.getElementById('designStyle')?.value || 'elegant';

    // Simulate AI generation (replace with real API call)
    setTimeout(() => {
        const aiTemplate = generateAITemplate(prompt, eventType, designStyle);
        
        htmlEditor.setValue(aiTemplate.html);
        cssEditor.setValue(aiTemplate.css);
        jsEditor.setValue(aiTemplate.js);

        startBtn.textContent = originalText;
        startBtn.disabled = false;
        isGenerating = false;
        
        document.getElementById('aiModal')?.classList.add('hidden');
        
        showNotification('✨ Template berhasil di-generate dengan AI Gemini!', 'success');
    }, 3000);
}

// Generate AI Template (Simplified - replace with real Gemini API integration)
function generateAITemplate(prompt, eventType, designStyle) {
    // This is a simplified version. In production, you would call Gemini API
    const templates = {
        wedding: {
            elegant: {
                html: `<!DOCTYPE html>\n<html lang="id">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Undangan Pernikahan AI Generated</title>\n    <script src="https://cdn.tailwindcss.com"></script>\n    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;600;700&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">\n</head>\n<body class="bg-gradient-to-br from-rose-50 via-pink-50 to-purple-50 min-h-screen flex items-center justify-center p-4">\n    <div class="max-w-2xl mx-auto bg-white rounded-3xl shadow-2xl overflow-hidden border border-rose-200 relative">\n        <!-- Decorative elements -->\n        <div class="absolute top-4 left-4 text-rose-300 text-2xl animate-pulse">🌸</div>\n        <div class="absolute top-4 right-4 text-rose-300 text-2xl animate-pulse">🌸</div>\n        \n        <div class="relative bg-gradient-to-r from-rose-400 via-pink-500 to-purple-500 p-16 text-white text-center">\n            <div class="absolute inset-0 bg-black opacity-10"></div>\n            <div class="relative z-10">\n                <div class="text-8xl mb-8 animate-float">💕</div>\n                <h1 class="text-5xl font-serif mb-6">Wedding Invitation</h1>\n                <p class="text-xl text-rose-100 font-light">Dengan penuh kebahagiaan, kami mengundang Anda</p>\n                <div class="w-40 h-0.5 bg-white mx-auto mt-6 opacity-80"></div>\n            </div>\n        </div>\n        \n        <div class="p-16 text-center relative">\n            <div class="mb-12">\n                <h2 class="text-6xl font-dancing bg-gradient-to-r from-rose-600 to-purple-600 bg-clip-text text-transparent mb-6">\n                    ${extractNamesFromPrompt(prompt) || 'John & Jane'}\n                </h2>\n                <p class="text-xl text-gray-600 font-light">Akan melangsungkan pernikahan pada:</p>\n            </div>\n            \n            <div class="bg-gradient-to-r from-rose-50 to-purple-50 p-10 rounded-2xl mb-12 border border-rose-200 relative">\n                <div class="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-white px-4 py-2 rounded-full border border-rose-200">\n                    <span class="text-rose-500 text-sm font-semibold">📅 Detail Acara</span>\n                </div>\n                <div class="mt-4">\n                    <p class="font-semibold text-gray-800 text-2xl mb-4">${extractDateFromPrompt(prompt) || 'Sabtu, 25 Desember 2024'}</p>\n                    <p class="text-gray-600 text-lg mb-2">Pukul ${extractTimeFromPrompt(prompt) || '10.00 WIB'}</p>\n                    <p class="text-gray-600 text-lg mb-2">${extractVenueFromPrompt(prompt) || 'Hotel Grand Ballroom'}</p>\n                    <p class="text-gray-600 text-lg">${extractAddressFromPrompt(prompt) || 'Jl. Sudirman No. 123, Jakarta'}</p>\n                </div>\n            </div>\n            \n            <div class="mb-12">\n                <p class="text-lg text-gray-600 mb-4 font-light italic">\n                    "Cinta sejati tidak pernah berakhir. Kekasih mungkin pergi, tetapi mereka tidak pernah benar-benar pergi.\n                    Mereka hidup dalam hati selamanya."\n                </p>\n            </div>\n            \n            <button class="bg-gradient-to-r from-rose-500 via-pink-500 to-purple-500 text-white px-12 py-4 rounded-full hover:from-rose-600 hover:via-pink-600 hover:to-purple-600 transition-all transform hover:scale-105 shadow-xl text-lg font-semibold">\n                💌 Konfirmasi Kehadiran\n            </button>\n            \n            <div class="mt-12 text-center">\n                <p class="text-gray-500 text-sm font-light">\n                    Atas kehadiran dan doa restu Anda, kami ucapkan terima kasih\n                </p>\n            </div>\n        </div>\n    </div>\n</body>\n</html>`,
                css: `/* AI Generated CSS */\n.font-dancing {\n    font-family: 'Dancing Script', cursive;\n}\n\n.font-serif {\n    font-family: 'Playfair Display', serif;\n}\n\n@keyframes float {\n    0%, 100% {\n        transform: translateY(0px);\n    }\n    50% {\n        transform: translateY(-20px);\n    }\n}\n\n@keyframes pulse {\n    0%, 100% {\n        opacity: 1;\n    }\n    50% {\n        opacity: 0.5;\n    }\n}\n\n@keyframes fadeInUp {\n    from {\n        opacity: 0;\n        transform: translateY(30px);\n    }\n    to {\n        opacity: 1;\n        transform: translateY(0);\n    }\n}\n\n.animate-float {\n    animation: float 4s ease-in-out infinite;\n}\n\n.animate-pulse {\n    animation: pulse 2s infinite;\n}\n\n.animate-fade-in {\n    animation: fadeInUp 0.8s ease-out;\n}\n\n/* Particle background */\nbody::before {\n    content: '';\n    position: fixed;\n    top: 0;\n    left: 0;\n    width: 100%;\n    height: 100%;\n    background-image: \n        radial-gradient(circle at 20% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 50%),\n        radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),\n        radial-gradient(circle at 40% 40%, rgba(245, 158, 11, 0.1) 0%, transparent 50%);\n    pointer-events: none;\n    z-index: -1;\n}\n\n/* Responsive design */\n@media (max-width: 768px) {\n    .max-w-2xl {\n        max-width: 95%;\n        margin: 0.5rem;\n    }\n    \n    .text-6xl {\n        font-size: 3rem;\n    }\n    \n    .text-5xl {\n        font-size: 2.5rem;\n    }\n    \n    .p-16 {\n        padding: 2rem;\n    }\n    \n    .p-10 {\n        padding: 1.5rem;\n    }\n}`,
                js: `// AI Generated JavaScript\ndocument.addEventListener('DOMContentLoaded', function() {\n    // Smooth entrance animation\n    const card = document.querySelector('.max-w-2xl');\n    card.style.opacity = '0';\n    card.style.transform = 'scale(0.9) translateY(20px)';\n    \n    setTimeout(() => {\n        card.style.transition = 'all 1s cubic-bezier(0.4, 0, 0.2, 1)';\n        card.style.opacity = '1';\n        card.style.transform = 'scale(1) translateY(0)';\n    }, 200);\n\n    // Staggered animation for content\n    const elements = document.querySelectorAll('.max-w-2xl > div > div > *');\n    elements.forEach((el, index) => {\n        el.style.opacity = '0';\n        el.style.transform = 'translateY(20px)';\n        setTimeout(() => {\n            el.style.transition = 'all 0.6s ease-out';\n            el.style.opacity = '1';\n            el.style.transform = 'translateY(0)';\n        }, 500 + (index * 100));\n    });\n\n    // Enhanced button interaction\n    const confirmBtn = document.querySelector('button');\n    if (confirmBtn) {\n        confirmBtn.addEventListener('click', function(e) {\n            e.preventDefault();\n            \n            // Button animation\n            this.style.transform = 'scale(0.95)';\n            setTimeout(() => {\n                this.style.transform = 'scale(1)';\n            }, 150);\n            \n            // Show enhanced confirmation\n            showEnhancedConfirmation();\n        });\n    }\n\n    // Floating hearts effect\n    createFloatingHearts();\n    \n    // Parallax effect\n    window.addEventListener('scroll', function() {\n        const scrolled = window.pageYOffset;\n        const parallax = document.querySelector('.max-w-2xl');\n        if (parallax) {\n            const speed = scrolled * 0.05;\n            parallax.style.transform = \`translateY(\${speed}px)\`;\n        }\n    });\n});\n\n// Enhanced confirmation modal\nfunction showEnhancedConfirmation() {\n    const modal = document.createElement('div');\n    modal.className = 'fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 backdrop-blur-sm';\n    modal.innerHTML = \`\n        <div class="bg-white rounded-3xl p-12 max-w-lg mx-4 text-center transform scale-0 transition-transform duration-500 shadow-2xl">\n            <div class="text-8xl mb-6 animate-bounce">🎉</div>\n            <h3 class="text-3xl font-bold text-gray-800 mb-6 font-serif">Terima Kasih!</h3>\n            <p class="text-gray-600 mb-8 text-lg leading-relaxed">\n                Konfirmasi kehadiran Anda telah diterima dengan penuh sukacita. \n                Kami sangat menantikan kehadiran Anda di hari bahagia kami!\n            </p>\n            <div class="flex justify-center space-x-4">\n                <button onclick="closeModal(this)" class="bg-gradient-to-r from-rose-500 to-pink-500 text-white px-8 py-3 rounded-full hover:from-rose-600 hover:to-pink-600 transition-all transform hover:scale-105">\n                    Tutup\n                </button>\n            </div>\n        </div>\n    `;\n    \n    document.body.appendChild(modal);\n    \n    // Animate modal\n    setTimeout(() => {\n        modal.querySelector('div').style.transform = 'scale(1)';\n    }, 100);\n}\n\n// Close modal\nfunction closeModal(btn) {\n    const modal = btn.closest('.fixed');\n    modal.querySelector('div').style.transform = 'scale(0)';\n    setTimeout(() => {\n        modal.remove();\n    }, 500);\n}\n\n// Floating hearts effect\nfunction createFloatingHearts() {\n    function createHeart() {\n        const heart = document.createElement('div');\n        heart.innerHTML = '💕';\n        heart.className = 'fixed text-2xl pointer-events-none opacity-70';\n        heart.style.left = Math.random() * window.innerWidth + 'px';\n        heart.style.top = window.innerHeight + 'px';\n        heart.style.zIndex = '5';\n        document.body.appendChild(heart);\n        \n        const animation = heart.animate([\n            { \n                transform: 'translateY(0px) rotate(0deg)', \n                opacity: 0.7 \n            },\n            { \n                transform: `translateY(-${window.innerHeight + 100}px) rotate(360deg)`, \n                opacity: 0 \n            }\n        ], {\n            duration: 6000 + Math.random() * 3000,\n            easing: 'linear'\n        });\n        \n        animation.onfinish = () => heart.remove();\n    }\n    \n    // Create hearts periodically\n    setInterval(createHeart, 2000);\n}\n\n// Extract information from AI prompt\nfunction extractNamesFromPrompt(prompt) {\n    const namePattern = /nama[\s:]*([^\n,]+)/i;\n    const match = prompt.match(namePattern);\n    return match ? match[1].trim() : null;\n}\n\nfunction extractDateFromPrompt(prompt) {\n    const datePattern = /tanggal[\s:]*([^\n,]+)/i;\n    const match = prompt.match(datePattern);\n    return match ? match[1].trim() : null;\n}\n\nfunction extractTimeFromPrompt(prompt) {\n    const timePattern = /waktu[\s:]*([^\n,]+)/i;\n    const match = prompt.match(timePattern);\n    return match ? match[1].trim() : null;\n}\n\nfunction extractVenueFromPrompt(prompt) {\n    const venuePattern = /tempat[\s:]*([^\n,]+)/i;\n    const match = prompt.match(venuePattern);\n    return match ? match[1].trim() : null;\n}\n\nfunction extractAddressFromPrompt(prompt) {\n    const addressPattern = /alamat[\s:]*([^\n,]+)/i;\n    const match = prompt.match(addressPattern);\n    return match ? match[1].trim() : null;\n}\n            },\n            birthday: {\n                modern: {\n                    html: `<!DOCTYPE html>\n<html lang="id">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Undangan Ulang Tahun</title>\n    <script src="https://cdn.tailwindcss.com"></script>\n</head>\n<body class="bg-gradient-to-br from-yellow-400 via-orange-500 to-red-500 min-h-screen flex items-center justify-center p-4">\n    <div class="max-w-md mx-auto bg-white rounded-3xl shadow-2xl overflow-hidden">\n        <div class="bg-gradient-to-r from-yellow-400 to-orange-500 p-12 text-white text-center">\n            <div class="text-8xl mb-6">🎂</div>\n            <h1 class="text-4xl font-bold mb-4">Birthday Party</h1>\n        </div>\n        <div class="p-12 text-center">\n            <h2 class="text-4xl font-bold text-orange-600 mb-8">Happy Birthday!</h2>\n            <div class="mb-8">\n                <p class="text-xl font-semibold mb-2">25 Desember 2024</p>\n                <p class="text-gray-600">Pukul 19.00 WIB</p>\n            </div>\n            <button class="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 rounded-full transition-all">\n                Konfirmasi Kehadiran\n            </button>\n        </div>\n    </div>\n</body>\n</html>`,\n                    css: `.party-card { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }`,\n                    js: `console.log('Birthday template loaded');`\n                }\n            }\n        }\n    };\n    \n    return templates[eventType]?.[designStyle] || templates.wedding.elegant;\n}\n\n// Export functionality\nfunction initializeExport() {\n    const exportBtn = document.getElementById('exportBtn');\n    const exportModal = document.getElementById('exportModal');\n    const closeExportModal = document.getElementById('closeExportModal');\n    const cancelExport = document.getElementById('cancelExport');\n\n    if (exportBtn) {\n        exportBtn.addEventListener('click', () => {\n            if (exportModal) exportModal.classList.remove('hidden');\n        });\n    }\n\n    if (closeExportModal) {\n        closeExportModal.addEventListener('click', () => {\n            if (exportModal) exportModal.classList.add('hidden');\n        });\n    }\n\n    if (cancelExport) {\n        cancelExport.addEventListener('click', () => {\n            if (exportModal) exportModal.classList.add('hidden');\n        });\n    }\n\n    // Export format buttons\n    document.querySelectorAll('.export-format').forEach(btn => {\n        btn.addEventListener('click', () => {\n            const format = btn.dataset.format;\n            exportTemplate(format);\n        });\n    });\n}\n\n// Export template\nfunction exportTemplate(format) {\n    const html = htmlEditor.getValue();\n    const css = cssEditor.getValue();\n    const js = jsEditor.getValue();\n\n    switch (format) {\n        case 'html':\n            downloadFile('undangan.html', html, 'text/html');\n            break;\n        case 'zip':\n            createZipFile(html, css, js);\n            break;\n        case 'pdf':\n            generatePDF();\n            break;\n        case 'image':\n            generateImage();\n            break;\n    }\n\n    document.getElementById('exportModal')?.classList.add('hidden');\n    showNotification(`📁 Template berhasil diekspor sebagai ${format.toUpperCase()}!`, 'success');\n}\n\n// Download file\nfunction downloadFile(filename, content, mimeType) {\n    const blob = new Blob([content], { type: mimeType });\n    const url = URL.createObjectURL(blob);\n    const a = document.createElement('a');\n    a.href = url;\n    a.download = filename;\n    document.body.appendChild(a);\n    a.click();\n    document.body.removeChild(a);\n    URL.revokeObjectURL(url);\n}\n\n// Create ZIP file (simplified)\nfunction createZipFile(html, css, js) {\n    // This would require a ZIP library like JSZip\n    // For now, we'll download individual files\n    downloadFile('index.html', html, 'text/html');\n    downloadFile('style.css', css, 'text/css');\n    downloadFile('script.js', js, 'text/javascript');\n}\n\n// Generate PDF (simplified)\nfunction generatePDF() {\n    // This would require a PDF library like jsPDF\n    showNotification('📄 Fitur PDF akan segera tersedia!', 'info');\n}\n\n// Generate Image (simplified)\nfunction generateImage() {\n    // This would require html2canvas or similar\n    showNotification('🖼️ Fitur gambar akan segera tersedia!', 'info');\n}\n\n// Template management\nfunction initializeTemplateManagement() {\n    // New template\n    document.getElementById('newTemplateBtn')?.addEventListener('click', () => {\n        if (confirm('Buat template baru? Perubahan yang belum disimpan akan hilang.')) {\n            setDefaultTemplate();\n            currentTemplate = null;\n            document.getElementById('templateName').value = '';\n            showNotification('📄 Template baru berhasil dibuat!', 'success');\n        }\n    });\n\n    // Save template\n    document.getElementById('saveTemplateBtn')?.addEventListener('click', saveTemplate);\n\n    // Preview template\n    document.getElementById('previewBtn')?.addEventListener('click', () => {\n        const previewWindow = window.open('', '_blank');\n        const html = htmlEditor.getValue();\n        const css = cssEditor.getValue();\n        const js = jsEditor.getValue();\n        \n        const fullHtml = html.replace('</head>', `<style>${css}</style></head>`).replace('</body>', `<script>${js}</script></body>`);\n        previewWindow.document.write(fullHtml);\n        previewWindow.document.close();\n    });\n\n    // Load template from library\n    document.querySelectorAll('.template-item').forEach(item => {\n        item.addEventListener('click', () => {\n            const templateId = item.dataset.templateId;\n            loadTemplate(templateId);\n        });\n    });\n}\n\n// Save template\nfunction saveTemplate() {\n    const templateName = document.getElementById('templateName')?.value;\n    if (!templateName) {\n        showNotification('❌ Nama template harus diisi!', 'error');\n        return;\n    }\n\n    const templateData = {\n        name: templateName,\n        html_content: htmlEditor.getValue(),\n        css_content: cssEditor.getValue(),\n        js_content: jsEditor.getValue(),\n        category: document.getElementById('templateCategory')?.value || 'wedding',\n        description: document.getElementById('templateDescription')?.value || ''\n    };\n\n    // Send to server\n    fetch('/editor/save-template/', {\n        method: 'POST',\n        headers: {\n            'Content-Type': 'application/json',\n            'X-CSRFToken': getCsrfToken()\n        },\n        body: JSON.stringify(templateData)\n    })\n    .then(response => response.json())\n    .then(data => {\n        if (data.success) {\n            currentTemplate = data.template_id;\n            showNotification('💾 Template berhasil disimpan!', 'success');\n        } else {\n            showNotification('❌ Gagal menyimpan template: ' + data.error, 'error');\n        }\n    })\n    .catch(error => {\n        console.error('Error:', error);\n        showNotification('❌ Terjadi kesalahan saat menyimpan!', 'error');\n    });\n}\n\n// Load template\nfunction loadTemplate(templateId) {\n    fetch(`/editor/load-template/${templateId}/`)\n    .then(response => response.json())\n    .then(data => {\n        if (data.success) {\n            htmlEditor.setValue(data.html_content || '');\n            cssEditor.setValue(data.css_content || '');\n            jsEditor.setValue(data.js_content || '');\n            \n            document.getElementById('templateName').value = data.name || '';\n            document.getElementById('templateCategory').value = data.category || 'wedding';\n            document.getElementById('templateDescription').value = data.description || '';\n            \n            currentTemplate = templateId;\n            showNotification('📂 Template berhasil dimuat!', 'success');\n        } else {\n            showNotification('❌ Gagal memuat template: ' + data.error, 'error');\n        }\n    })\n    .catch(error => {\n        console.error('Error:', error);\n        showNotification('❌ Terjadi kesalahan saat memuat template!', 'error');\n    });\n}\n\n// Notification system\nfunction initializeNotifications() {\n    // Create notification container if it doesn't exist\n    if (!document.getElementById('notificationContainer')) {\n        const container = document.createElement('div');\n        container.id = 'notificationContainer';\n        container.className = 'fixed top-4 right-4 z-50 space-y-2';\n        document.body.appendChild(container);\n    }\n}\n\n// Show notification\nfunction showNotification(message, type = 'info') {\n    const container = document.getElementById('notificationContainer');\n    if (!container) return;\n\n    const notification = document.createElement('div');\n    const bgColor = {\n        success: 'bg-green-500',\n        error: 'bg-red-500',\n        warning: 'bg-yellow-500',\n        info: 'bg-blue-500'\n    }[type] || 'bg-blue-500';\n\n    notification.className = `${bgColor} text-white px-6 py-3 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300 max-w-sm`;\n    notification.innerHTML = `\n        <div class="flex items-center justify-between">\n            <span class="text-sm font-medium">${message}</span>\n            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">\n                ✕\n            </button>\n        </div>\n    `;\n\n    container.appendChild(notification);\n\n    // Animate in\n    setTimeout(() => {\n        notification.style.transform = 'translateX(0)';\n    }, 100);\n\n    // Auto remove after 5 seconds\n    setTimeout(() => {\n        if (notification.parentElement) {\n            notification.style.transform = 'translateX(100%)';\n            setTimeout(() => {\n                if (notification.parentElement) {\n                    notification.remove();\n                }\n            }, 300);\n        }\n    }, 5000);\n}\n\n// Utility functions\nfunction debounce(func, wait) {\n    let timeout;\n    return function executedFunction(...args) {\n        const later = () => {\n            clearTimeout(timeout);\n            func(...args);\n        };\n        clearTimeout(timeout);\n        timeout = setTimeout(later, wait);\n    };\n}\n\nfunction getCsrfToken() {\n    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';\n}\n\n// Keyboard shortcuts\ndocument.addEventListener('keydown', function(e) {\n    // Ctrl+S to save\n    if (e.ctrlKey && e.key === 's') {\n        e.preventDefault();\n        saveTemplate();\n    }\n    \n    // Ctrl+N for new template\n    if (e.ctrlKey && e.key === 'n') {\n        e.preventDefault();\n        document.getElementById('newTemplateBtn')?.click();\n    }\n    \n    // Ctrl+P for preview\n    if (e.ctrlKey && e.key === 'p') {\n        e.preventDefault();\n        document.getElementById('previewBtn')?.click();\n    }\n});