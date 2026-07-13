document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('generator-form');
    const projectInput = document.getElementById('project-input');
    const serviceInput = document.getElementById('service-input');
    const tagsWrapper = document.getElementById('tags-wrapper');
    const tagContainer = document.getElementById('services-tag-container');
    const btnGenerate = document.getElementById('btn-generate');
    const btnOpenFolder = document.getElementById('btn-open-folder');
    const generateSpinner = document.getElementById('generate-spinner');
    
    // Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    const sunIcon = themeToggle.querySelector('.sun-icon');
    const moonIcon = themeToggle.querySelector('.moon-icon');

    // Collapsible Advanced Settings
    const advancedToggle = document.getElementById('advanced-toggle');
    const advancedContent = document.getElementById('advanced-content');
    
    // Advanced form fields
    const domainInput = document.getElementById('domain-input');
    const registryInput = document.getElementById('registry-input');
    const imageTagInput = document.getElementById('image-tag-input');
    const portInput = document.getElementById('port-input');
    const namespaceInput = document.getElementById('namespace-input');
    const envKeysInput = document.getElementById('env-keys-input');
    const repMinInput = document.getElementById('rep-min-input');
    const repMaxInput = document.getElementById('rep-max-input');
    const cpuReqInput = document.getElementById('cpu-req-input');
    const memReqInput = document.getElementById('mem-req-input');
    const memLimitInput = document.getElementById('mem-limit-input');
        const autoscaleCheckbox = document.getElementById('autoscale-checkbox');
    const logsPvcCheckbox = document.getElementById('logs-pvc-checkbox');

    // GitLab form fields and modal elements
    const gitlabUrlInput = document.getElementById('gitlab-url-input');
    const gitlabTokenInput = document.getElementById('gitlab-token-input');
    const gitlabProjectInput = document.getElementById('gitlab-project-input');
    const gitlabBranchInput = document.getElementById('gitlab-branch-input');
    const gitlabSubfolderInput = document.getElementById('gitlab-subfolder-input');
    const gitlabCommitMsgInput = document.getElementById('gitlab-commit-msg-input');
    const btnPushGitlab = document.getElementById('btn-push-gitlab');
    
    // Modal controls
    const gitlabModal = document.getElementById('gitlab-modal');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const btnModalCancel = document.getElementById('btn-modal-cancel');
    const btnModalSubmit = document.getElementById('btn-modal-submit');
    const modalPushSpinner = document.getElementById('modal-push-spinner');

    // GitLab push history log elements
    const gitlabHistory = document.getElementById('gitlab-history');
    const gitlabHistoryList = document.getElementById('gitlab-history-list');
    const btnClearHistory = document.getElementById('btn-clear-history');

    const statusAlert = document.getElementById('status-alert');
    const statusMessage = document.getElementById('status-message');
    
    const outdirText = document.getElementById('outdir-text');
    const previewActions = document.getElementById('preview-actions');
    const btnCopy = document.getElementById('btn-copy');
    const copyText = document.getElementById('copy-text');
    
    const previewPlaceholder = document.getElementById('preview-placeholder');
    const previewViewer = document.getElementById('preview-viewer');
    const fileTabsList = document.getElementById('file-tabs-list');
    const codeContent = document.getElementById('code-content');
    const codeLines = document.getElementById('code-lines');
    
    // State
    let services = ['core', 'admin-api'];
    let generatedFiles = [];
    let activeFileIndex = 0;

    // Theme Management
    let currentTheme = localStorage.getItem('theme') || 'dark';
    setTheme(currentTheme);

    themeToggle.addEventListener('click', () => {
        currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(currentTheme);
    });

    function setTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        if (theme === 'dark') {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        } else {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        }
    }

    // Toggle Advanced Configs
    advancedToggle.addEventListener('click', () => {
        const isExpanded = advancedToggle.getAttribute('aria-expanded') === 'true';
        advancedToggle.setAttribute('aria-expanded', !isExpanded);
        advancedContent.classList.toggle('open');
    });

    // Modal Open/Close Logic
    btnPushGitlab.addEventListener('click', () => {
        if (!generatedFiles || generatedFiles.length === 0) {
            showAlert('Chưa có file cấu hình nào được sinh để đẩy.', 'error');
            return;
        }
        gitlabModal.classList.add('open');
    });

    const closeModal = () => {
        gitlabModal.classList.remove('open');
    };

    btnCloseModal.addEventListener('click', closeModal);
    btnModalCancel.addEventListener('click', closeModal);
    
    gitlabModal.addEventListener('click', (e) => {
        if (e.target === gitlabModal) {
            closeModal();
        }
    });

    // Load GitLab config from localStorage
    function loadGitLabConfig() {
        if (localStorage.getItem('gitlab_url')) gitlabUrlInput.value = localStorage.getItem('gitlab_url');
        if (localStorage.getItem('gitlab_token')) gitlabTokenInput.value = localStorage.getItem('gitlab_token');
        if (localStorage.getItem('gitlab_project')) gitlabProjectInput.value = localStorage.getItem('gitlab_project');
        if (localStorage.getItem('gitlab_branch')) gitlabBranchInput.value = localStorage.getItem('gitlab_branch');
        if (localStorage.getItem('gitlab_subfolder')) gitlabSubfolderInput.value = localStorage.getItem('gitlab_subfolder');
        if (localStorage.getItem('gitlab_commit_msg')) gitlabCommitMsgInput.value = localStorage.getItem('gitlab_commit_msg');
    }

    // Save GitLab config to localStorage
    function saveGitLabConfig() {
        localStorage.setItem('gitlab_url', gitlabUrlInput.value);
        localStorage.setItem('gitlab_token', gitlabTokenInput.value);
        localStorage.setItem('gitlab_project', gitlabProjectInput.value);
        localStorage.setItem('gitlab_branch', gitlabBranchInput.value);
        localStorage.setItem('gitlab_subfolder', gitlabSubfolderInput.value);
        localStorage.setItem('gitlab_commit_msg', gitlabCommitMsgInput.value);
    }

    loadGitLabConfig();

    // Auto-parse clone URL on input
    gitlabUrlInput.addEventListener('input', () => {
        const val = gitlabUrlInput.value.trim();
        if (val.startsWith('http://') || val.startsWith('https://')) {
            try {
                const url = new URL(val);
                if (url.pathname && url.pathname !== '/') {
                    const baseDomain = `${url.protocol}//${url.host}`;
                    let projectPath = url.pathname.substring(1);
                    if (projectPath.endsWith('.git')) {
                        projectPath = projectPath.substring(0, projectPath.length - 4);
                    }
                    gitlabUrlInput.value = baseDomain;
                    gitlabProjectInput.value = projectPath;
                }
            } catch (e) {
                // Ignore invalid URL structures while typing
            }
        }
    });

    // GitLab history helper
    function addGitLabHistoryItem(status, detail) {
        const time = new Date().toLocaleTimeString('vi-VN');
        const item = document.createElement('div');
        item.className = 'history-item';
        
        if (status === 'success') {
            const shortCommit = detail.commit_id.substring(0, 8);
            item.innerHTML = `
                <div class="history-item-header">
                    <span class="history-time">${time}</span>
                    <span class="history-badge success">Thành công</span>
                </div>
                <div style="margin-top: 0.2rem; font-size: 0.75rem;">
                    Dự án: <span style="font-weight: 500;">${detail.project}</span> (${detail.branch})
                </div>
                <div style="font-size: 0.75rem;">
                    Commit: <a href="${detail.web_url}" target="_blank" class="history-commit-link" title="Xem commit trên GitLab">${shortCommit}</a>
                </div>
            `;
        } else {
            item.innerHTML = `
                <div class="history-item-header">
                    <span class="history-time">${time}</span>
                    <span class="history-badge error">Thất bại</span>
                </div>
                <div class="history-error-msg">${detail}</div>
            `;
        }
        
        gitlabHistoryList.insertBefore(item, gitlabHistoryList.firstChild);
        gitlabHistory.style.display = 'block';
    }

    btnClearHistory.addEventListener('click', () => {
        gitlabHistoryList.innerHTML = '';
        gitlabHistory.style.display = 'none';
    });

    // Tag Chip System
    tagContainer.addEventListener('click', (e) => {
        if (e.target === tagContainer || e.target === tagsWrapper) {
            serviceInput.focus();
        }
    });
    
    function renderChips() {
        tagsWrapper.innerHTML = '';
        services.forEach((service, index) => {
            const chip = document.createElement('span');
            chip.className = 'tag-chip';
            chip.setAttribute('data-value', service);
            chip.innerHTML = `${service}<button type="button" class="tag-close" data-index="${index}">&times;</button>`;
            tagsWrapper.appendChild(chip);
        });
        
        document.querySelectorAll('.tag-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const idx = parseInt(btn.getAttribute('data-index'));
                removeServiceTag(idx);
            });
        });
    }
    
    function addServiceTag(value) {
        const val = value.trim().toLowerCase().replace(/[^a-z0-9\-]/g, '');
        if (val && !services.includes(val)) {
            services.push(val);
            renderChips();
        }
        serviceInput.value = '';
    }
    
    function removeServiceTag(index) {
        services.splice(index, 1);
        renderChips();
    }
    
    serviceInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            addServiceTag(serviceInput.value);
        } else if (e.key === 'Backspace' && serviceInput.value === '' && services.length > 0) {
            removeServiceTag(services.length - 1);
        }
    });
    
    serviceInput.addEventListener('focusout', () => {
        if (serviceInput.value.trim() !== '') {
            addServiceTag(serviceInput.value);
        }
    });
    
    renderChips();
    
    // YAML Syntax Highlighting
    function highlightYaml(code) {
        let escaped = code
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
            
        // Comments
        escaped = escaped.replace(/(#.*)/g, '<span class="hl-comment">$1</span>');
        
        // Separators
        escaped = escaped.replace(/^(---)$/gm, '<span class="hl-sep">$1</span>');
        
        // Keys
        escaped = escaped.replace(/^([\s-]*)([\w\-\.\/]+)(:)(?=\s|$)/gm, '$1<span class="hl-key">$2</span>$3');
        
        return escaped;
    }
    
    // Alert Notification
    function showAlert(message, type) {
        statusAlert.style.display = 'flex';
        statusAlert.className = `alert alert-${type}`;
        statusMessage.textContent = message;
        
        const iconContainer = statusAlert.querySelector('.alert-icon');
        if (type === 'success') {
            iconContainer.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
        } else {
            iconContainer.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
        }
    }
    
    // File Switcher
    function showFile(index) {
        activeFileIndex = index;
        const file = generatedFiles[index];
        if (!file) return;
        
        document.querySelectorAll('.tab-btn').forEach((btn, idx) => {
            if (idx === index) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        codeContent.innerHTML = highlightYaml(file.content);
        
        const linesCount = file.content.split('\n').length;
        let linesHtml = '';
        for (let i = 1; i <= linesCount; i++) {
            linesHtml += `<span class="code-line-number">${i}</span>`;
        }
        codeLines.innerHTML = linesHtml;
        
        copyText.textContent = 'Sao chép';
        btnCopy.classList.remove('success');
    }
    
    // Form Submit API Integration
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (services.length === 0) {
            showAlert('Vui lòng nhập ít nhất một dịch vụ.', 'error');
            serviceInput.focus();
            return;
        }
        
        btnGenerate.disabled = true;
        generateSpinner.style.display = 'inline-block';
        statusAlert.style.display = 'none';
        
        // Assemble payload with advanced variables
        const payload = {
            project: projectInput.value,
            services: services,
            domain: domainInput.value,
            registry: registryInput.value,
            image_tag: imageTagInput.value,
            port: portInput.value,
            namespace: namespaceInput.value,
            extra_env_keys: envKeysInput.value,
            replicas_min: repMinInput.value,
            replicas_max: repMaxInput.value,
            cpu_request: cpuReqInput.value,
            mem_request: memReqInput.value,
            mem_limit: memLimitInput.value,
            enable_autoscale: autoscaleCheckbox.checked,
            needs_logs_volume: logsPvcCheckbox.checked
        };
        
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                generatedFiles = data.files;
                outdirText.textContent = `Thư mục: ${data.outdir}`;
                showAlert(`Tạo thành công ${generatedFiles.length} file cấu hình!`, 'success');
                
                previewPlaceholder.style.display = 'none';
                previewViewer.style.display = 'flex';
                previewActions.style.display = 'flex';
                
                fileTabsList.innerHTML = '';
                generatedFiles.forEach((file, index) => {
                    const tab = document.createElement('button');
                    tab.type = 'button';
                    tab.className = `tab-btn ${index === 0 ? 'active' : ''}`;
                    tab.textContent = file.name;
                    tab.addEventListener('click', () => showFile(index));
                    fileTabsList.appendChild(tab);
                });
                
                showFile(0);

            } else {
                showAlert(data.error || 'Có lỗi xảy ra khi tạo manifests.', 'error');
            }
        } catch (err) {
            showAlert('Không thể kết nối đến server backend.', 'error');
            console.error(err);
        } finally {
            btnGenerate.disabled = false;
            generateSpinner.style.display = 'none';
        }
    });
    
    // Copy Utility
    btnCopy.addEventListener('click', () => {
        const file = generatedFiles[activeFileIndex];
        if (!file) return;
        
        navigator.clipboard.writeText(file.content).then(() => {
            copyText.textContent = 'Đã chép!';
            btnCopy.classList.add('success');
            setTimeout(() => {
                copyText.textContent = 'Sao chép';
                btnCopy.classList.remove('success');
            }, 2000);
        }).catch(err => {
            console.error('Không thể chép:', err);
        });
    });
    
    // Explorer Integration
    btnOpenFolder.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/open-folder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    project: projectInput.value
                })
            });
            const data = await response.json();
            if (!response.ok) {
                alert('Không thể mở thư mục: ' + data.error);
            }
        } catch (err) {
            alert('Không thể kết nối đến server backend.');
            console.error(err);
        }
    });

    // GitLab Push Integration
    async function pushToGitLab() {
        if (!gitlabTokenInput.value.trim()) {
            alert('Vui lòng nhập GitLab Access Token.');
            gitlabTokenInput.focus();
            return;
        }
        if (!gitlabProjectInput.value.trim()) {
            alert('Vui lòng nhập Project ID hoặc Path.');
            gitlabProjectInput.focus();
            return;
        }
        if (!generatedFiles || generatedFiles.length === 0) {
            alert('Chưa có file cấu hình nào được sinh để đẩy.');
            return;
        }

        saveGitLabConfig();

        btnModalSubmit.disabled = true;
        btnModalCancel.disabled = true;
        btnCloseModal.disabled = true;
        modalPushSpinner.style.display = 'inline-block';
        
        const submitTextNode = btnModalSubmit.querySelector('.btn-text');
        const origSubmitText = submitTextNode.textContent;
        submitTextNode.textContent = 'Đang đẩy...';

        const payload = {
            gitlab_url: gitlabUrlInput.value.trim(),
            token: gitlabTokenInput.value.trim(),
            project: gitlabProjectInput.value.trim(),
            branch: gitlabBranchInput.value.trim() || 'main',
            subfolder: gitlabSubfolderInput.value.trim(),
            commit_message: gitlabCommitMsgInput.value.trim() || `Deploy k8s manifests for ${projectInput.value}`,
            files: generatedFiles
        };

        try {
            const response = await fetch('/api/gitlab-push', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (response.ok) {
                showAlert('Đẩy lên GitLab thành công!', 'success');
                addGitLabHistoryItem('success', {
                    commit_id: data.commit_id,
                    web_url: data.web_url,
                    project: gitlabProjectInput.value.trim(),
                    branch: gitlabBranchInput.value.trim() || 'main'
                });
                closeModal();
            } else {
                alert('Lỗi đẩy GitLab: ' + data.error);
                addGitLabHistoryItem('error', `Lỗi: ${data.error}`);
            }
        } catch (err) {
            alert('Không thể kết nối đến server backend.');
            console.error(err);
            addGitLabHistoryItem('error', 'Lỗi: Không thể kết nối đến server backend.');
        } finally {
            btnModalSubmit.disabled = false;
            btnModalCancel.disabled = false;
            btnCloseModal.disabled = false;
            modalPushSpinner.style.display = 'none';
            submitTextNode.textContent = origSubmitText;
        }
    }

    btnModalSubmit.addEventListener('click', pushToGitLab);
});
