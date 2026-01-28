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
            console.error("Fetch Error:", err);
            ui.toast(err.message, 'error');
            throw err;
        }
    }
};

// --- 2. STATE MANAGEMENT ---
const state = {
    templates: [],
    currentTemplateId: null,
    currentTemplateFields: {},
    editingDocId: null,
    documents: [],
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
            this.els.templateList.innerHTML = '<li style="text-align: center; color: var(--text-muted); padding: 1rem;">No templates found</li>';
            this.els.statTemplates.textContent = 0;
            return;
        }

        this.els.templateList.innerHTML = state.templates.map(t => `
            <li class="list-item flex-between ${String(t.id) === String(state.currentTemplateId) ? 'active' : ''}" 
                onclick="window.app.selectTemplate('${t.id}')">
                <div>
                    <div class="font-bold text-sm">${t.name}</div>
                    <div class="text-xs" style="color: var(--text-muted);">${new Date(t.created_at).toLocaleDateString()}</div>
                </div>
                <button class="btn btn-danger btn-sm"
                        onclick="event.stopPropagation(); window.app.deleteTemplate('${t.id}')"
                        title="Delete Template">
                    <i data-feather="x" style="width:14px; height:14px;"></i>
                </button>
            </li>
        `).join('');
        this.els.statTemplates.textContent = state.templates.length;
        if (typeof feather !== 'undefined') feather.replace();
    },

    renderWorkspace(template, fieldsData) {
        this.els.emptyState.classList.add('hidden');
        this.els.workspace.classList.remove('hidden');

        // Config Form
        this.els.configName.value = template.name;

        let fields = fieldsData.fields || {};
        if (typeof fields === 'string') {
            try { fields = JSON.parse(fields); } catch (e) { console.error("Parse Error", e); }
        }
        state.currentTemplateFields = fields;

        // Key Field Dropdown
        const keys = Object.keys(fields);
        if (keys.length === 0) {
            this.els.dynamicForm.innerHTML = '<div style="color: var(--accent); grid-column: span 2;">No placeholders found in this template.</div>';
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

        this.toggleEditMode(false);
    },

    toggleEditMode(isEditing) {
        if (isEditing) {
            this.els.editModeIndicator.classList.remove('hidden');
            this.els.btnSave.textContent = "Overwrite Cloud Save";
            this.els.btnSave.classList.add('btn-amber');
            this.els.btnSave.classList.remove('btn-secondary');
        } else {
            this.els.editModeIndicator.classList.add('hidden');
            this.els.btnSave.textContent = "Save to Cloud";
            this.els.btnSave.classList.add('btn-secondary');
            this.els.btnSave.classList.remove('btn-amber');
            state.editingDocId = null;
            document.querySelectorAll('#dynamicForm input').forEach(i => i.value = '');
        }
        this.renderHistory(state.documents);
    },

    renderHistory(documents) {
        state.documents = documents;

        if (!documents || !documents.length) {
            this.els.historyList.innerHTML = '<li style="text-align: center; color: var(--text-muted); grid-column: 1 / -1;">No history yet</li>';
            return;
        }

        this.els.historyList.innerHTML = documents.map(doc => {
            const isSelected = String(doc.id) === String(state.editingDocId);
            const activeClass = isSelected ? 'active' : '';

            let displayName = doc.key_field_value || 'Generated Document';
            const template = state.templates.find(t => String(t.id) === String(doc.template));
            if (template) {
                const keyVal = doc.key_field_value || 'generated';
                displayName = `${template.name}_${keyVal}`;
            }

            return `
            <li class="doc-item ${activeClass}" onclick="window.app.editDoc('${doc.id}')">
                <div style="overflow: hidden; padding-right: 1rem;">
                    <div class="font-bold text-sm" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        ${displayName}
                    </div>
                    <div class="text-xs" style="color: var(--text-muted);">
                        ${new Date(doc.created_at).toLocaleString()}
                        ${isSelected ? '<span style="color: var(--primary); font-weight: bold; margin-left: 0.5rem;">EDITING</span>' : ''}
                    </div>
                </div>

                <div class="gap-2" onclick="event.stopPropagation()">
                     <button class="btn btn-secondary btn-sm" onclick="window.app.editDoc('${doc.id}')" title="Edit Data">✏️</button>
                     <button class="btn btn-secondary btn-sm" onclick="window.app.previewSavedDoc('${doc.id}')" title="Preview">👁️</button>
                     <button class="btn btn-secondary btn-sm" style="color: #60a5fa;" onclick="window.app.downloadDoc('${doc.id}', 'docx')" title="DOCX">W</button>
                     <button class="btn btn-secondary btn-sm" style="color: #f87171;" onclick="window.app.downloadDoc('${doc.id}', 'pdf')" title="PDF">PDF</button>
                     <button class="btn btn-danger btn-sm" onclick="window.app.deleteDoc('${doc.id}')">🗑️</button>
                </div>
            </li>
        `}).join('');
    },

    openUploadModal() {
        document.getElementById('uploadForm').reset();
        document.getElementById('fileName').textContent = '';
        this.els.uploadModal.classList.remove('hidden');
    },

    openPreviewModal() {
        this.els.previewModal.classList.remove('hidden');
        this.els.previewContainer.innerHTML = '<div style="display:flex; justify-content:center; align-items:center; height:100%; color: #374151;">Loading Preview...</div>';
    },

    closeModal(modalId) {
        document.getElementById(modalId).classList.add('hidden');
    },

    // --- FIX: Fixed Toast Function (Removed the deleting logic) ---
    toast(msg, type = 'success') {
        const el = document.getElementById('toast');
        if (!el) return console.error("Toast element missing");

        el.textContent = msg;
        el.className = `toast show ${type}`;

        // Hide after 3 seconds, but DO NOT remove from DOM
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
        if (!dropzone || !fileInput) return;

        dropzone.onclick = () => fileInput.click();
        fileInput.onchange = (e) => {
            if (e.target.files[0]) document.getElementById('fileName').textContent = e.target.files[0].name;
        };
        dropzone.ondragover = (e) => { e.preventDefault(); dropzone.classList.add('drag-active'); };
        dropzone.ondragleave = () => dropzone.classList.remove('drag-active');
        dropzone.ondrop = (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-active');
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
            } catch (e) { console.warn("History fetch failed", e); }

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
            ui.toast('Template Uploaded', 'success');
            await this.loadTemplates();
            if (newTemplate && newTemplate.id) this.selectTemplate(newTemplate.id);
        } catch (e) { /* handled in fetch */ }
    },

    async updateSettings() {
        if (!state.currentTemplateId) return;
        const name = document.getElementById('configName').value;
        const keyField = document.getElementById('configKeyField').value;
        try {
            await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/`, {
                method: 'PATCH',
                body: JSON.stringify({ name: name, key_field: keyField })
            });
            ui.toast('Settings Updated', 'info');
            const t = state.templates.find(t => String(t.id) === String(state.currentTemplateId));
            if (t) t.name = name;
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

        } catch (e) { console.error(e); }
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
            ui.toast('Document Deleted', 'error');
            if (String(state.editingDocId) === String(docId)) {
                ui.toggleEditMode(false);
                document.querySelectorAll('#dynamicForm input').forEach(i => i.value = '');
            }
            if (state.currentTemplateId) {
                const history = await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/documents/`);
                ui.renderHistory(history);
            }
        } catch (e) { /* handled */ }
    },

    async generatePreview() {
        if (!state.currentTemplateId) return;
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
            if (response instanceof Response) {
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
        if (!state.lastPreviewBlob) {
            return ui.toast('No preview available to download', 'error');
        }
        const url = window.URL.createObjectURL(state.lastPreviewBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `preview_document.docx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        ui.toast('Downloading...', 'success');
    },

    async saveToBackend() {
        if (!state.currentTemplateId) return;
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
                ui.toast('Document Overwritten', 'success');
            }
            else {
                await utils.fetch(`${API_BASE}/documents/`, {
                    method: 'POST',
                    body: JSON.stringify(data)
                });
                ui.toast('Saved New Document', 'success');
            }
            const history = await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/documents/`);
            ui.renderHistory(history);
        } catch (e) { /* handled */ }
    },

    async deleteTemplate(id = null) {
        const targetId = id || state.currentTemplateId;
        if (!targetId) return;

        if (!confirm("Delete this template and all its documents?")) return;
        try {
            await utils.fetch(`${API_BASE}/templates/${targetId}/`, { method: 'DELETE' });

            if (String(targetId) === String(state.currentTemplateId)) {
                state.currentTemplateId = null;
                document.getElementById('workspace').classList.add('hidden');
                document.getElementById('emptyState').classList.remove('hidden');
            }

            this.loadTemplates();
            ui.toast('Deleted', 'error');
        } catch (e) { /* handled */ }
    },

    // --- FIX: Ensure we use 'window.URL' safely ---
    async downloadDoc(id, format = 'docx') {
        try {
            ui.toast(`Generating ${format.toUpperCase()}...`, 'info');
            const response = await utils.fetch(`${API_BASE}/documents/${id}/preview/?file_format=${format}`);

            if (response instanceof Response) {
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
            ui.toast("Download Failed", "error");
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.app.init();
});