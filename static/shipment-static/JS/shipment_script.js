// --- 1. CONFIG & UTILS ---
const API_BASE = '/api/shipment_forms'; 

const utils = {
    // CSRF Token logic is CRITICAL for Django POST requests
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
        // Add CSRF token to non-GET requests
        if (options.method && options.method !== 'GET') {
            headers['X-CSRFToken'] = this.getCookie('csrftoken');
        }
        // Add JSON content type unless it's FormData (file upload)
        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }

        try {
            const response = await fetch(url, { ...options, headers });
            if (response.status === 204) return null; // No content
            if (!response.ok) {
                const err = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(err.detail || JSON.stringify(err));
            }
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return await response.json();
            }
            return response; // Return raw response for blobs
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
    currentTemplateFields: {}
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
        statTemplates: document.getElementById('statTemplates')
    },

    renderTemplateList() {
        if (!state.templates.length) {
            this.els.templateList.innerHTML = '<li class="text-center" style="color:var(--text-muted)">No templates found</li>';
            this.els.statTemplates.textContent = 0;
            return;
        }

        this.els.templateList.innerHTML = state.templates.map(t => `
            <li class="template-item ${String(t.id) === String(state.currentTemplateId) ? 'active' : ''}" 
                onclick="app.selectTemplate('${t.id}')"> 
                <span class="template-name">${t.name}</span>
                <span class="template-meta">${new Date(t.created_at).toLocaleDateString()}</span>
            </li>
        `).join('');
        this.els.statTemplates.textContent = state.templates.length;
    },

    renderWorkspace(template, fieldsData) {
        console.log("Rendering Workspace with:", fieldsData); // DEBUG

        // 1. Show Workspace
        this.els.emptyState.classList.add('hidden');
        this.els.workspace.classList.remove('hidden');

        // 2. Setup Config Form
        this.els.configName.value = template.name;
        
        // 3. Handle Fields (Parsing safety)
        let fields = fieldsData.fields || {};
        if (typeof fields === 'string') {
            try { fields = JSON.parse(fields); } catch(e) { console.error("Could not parse fields JSON", e); }
        }
        state.currentTemplateFields = fields;

        // 4. Populate Key Field Dropdown
        const keys = Object.keys(fields);
        
        if (keys.length === 0) {
            this.els.dynamicForm.innerHTML = '<div style="color: orange; padding: 1rem;">No placeholders found in this document (e.g. {{Name}}).</div>';
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
                <option value="${key}" ${key === fieldsData.key_field ? 'selected' : ''}>
                    ${key}
                </option>
            `).join('')}
        `;
    },

    renderHistory(documents) {
        if(!documents || !documents.length) {
            this.els.historyList.innerHTML = '<li class="text-center" style="color:#ccc; padding:1rem;">No documents generated yet</li>';
            return;
        }
        this.els.historyList.innerHTML = documents.map(doc => `
            <li style="padding:0.8rem; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-weight:600;">${doc.key_field_value || 'Generated Document'}</div>
                    <div style="font-size:0.8rem; color:#888">${new Date(doc.created_at).toLocaleString()}</div>
                </div>
                <button class="btn btn-sm btn-secondary" onclick="app.downloadDoc('${doc.id}')">⬇ Download</button>
            </li>
        `).join('');
    },

    openUploadModal() {
        document.getElementById('uploadForm').reset();
        document.getElementById('fileName').textContent = '';
        this.els.uploadModal.classList.add('show');
    },

    closeModal() {
        this.els.uploadModal.classList.remove('show');
    },

    toast(msg, type='success') {
        const el = document.getElementById('toast');
        el.textContent = msg;
        el.className = `toast ${type} show`;
        setTimeout(() => el.classList.remove('show'), 3000);
    }
};

// --- 4. APP LOGIC ---
const app = {
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
        // Force ID to string for comparison safety
        state.currentTemplateId = String(id);
        
        try {
            // 1. Find template in local state
            const template = state.templates.find(t => String(t.id) === String(id));
            if (!template) return console.error("Template not found in local state");

            // 2. Fetch Fields
            console.log(`Fetching fields for template ${id}...`);
            const fieldsData = await utils.fetch(`${API_BASE}/templates/${id}/fields/`);
            
            // 3. Fetch History (Check if endpoint exists, handle 404 gracefully)
            let history = [];
            try {
                history = await utils.fetch(`${API_BASE}/templates/${id}/documents/`);
            } catch(e) {
                console.warn("Could not fetch history (endpoint might be missing)", e);
            }

            // 4. Render
            ui.renderTemplateList(); // Updates active class
            ui.renderWorkspace(template, fieldsData);
            ui.renderHistory(history);

        } catch (e) { console.error("Selection Error:", e); }
    },

    async handleUpload(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        try {
            const newTemplate = await utils.fetch(`${API_BASE}/templates/`, {
                method: 'POST',
                body: formData
            });
            ui.closeModal();
            ui.toast('Template Uploaded');
            await this.loadTemplates();
            // Select the new template
            if (newTemplate && newTemplate.id) {
                this.selectTemplate(newTemplate.id);
            }
        } catch (e) { /* handled in fetch */ }
    },

    async updateSettings() {
        const name = document.getElementById('configName').value;
        const keyField = document.getElementById('configKeyField').value;
        if(!state.currentTemplateId) return;

        try {
            await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/`, {
                method: 'PATCH',
                body: JSON.stringify({ name: name, key_field: keyField })
            });
            ui.toast('Settings Updated');
            // Update local state name without full reload
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

    async generateDocument() {
        if(!state.currentTemplateId) return;
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
                this.downloadDoc(doc.id);
                // Reload history to show the new document
                const history = await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/documents/`);
                ui.renderHistory(history);
                ui.toast('Generated Successfully');
            }
        } catch (e) { /* handled */ }
    },

    async saveToBackend() {
        if(!state.currentTemplateId) return;
        const data = {
            template: state.currentTemplateId,
            field_values: this.getFormData()
        };
            try {
            await utils.fetch(`${API_BASE}/documents/`, {
                method: 'POST',
                body: JSON.stringify(data)
            });
            const history = await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/documents/`);
            ui.renderHistory(history);
            ui.toast('Saved to Backend');
        } catch (e) { /* handled */ }
    },

    async deleteTemplate() {
        if(!confirm("Delete this template and all its documents?")) return;
        try {
            await utils.fetch(`${API_BASE}/templates/${state.currentTemplateId}/`, { method: 'DELETE' });
            state.currentTemplateId = null;
            document.getElementById('workspace').classList.add('hidden');
            document.getElementById('emptyState').classList.remove('hidden');
            this.loadTemplates();
            ui.toast('Deleted');
        } catch(e) { /* handled */ }
    },

    async downloadDoc(id) {
        try {
            const response = await utils.fetch(`${API_BASE}/documents/${id}/preview/`); 
            if(response instanceof Response) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                const disposition = response.headers.get('content-disposition');
                let filename = `document_${id}.docx`;
                if (disposition && disposition.includes('filename=')) {
                    filename = disposition.split('filename=')[1].replace(/"/g, '');
                }
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
            }
        } catch (e) { console.error(e); }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    app.init();
});