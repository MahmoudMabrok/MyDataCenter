class FeatureGraphicEditor {
    constructor() {
        this.canvas = document.getElementById('fg-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.layers = [];
        this.selectedIndex = -1;
        this.bgColor = '#1a1a2e';
        this.bgImage = null;
        this.exportFormat = 'image/png';

        this._dragActive = false;
        this._dragOffsetX = 0;
        this._dragOffsetY = 0;

        this._resizeHandle = null;   // active handle id, or null
        this._resizeOrigin = null;   // { x, y, width, height, mouseX, mouseY }

        this._setupEventListeners();
        this.render();
    }

    // Convert a mouse/touch event clientX/Y to canvas logical coordinates
    _toCanvasCoords(clientX, clientY) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = 1024 / rect.width;
        const scaleY = 500 / rect.height;
        return {
            x: (clientX - rect.left) * scaleX,
            y: (clientY - rect.top) * scaleY
        };
    }

    render() {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, 1024, 500);

        // Background
        if (this.bgImage) {
            ctx.drawImage(this.bgImage, 0, 0, 1024, 500);
        } else {
            ctx.fillStyle = this.bgColor;
            ctx.fillRect(0, 0, 1024, 500);
        }

        // Layers
        this.layers.forEach((layer, i) => {
            this._drawLayer(layer);
            if (i === this.selectedIndex) {
                this._drawSelection(layer);
            }
        });
    }

    _drawLayer(layer) {
        const ctx = this.ctx;
        if (layer.type === 'image') {
            ctx.drawImage(layer.img, layer.x, layer.y, layer.width, layer.height);
        } else if (layer.type === 'text') {
            const style = `${layer.italic ? 'italic ' : ''}${layer.bold ? 'bold ' : ''}${layer.fontSize}px ${layer.fontFamily}`;
            ctx.font = style;
            ctx.fillStyle = layer.color;
            ctx.textBaseline = 'top';
            ctx.fillText(layer.content, layer.x, layer.y);
            // Update bounding box based on measured text
            const metrics = ctx.measureText(layer.content);
            layer.width = metrics.width;
            layer.height = layer.fontSize * 1.2;
        }
    }

    _getHandles(layer) {
        const { x, y, width, height } = layer;
        const cx = x + width / 2;
        const cy = y + height / 2;
        const r = x + width;
        const b = y + height;
        return [
            { id: 'TL', x, y },
            { id: 'TC', x: cx, y },
            { id: 'TR', x: r, y },
            { id: 'ML', x, y: cy },
            { id: 'MR', x: r, y: cy },
            { id: 'BL', x, y: b },
            { id: 'BC', x: cx, y: b },
            { id: 'BR', x: r, y: b }
        ];
    }

    _drawSelection(layer) {
        const ctx = this.ctx;
        ctx.strokeStyle = '#6366f1';
        ctx.lineWidth = 2;
        ctx.setLineDash([6, 3]);
        ctx.strokeRect(layer.x - 4, layer.y - 4, layer.width + 8, layer.height + 8);
        ctx.setLineDash([]);

        if (layer.type !== 'image') return;

        // Draw 8 handles
        const HALF = 4; // half of 8px square
        this._getHandles(layer).forEach(h => {
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#6366f1';
            ctx.lineWidth = 2;
            ctx.fillRect(h.x - HALF, h.y - HALF, HALF * 2, HALF * 2);
            ctx.strokeRect(h.x - HALF, h.y - HALF, HALF * 2, HALF * 2);
        });
    }

    _setupEventListeners() {
        // Background color
        document.getElementById('fg-bg-color').addEventListener('input', (e) => {
            this.bgColor = e.target.value;
            this.bgImage = null;
            this.render();
        });

        // Background image
        document.getElementById('fg-bg-image-btn').addEventListener('click', () => {
            document.getElementById('fg-bg-image-input').click();
        });
        document.getElementById('fg-bg-image-input').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            this._loadImageFile(file, (img) => {
                this.bgImage = img;
                this.render();
            });
        });

        this._setupPhotoControls();

        this._setupCanvasInteraction();

        this._setupTextControls();

        this._setupTextEditing();

        this._setupTextStyleControls();

        this._setupExport();
    }

    _loadImageFile(file, callback) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => callback(img);
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    _addLayer(layer) {
        this.layers.push(layer);
        this.selectedIndex = this.layers.length - 1;
        this._updateLayersList();
        this.render();
    }

    _removeLayer(index) {
        this.layers.splice(index, 1);
        if (this.selectedIndex >= this.layers.length) {
            this.selectedIndex = this.layers.length - 1;
        }
        this._updateLayersList();
        this.render();
    }

    _selectLayer(index) {
        this.selectedIndex = index;
        this._updateLayersList();
        this._updateTextStylePanel();
        this.render();
    }

    _updateLayersList() {
        const list = document.getElementById('fg-layers-list');
        list.innerHTML = '';

        if (this.layers.length === 0) {
            list.innerHTML = '<li class="fg-no-layers">No layers yet</li>';
            return;
        }

        this.layers.forEach((layer, i) => {
            const li = document.createElement('li');
            li.className = `fg-layer-item${i === this.selectedIndex ? ' selected' : ''}`;
            const icon = layer.type === 'image' ? 'image' : 'type';
            const label = layer.type === 'image' ? `Photo ${i + 1}` : `"${layer.content.slice(0, 12)}${layer.content.length > 12 ? '…' : ''}"`;
            li.innerHTML = `
                <i data-lucide="${icon}" style="width:0.75rem;height:0.75rem;flex-shrink:0"></i>
                <span class="fg-layer-label">${label}</span>
                <button class="fg-layer-delete" data-index="${i}" title="Delete layer">
                    <i data-lucide="trash-2"></i>
                </button>
            `;
            li.addEventListener('click', (e) => {
                if (!e.target.closest('.fg-layer-delete')) {
                    this._selectLayer(i);
                }
            });
            li.querySelector('.fg-layer-delete').addEventListener('click', () => {
                this._removeLayer(i);
            });
            list.appendChild(li);
        });

        lucide.createIcons();
    }

    _updateTextStylePanel() {
        const panel = document.getElementById('fg-text-style-panel');
        const layer = this.layers[this.selectedIndex];
        if (layer && layer.type === 'text') {
            panel.classList.remove('hidden');
            document.getElementById('fg-font-family').value = layer.fontFamily;
            document.getElementById('fg-font-size').value = layer.fontSize;
            document.getElementById('fg-text-color').value = layer.color;
            document.getElementById('fg-bold-btn').classList.toggle('active', layer.bold);
            document.getElementById('fg-italic-btn').classList.toggle('active', layer.italic);
        } else {
            panel.classList.add('hidden');
        }
    }

    _setupPhotoControls() {
        document.getElementById('fg-add-photo-btn').addEventListener('click', () => {
            document.getElementById('fg-photo-input').click();
        });

        document.getElementById('fg-photo-input').addEventListener('change', (e) => {
            Array.from(e.target.files).forEach(file => {
                this._loadImageFile(file, (img) => {
                    const { width, height } = this._fitSize(img.width, img.height, 400, 300);
                    this._addLayer({
                        type: 'image',
                        img,
                        x: 50,
                        y: 50,
                        width,
                        height
                    });
                });
            });
            e.target.value = '';
        });

        // Clipboard paste (Ctrl+V / Cmd+V)
        document.addEventListener('paste', (e) => {
            // Only handle paste when Feature Graphic tab is active
            if (!fgEditor) return;
            const items = e.clipboardData.items;
            for (const item of items) {
                if (item.type.startsWith('image/')) {
                    const blob = item.getAsFile();
                    this._loadImageFile(blob, (img) => {
                        const { width, height } = this._fitSize(img.width, img.height, 400, 300);
                        this._addLayer({
                            type: 'image',
                            img,
                            x: 50,
                            y: 50,
                            width,
                            height
                        });
                    });
                    break;
                }
            }
        });
    }

    _hitHandle(x, y) {
        if (this.selectedIndex === -1) return null;
        const layer = this.layers[this.selectedIndex];
        if (layer.type !== 'image') return null;
        const HIT = 8;
        for (const h of this._getHandles(layer)) {
            if (Math.abs(x - h.x) <= HIT && Math.abs(y - h.y) <= HIT) return h.id;
        }
        return null;
    }

    _setupCanvasInteraction() {
        const CURSOR_MAP = {
            TL: 'nwse-resize', TC: 'ns-resize',   TR: 'nesw-resize',
            ML: 'ew-resize',                        MR: 'ew-resize',
            BL: 'nesw-resize', BC: 'ns-resize',    BR: 'nwse-resize'
        };

        this.canvas.addEventListener('mousedown', (e) => {
            const { x, y } = this._toCanvasCoords(e.clientX, e.clientY);

            const handle = this._hitHandle(x, y);
            if (handle) {
                const layer = this.layers[this.selectedIndex];
                this._resizeHandle = handle;
                this._resizeOrigin = {
                    x: layer.x, y: layer.y,
                    width: layer.width, height: layer.height,
                    mouseX: x, mouseY: y
                };
                this.canvas.style.cursor = CURSOR_MAP[handle];
                return;
            }

            let hit = -1;
            for (let i = this.layers.length - 1; i >= 0; i--) {
                const l = this.layers[i];
                if (x >= l.x && x <= l.x + l.width && y >= l.y && y <= l.y + l.height) {
                    hit = i;
                    break;
                }
            }
            if (hit !== -1) {
                this._selectLayer(hit);
                this._dragActive = true;
                this._dragOffsetX = x - this.layers[hit].x;
                this._dragOffsetY = y - this.layers[hit].y;
                this.canvas.style.cursor = 'grabbing';
            } else {
                this.selectedIndex = -1;
                this._updateLayersList();
                this._updateTextStylePanel();
                this.render();
            }
        });

        this.canvas.addEventListener('mousemove', (e) => {
            const { x, y } = this._toCanvasCoords(e.clientX, e.clientY);

            if (this._resizeHandle) {
                this._applyResize(x, y);
                return;
            }

            if (this._dragActive && this.selectedIndex !== -1) {
                this.layers[this.selectedIndex].x = x - this._dragOffsetX;
                this.layers[this.selectedIndex].y = y - this._dragOffsetY;
                this.render();
                return;
            }

            const handle = this._hitHandle(x, y);
            if (handle) {
                this.canvas.style.cursor = CURSOR_MAP[handle];
                return;
            }
            for (let i = this.layers.length - 1; i >= 0; i--) {
                const l = this.layers[i];
                if (x >= l.x && x <= l.x + l.width && y >= l.y && y <= l.y + l.height) {
                    this.canvas.style.cursor = 'grab';
                    return;
                }
            }
            this.canvas.style.cursor = 'default';
        });

        const endInteraction = () => {
            this._dragActive = false;
            this._resizeHandle = null;
            this._resizeOrigin = null;
            this.canvas.classList.remove('dragging');
            this.canvas.style.cursor = 'default';
        };
        this.canvas.addEventListener('mouseup', endInteraction);
        this.canvas.addEventListener('mouseleave', endInteraction);
    }

    _setupTextControls() {
        document.getElementById('fg-add-text-btn').addEventListener('click', () => {
            this._addLayer({
                type: 'text',
                content: 'Your Text',
                x: 80,
                y: 200,
                width: 0,
                height: 0,
                fontFamily: 'Inter, sans-serif',
                fontSize: 64,
                color: '#ffffff',
                bold: false,
                italic: false
            });
            this._updateTextStylePanel();
        });
    }

    _setupTextEditing() {
        const overlay = document.getElementById('fg-text-edit-overlay');
        const input = document.getElementById('fg-text-edit-input');

        this.canvas.addEventListener('dblclick', (e) => {
            const { x, y } = this._toCanvasCoords(e.clientX, e.clientY);
            for (let i = this.layers.length - 1; i >= 0; i--) {
                const l = this.layers[i];
                if (l.type === 'text' && x >= l.x && x <= l.x + l.width && y >= l.y && y <= l.y + l.height) {
                    this._openTextEdit(i, overlay, input);
                    return;
                }
            }
        });

        const commitEdit = () => {
            const idx = parseInt(overlay.dataset.editingIndex);
            if (isNaN(idx)) return;
            this.layers[idx].content = input.value || 'Text';
            overlay.classList.add('hidden');
            overlay.classList.remove('active');
            overlay.dataset.editingIndex = '';
            this._updateLayersList();
            this.render();
        };

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                commitEdit();
            }
            if (e.key === 'Escape') {
                commitEdit();
            }
        });

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) commitEdit();
        });
    }

    _openTextEdit(layerIndex, overlay, input) {
        const layer = this.layers[layerIndex];
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = rect.width / 1024;
        const scaleY = rect.height / 500;
        const wrapperRect = this.canvas.parentElement.getBoundingClientRect();

        const left = rect.left - wrapperRect.left + layer.x * scaleX;
        const top = rect.top - wrapperRect.top + layer.y * scaleY;

        input.style.left = `${left}px`;
        input.style.top = `${top}px`;
        input.style.minWidth = `${Math.max(layer.width * scaleX, 120)}px`;
        input.value = layer.content;

        overlay.dataset.editingIndex = layerIndex;
        overlay.classList.remove('hidden');
        overlay.classList.add('active');
        input.focus();
        input.select();
    }

    _setupTextStyleControls() {
        const update = (prop, value) => {
            const layer = this.layers[this.selectedIndex];
            if (!layer || layer.type !== 'text') return;
            layer[prop] = value;
            this.render();
        };

        document.getElementById('fg-font-family').addEventListener('change', (e) => {
            update('fontFamily', e.target.value);
        });

        document.getElementById('fg-font-size').addEventListener('input', (e) => {
            update('fontSize', parseInt(e.target.value) || 48);
        });

        document.getElementById('fg-text-color').addEventListener('input', (e) => {
            update('color', e.target.value);
        });

        document.getElementById('fg-bold-btn').addEventListener('click', () => {
            const layer = this.layers[this.selectedIndex];
            if (!layer || layer.type !== 'text') return;
            layer.bold = !layer.bold;
            document.getElementById('fg-bold-btn').classList.toggle('active', layer.bold);
            this.render();
        });

        document.getElementById('fg-italic-btn').addEventListener('click', () => {
            const layer = this.layers[this.selectedIndex];
            if (!layer || layer.type !== 'text') return;
            layer.italic = !layer.italic;
            document.getElementById('fg-italic-btn').classList.toggle('active', layer.italic);
            this.render();
        });
    }

    _setupExport() {
        // Format toggle
        document.querySelectorAll('.fg-format-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.fg-format-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.exportFormat = btn.dataset.format;
            });
        });

        // Save
        document.getElementById('fg-save-btn').addEventListener('click', () => {
            // Deselect so no selection highlight appears in exported image
            const prevSelected = this.selectedIndex;
            this.selectedIndex = -1;
            this.render();

            const ext = this.exportFormat === 'image/jpeg' ? 'jpg' : 'png';
            const quality = this.exportFormat === 'image/jpeg' ? 0.95 : undefined;

            this.canvas.toBlob((blob) => {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `feature-graphic.${ext}`;
                a.click();
                URL.revokeObjectURL(url);

                // Restore selection
                this.selectedIndex = prevSelected;
                this.render();
            }, this.exportFormat, quality);
        });
    }

    _fitSize(imgWidth, imgHeight, maxW, maxH) {
        if (!imgWidth || !imgHeight) return { width: maxW, height: maxH };
        let w = Math.min(imgWidth, maxW);
        let h = w * (imgHeight / imgWidth);
        if (h > maxH) {
            h = maxH;
            w = h * (imgWidth / imgHeight);
        }
        return { width: Math.round(w), height: Math.round(h) };
    }

    _applyResize(mouseX, mouseY) {
        const o = this._resizeOrigin;
        const layer = this.layers[this.selectedIndex];
        const h = this._resizeHandle;
        const dx = mouseX - o.mouseX;
        const dy = mouseY - o.mouseY;
        const MIN = 10;

        let { x, y, width, height } = o;

        if (h === 'TL') {
            width  = Math.max(MIN, o.width  - dx);
            height = Math.max(MIN, o.height - dy);
            x = o.x + (o.width  - width);
            y = o.y + (o.height - height);
        } else if (h === 'TC') {
            height = Math.max(MIN, o.height - dy);
            y = o.y + (o.height - height);
        } else if (h === 'TR') {
            width  = Math.max(MIN, o.width  + dx);
            height = Math.max(MIN, o.height - dy);
            y = o.y + (o.height - height);
        } else if (h === 'ML') {
            width = Math.max(MIN, o.width - dx);
            x = o.x + (o.width - width);
        } else if (h === 'MR') {
            width = Math.max(MIN, o.width + dx);
        } else if (h === 'BL') {
            width  = Math.max(MIN, o.width  - dx);
            height = Math.max(MIN, o.height + dy);
            x = o.x + (o.width - width);
        } else if (h === 'BC') {
            height = Math.max(MIN, o.height + dy);
        } else if (h === 'BR') {
            width  = Math.max(MIN, o.width  + dx);
            height = Math.max(MIN, o.height + dy);
        }

        layer.x = x;
        layer.y = y;
        layer.width = width;
        layer.height = height;
        this.render();
    }
}

// Initialize when Feature Graphic tab is first opened
let fgEditor = null;
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        if (btn.dataset.tab === 'feature-graphic' && !fgEditor) {
            fgEditor = new FeatureGraphicEditor();
        }
    });
});
