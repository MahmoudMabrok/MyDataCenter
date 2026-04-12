const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const resultsSection = document.getElementById('results-section');
const resultsGrid = document.getElementById('results-grid');
const downloadAllBtn = document.getElementById('download-all-btn');
const presetButtons = document.querySelectorAll('.preset-btn');
const customInputs = document.getElementById('custom-inputs');
const customWidthInput = document.getElementById('width');
const customHeightInput = document.getElementById('height');

let activeWidth = 512;
let activeHeight = 512;
let processedImages = [];

// Initialize
function init() {
    setupTabs();
    setupEventListeners();
}

function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.add('hidden'));
            document.getElementById(`tab-${btn.dataset.tab}`).classList.remove('hidden');
            lucide.createIcons();
        });
    });
}

function setupEventListeners() {
    // Preset selection
    presetButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            presetButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            if (btn.id === 'custom-preset-btn') {
                customInputs.classList.remove('hidden');
                activeWidth = parseInt(customWidthInput.value);
                activeHeight = parseInt(customHeightInput.value);
            } else {
                customInputs.classList.add('hidden');
                activeWidth = parseInt(btn.dataset.width);
                activeHeight = parseInt(btn.dataset.height);
            }
        });
    });

    // Custom input changes
    customWidthInput.addEventListener('input', () => {
        if (document.getElementById('custom-preset-btn').classList.contains('active')) {
            activeWidth = parseInt(customWidthInput.value) || 0;
        }
    });

    customHeightInput.addEventListener('input', () => {
        if (document.getElementById('custom-preset-btn').classList.contains('active')) {
            activeHeight = parseInt(customHeightInput.value) || 0;
        }
    });

    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    });

    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // Download All
    downloadAllBtn.addEventListener('click', downloadAllAsZip);
}

async function handleFiles(files) {
    const fileList = Array.from(files).filter(file => file.type.startsWith('image/'));
    
    if (fileList.length === 0) return;

    resultsSection.classList.remove('hidden');
    
    for (const file of fileList) {
        await processImage(file);
    }
}

function processImage(file) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = activeWidth;
                canvas.height = activeHeight;
                const ctx = canvas.getContext('2d');

                // Clear canvas (transparency)
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Use better scaling (we draw once, but let's just do a simple fit/fill)
                // For icons/screenshots, usually we want to fill or center. 
                // Let's implement "fit with aspect ratio preservation" for a clean look.
                const scale = Math.min(canvas.width / img.width, canvas.height / img.height);
                const x = (canvas.width / 2) - (img.width / 2) * scale;
                const y = (canvas.height / 2) - (img.height / 2) * scale;
                
                ctx.imageSmoothingEnabled = true;
                ctx.imageSmoothingQuality = 'high';
                ctx.drawImage(img, x, y, img.width * scale, img.height * scale);

                const dataUrl = canvas.toDataURL('image/png');
                const processed = {
                    name: `resized_${activeWidth}x${activeHeight}_${file.name.split('.')[0]}.png`,
                    dataUrl: dataUrl,
                    width: activeWidth,
                    height: activeHeight
                };

                processedImages.push(processed);
                renderResult(processed);
                resolve();
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });
}

function renderResult(processed) {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.innerHTML = `
        <div class="result-preview">
            <img src="${processed.dataUrl}" alt="${processed.name}">
        </div>
        <div class="result-info">
            <h4>${processed.name}</h4>
            <p>${processed.width} x ${processed.height} px • PNG</p>
            <button class="download-btn" onclick="downloadImage('${processed.dataUrl}', '${processed.name}')">
                <i data-lucide="download"></i> Download
            </button>
        </div>
    `;
    resultsGrid.appendChild(card);
    lucide.createIcons();
    
    // Scroll to results if first batch
    if (resultsGrid.children.length === 1) {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

function downloadImage(dataUrl, name) {
    const link = document.createElement('a');
    link.href = dataUrl;
    link.download = name;
    link.click();
}

async function downloadAllAsZip() {
    if (processedImages.length === 0) return;

    const zip = new JSZip();
    const downloadBtn = document.getElementById('download-all-btn');
    const originalText = downloadBtn.innerHTML;
    
    downloadBtn.disabled = true;
    downloadBtn.innerHTML = '<i data-lucide="loader-2" class="spin"></i> Zipping...';
    lucide.createIcons();

    processedImages.forEach(img => {
        // Remove data URL prefix
        const base64Data = img.dataUrl.replace(/^data:image\/(png|jpg|webp);base64,/, "");
        zip.file(img.name, base64Data, { base64: true });
    });

    const content = await zip.generateAsync({ type: "blob" });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(content);
    link.download = `pixelperfect_batch_${Date.now()}.zip`;
    link.click();

    downloadBtn.disabled = false;
    downloadBtn.innerHTML = originalText;
    lucide.createIcons();
}

// Global expose
window.downloadImage = downloadImage;

init();
