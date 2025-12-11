// --- 1. CONFIG & UTILS ---
const API_BASE = '/api/shipment_forms'; 

const utils = {
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    async fetch(url, options = {}) {
        const headers = options.headers || {};
        if (options.method && options.method !== 'GET') {
            headers['X-CSRFToken'] = this.getCookie('csrftoken');
        }
        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }

        try {
            const response = await fetch(url, { ...options, headers });
            if (response.status === 204) return null;
            if (!response.ok) {
                const err = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(err.detail || JSON.stringify(err));
            }
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return await response.json();
            }
            return response; 
        } catch (err) {
            ui.toast(err.message, 'error');
            console.error("Fetch Error:", err);
            throw err;
        }
    }
};

// --- 2. STATE MANAGEMENT ---
const state = {
    templates: [],
    currentTemplateId: null,
    currentTemplateFields: {},
    editingDocId: null, // ID of the document currently being edited
    documents: [],      // Local cache of history
    lastPreviewBlob: null 
};

// --- 3. UI CONTROLLER ---
const ui = {
    els: {
        templateList: document.getElementById('templateList'),
        workspace: document.getElementById('workspace'),
        emptyState: document.getElementById('emptyState'),
        configName: document.getElementById('configName'),
        configKeyField: document.getElementById('configKeyField'),
        dynamicForm: document.getElementById('dynamicForm'),
        historyList: document.getElementById('historyList'),
        uploadModal: document.getElementById('uploadModal'),
        previewModal: document.getElementById('previewModal'),
        previewContainer: document.getElementById('previewContainer'),
        statTemplates: document.getElementById('statTemplates'),
        editModeIndicator: document.getElementById('editModeIndicator'),
        btnSave: document.getElementById('btnSave')
    },

    renderTemplateList() {
        if (!state.templates.length) {
            this.els.templateList.innerHTML = '<li class="text-center" style="color:var(--text-muted)">No templates found</li>';
            this.els.statTemplates.textContent = 0;
            return;
        }

        this.els.templateList.innerHTML = state.templates.map(t => `
            <li class="template-item ${String(t.id) === String(state.currentTemplateId) ? 'active' : ''}" 
                onclick="window.app.selectTemplate('${t.id}')"> 
                <span class="template-name">${t.name}</span>
                <span class="template-meta">${new Date(t.created_at).toLocaleDateString()}</span>
                <button class="template-delete-btn" 
                        onclick="event.stopPropagation(); window.app.deleteTemplate('${t.id}')" 
                        title="Delete Template">×</button>
            </li>
        `).join('');
        this.els.statTemplates.textContent = state.templates.length;
    },

    renderWorkspace(template, fieldsData) {
        this.els.emptyState.classList.add('hidden');
        this.els.workspace.classList.remove('hidden');

        // Config Form
        this.els.configName.value = template.name;
        
        let fields = fieldsData.fields || {};
        if (typeof fields === 'string') {
            try { fields = JSON.parse(fields); } catch(e) { console.error("Parse Error", e); }
        }
        state.currentTemplateFields = fields;

        // Key Field Dropdown
        const keys = Object.keys(fields);
        if (keys.length === 0) {
            this.els.dynamicForm.innerHTML = '<div style="color: orange; padding: 1rem;">No placeholders found.</div>';
        } else {
            this.els.dynamicForm.innerHTML = keys.map(key => `
                <div class="form-group">
                    <label class="form-label">${key.replace(/_/g, ' ')}</label>
                    <input type="text" name="${key}" class="form-input" placeholder="Enter value...">
                </div>
            `).join('');
        }

        this.els.configKeyField.innerHTML = `
            <option value="">-- Select Key Field --</option>
            ${keys.map(key => `
                <option value="${key}" ${key === fieldsData.key_field ? 'selected' : ''}>${key}</option>
            `).join('')}
        `;
        
        // When switching templates, reset the edit mode
        this.toggleEditMode(false);
    },

    toggleEditMode(isEditing) {
        if(isEditing) {
            this.els.editModeIndicator.classList.remove('hidden');
            this.els.btnSave.textContent = "Overwrite Previous Doc";
            this.els.btnSave.classList.add('btn-primary');
            this.els.btnSave.classList.remove('btn-secondary');
        } else {
            this.els.editModeIndicator.classList.add('hidden');
            this.els.btnSave.textContent = "Save New Document";
            this.els.btnSave.classList.add('btn-secondary');
            this.els.btnSave.classList.remove('btn-primary');
            state.editingDocId = null;
            document.querySelectorAll('#dynamicForm input').forEach(i => i.value = '');
        }
        // Re-render history to update the active highlight
        this.renderHistory(state.documents);
    },

    renderHistory(documents) {
        state.documents = documents; // Update cache
        
        if(!documents || !documents.length) {
            this.els.historyList.innerHTML = '<li class="text-center" style="color:#ccc; padding:1rem;">No documents generated yet</li>';
            return;
        }
        
        this.els.historyList.innerHTML = documents.map(doc => {
            const isSelected = String(doc.id) === String(state.editingDocId);
            const activeClass = isSelected ? 'active' : '';
            
            // Construct Display Name: TemplateName_KeyVal
            let displayName = doc.key_field_value || 'Generated Document';
            const template = state.templates.find(t => String(t.id) === String(doc.template));
            if (template) {
                const keyVal = doc.key_field_value || 'generated';
                // Note: We don't assume extension here, it depends on download format
                displayName = `${template.name}_${keyVal}`;
            }

            return `
            <li class="document-item ${activeClass}" 
                onclick="window.app.editDoc('${doc.id}')"
                style="padding:0.8rem; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center; cursor:pointer;">
                
                <div style="flex: 1; padding-right: 1rem;">
                    <div style="font-weight:600; overflow-wrap: break-word;">
                        ${displayName}
                        ${isSelected ? '<span style="font-size:0.7rem; background:var(--primary); color:white; padding:2px 6px; border-radius:4px; margin-left:8px;">EDITING</span>' : ''}
                    </div>
                    <div style="font-size:0.8rem; color:#888">${new Date(doc.created_at).toLocaleString()}</div>
                </div>
                
                <!-- Action Buttons -->
                <div style="display:flex; gap:0.5rem; flex-shrink: 0; align-items: center;" onclick="event.stopPropagation()">
                    <button class="btn btn-sm btn-secondary" onclick="window.app.editDoc('${doc.id}')" title="Edit">✏️</button>
                    <button class="btn btn-sm btn-secondary" onclick="window.app.previewSavedDoc('${doc.id}')" title="Preview">👁️</button>
                    
                    <!-- NEW: Separate Download Buttons -->
                    <button class="btn btn-sm btn-secondary" onclick="window.app.downloadDoc('${doc.id}', 'docx')" title="Download Word" style="font-size: 0.8rem;">
                        <span style="color:#2b579a; font-weight:bold;">W</span>⬇
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="window.app.downloadDoc('${doc.id}', 'pdf')" title="Download PDF" style="font-size: 0.8rem;">
                        <span style="color:#d32f2f; font-weight:bold;">PDF</span>⬇
                    </button>

                    <button class="btn btn-sm btn-danger" onclick="window.app.deleteDoc('${doc.id}')" title="Delete">🗑️</button>
                </div>
            </li>
        `}).join('');
    },

    openUploadModal() {
        document.getElementById('uploadForm').reset();
        document.getElementById('fileName').textContent = '';
        this.els.uploadModal.classList.add('show');
    },

    openPreviewModal() {
        this.els.previewModal.classList.add('show');
        this.els.previewContainer.innerHTML = '<div class="loading-spinner" style="border-top-color: var(--primary);"></div> Loading Preview...';
    },

    closeModal(modalId) {
        document.getElementById(modalId).classList.remove('show');
    },

    toast(msg, type='success') {
        const el = document.getElementById('toast');
        el.textContent = msg;
        el.className = `toast ${type} show`;
        setTimeout(() => el.classList.remove('show'), 3000);
    }
};

// --- 4. APP LOGIC ---
window.app = {
    async init() {
        await this.loadTemplates();
        this.setupDragDrop();
    },

    setupDragDrop() {
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        dropzone.onclick = () => fileInput.click();
        fileInput.onchange = (e) => {
            if(e.target.files[0]) document.getElementById('fileName').textContent = e.target.files[0].name;
        };
        dropzone.ondragover = (e) => { e.preventDefault(); dropzone.classList.add('dragover'); };
        dropzone.ondragleave = () => dropzone.classList.remove('dragover');
        dropzone.ondrop = (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files[0]) {
                fileInput.files = e.dataTransfer.files;
                document.getElementById('fileName').textContent = e.dataTransfer.files[0].name;
            }
        };
    },

    async loadTemplates() {
        try {
            state.templates = await utils.fetch(`${API_BASE}/templates/`);
            ui.renderTemplateList();
        } catch (e) { console.error(e); }
    },

    async selectTemplate(id) {
        state.currentTemplateId = String(id);
        try {
            const template = state.templates.find(t => String(t.id) === String(id));
            if (!template) return console.error("Template not found");

            const fieldsData = await utils.fetch(`${API_BASE}/templates/${id}/fields/`);
            
            let history = [];
            try {
                history = await utils.fetch(`${API_BASE}/templates/${id}/documents/`);
            } catch(e) { console.warn("History fetch failed", e); }

            ui.renderTemplateList();
            ui.renderWorkspace(template, fieldsData);
            ui.renderHistory(history);

        } catch (e) { console.error("Selection Error:", e); }
    },

    async handleUpload(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        try {
            const newTemplate = await utils.fetch(`${API_BASE}/templates/`, { method: 'POST', body: formData });
            ui.closeModal('uploadModal');
            ui.toast('Template Uploaded');
            await this.loadTemplates();
            if (newTemplate && newTemplate.id) this.selectTemplate(newTemplate.id);
        } catch (e) { /* handled in fetch */ }
    },

    async updateSettings() {
        if(!state.currentTemplateId) return;
        const name = document.getElementById('configName').value;
        const keyField = document.getElementById('configKeyField').value;
        try {
            await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/`, {
                method: 'PATCH',
                body: JSON.stringify({ name: name, key_field: keyField })
            });
            ui.toast('Settings Updated');
            const t = state.templates.find(t => String(t.id) === String(state.currentTemplateId));
            if(t) t.name = name;
            ui.renderTemplateList();
        } catch (e) { /* handled */ }
    },

    getFormData() {
        const inputs = document.getElementById('dynamicForm').querySelectorAll('input');
        const data = {};
        inputs.forEach(input => data[input.name] = input.value);
        return data;
    },

    async editDoc(docId) {
        try {
            const doc = await utils.fetch(`${API_BASE}/documents/${docId}/`);
            state.editingDocId = String(docId);
            
            let values = doc.field_values || {};
            if (typeof values === 'string') {
                try { values = JSON.parse(values); } 
                catch (e) { console.error("JSON Parse Error", e); }
            }

            document.querySelectorAll('#dynamicForm input').forEach(i => i.value = '');
            for (const [key, val] of Object.entries(values)) {
                const input = document.querySelector(`#dynamicForm input[name="${key}"]`);
                if (input) input.value = val;
            }
            
            ui.toggleEditMode(true);
            ui.toast('Editing Document', 'info');
            document.getElementById('dynamicForm').scrollIntoView({ behavior: 'smooth' });

        } catch(e) { console.error(e); }
    },

    clearForm() {
        ui.toggleEditMode(false);
    },

    async deleteCurrentDoc() {
        if (!state.editingDocId) return;
        await this.deleteDoc(state.editingDocId);
    },

    async deleteDoc(docId) {
        if (!confirm("Are you sure you want to delete this document?")) return;
        try {
            await utils.fetch(`${API_BASE}/documents/${docId}/`, { method: 'DELETE' });
            ui.toast('Document Deleted');
            if (String(state.editingDocId) === String(docId)) {
                ui.toggleEditMode(false);
                document.querySelectorAll('#dynamicForm input').forEach(i => i.value = '');
            }
            if(state.currentTemplateId) {
                const history = await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/documents/`);
                ui.renderHistory(history);
            }
        } catch (e) { /* handled */ }
    },

    async generatePreview() {
        if(!state.currentTemplateId) return;
        ui.openPreviewModal();
        const data = {
            template: state.currentTemplateId,
            field_values: this.getFormData()
        };

        try {
            const doc = await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/generate/`, {
                method: 'POST',
                body: JSON.stringify(data)
            });

            if (doc && doc.id) {
                await this.renderPreviewBlob(doc.id);
                const history = await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/documents/`);
                ui.renderHistory(history);
            }
        } catch (e) { 
            ui.closeModal('previewModal');
        }
    },

    async previewSavedDoc(docId) {
        ui.openPreviewModal();
        await this.renderPreviewBlob(docId);
    },

    async renderPreviewBlob(docId) {
        try {
            const response = await utils.fetch(`${API_BASE}/documents/${docId}/preview/`);
            if(response instanceof Response) {
                const blob = await response.blob();
                state.lastPreviewBlob = blob; 
                
                const container = document.getElementById('previewContainer');
                container.innerHTML = '';
                
                if (typeof docx !== 'undefined') {
                    await docx.renderAsync(blob, container, null, {
                        className: "docx-viewer",
                        inWrapper: false,
                        ignoreWidth: false,
                        ignoreHeight: false,
                        breakPages: true,
                        useBase64URL: true
                    });
                } else {
                    container.innerHTML = '<div style="color:red">Preview library missing.</div>';
                }
            }
        } catch (e) {
            document.getElementById('previewContainer').innerHTML = '<div style="color:red">Preview failed.</div>';
        }
    },

    async downloadCurrentPreview() {
        if (!state.lastPreviewBlob) return;
        const url = window.URL.createObjectURL(state.lastPreviewBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `preview_document.docx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        ui.toast('Downloading...');
    },

    async saveToBackend() {
        if(!state.currentTemplateId) return;
        const data = {
            template: state.currentTemplateId,
            field_values: this.getFormData()
        };

        try {
            if (state.editingDocId) {
                await utils.fetch(`${API_BASE}/documents/${state.editingDocId}/`, {
                    method: 'PATCH',
                    body: JSON.stringify(data)
                });
                ui.toast('Document Overwritten');
            } 
            else {
                await utils.fetch(`${API_BASE}/documents/`, {
                    method: 'POST',
                    body: JSON.stringify(data)
                });
                ui.toast('Saved New Document');
            }
            const history = await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/documents/`);
            ui.renderHistory(history);
        } catch (e) { /* handled */ }
    },

    async deleteTemplate(id = null) {
        const targetId = id || state.currentTemplateId;
        if (!targetId) return;

        if(!confirm("Delete this template and all its documents?")) return;
        try {
            await utils.fetch(`${API_BASE}/templates/${targetId}/`, { method: 'DELETE' });
            
            if (String(targetId) === String(state.currentTemplateId)) {
                state.currentTemplateId = null;
                document.getElementById('workspace').classList.add('hidden');
                document.getElementById('emptyState').classList.remove('hidden');
            }
            
            this.loadTemplates();
            ui.toast('Deleted');
        } catch(e) { /* handled */ }
    },

    // --- UPDATED: DOWNLOAD FUNCTION ---
    async downloadDoc(id, format = 'docx') {
        try {
            ui.toast(`Generating ${format.toUpperCase()}...`);
            // Pass format query parameter to backend
            const response = await utils.fetch(`${API_BASE}/documents/${id}/preview/?format=${format}`); 
            
            if(response instanceof Response) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                
                const disposition = response.headers.get('content-disposition');
                let filename = `document_${id}.${format}`;
                if (disposition && disposition.includes('filename=')) {
                    filename = disposition.split('filename=')[1].replace(/"/g, '');
                }
                
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
            }
        } catch (e) { 
            console.error(e); 
            ui.toast("Download Failed (Check server logs)", "error");
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.app.init();
});