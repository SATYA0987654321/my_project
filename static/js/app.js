// Global App State
let state = {
    user: null,
    activeTab: 'dashboard',
    selectedTemplate: 'Classic ATS',
    selectedFile: null,
    jobsList: [],
    projectsCount: 0
};

// ==========================================
//            1. INITIALIZATION & ROUTING     
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Theme (Light/Dark Mode)
    initTheme();

    // Set current date in header
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('current-date').innerText = new Date().toLocaleDateString('en-US', options);

    // Setup drag and drop for analyzer
    setupDragAndDrop();

    // Check if user has active session
    checkSession();
});

function checkSession() {
    fetch('/api/auth/me')
        .then(response => {
            if (response.ok) return response.json();
            throw new Error('Not authenticated');
        })
        .then(data => {
            state.user = data.user;
            showDashboard();
        })
        .catch(() => {
            showLandingPage();
        });
}

function showLandingPage() {
    document.getElementById('landing-page').classList.remove('hidden');
    document.getElementById('auth-page').classList.add('hidden');
    document.getElementById('app-layout').classList.add('hidden');
}

function showAuthPage(mode = 'login') {
    document.getElementById('landing-page').classList.add('hidden');
    document.getElementById('auth-page').classList.remove('hidden');
    document.getElementById('app-layout').classList.add('hidden');
    toggleAuthMode(mode);
}

function toggleAuthMode(mode) {
    const title = document.getElementById('auth-title');
    const subtitle = document.getElementById('auth-subtitle');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    if (loginForm) loginForm.classList.add('hidden');
    if (signupForm) signupForm.classList.add('hidden');

    if (mode === 'signup') {
        title.innerText = 'Create Account';
        subtitle.innerText = 'Sign up to start optimizing your resume';
        if (signupForm) signupForm.classList.remove('hidden');
    } else {
        title.innerText = 'Welcome Back';
        subtitle.innerText = 'Sign in to access your dashboard';
        if (loginForm) loginForm.classList.remove('hidden');
    }
}

function showDashboard() {
    document.getElementById('landing-page').classList.add('hidden');
    document.getElementById('auth-page').classList.add('hidden');
    document.getElementById('app-layout').classList.remove('hidden');
    
    // Set user display names
    document.getElementById('user-display-name').innerText = state.user.username;
    document.getElementById('welcome-username').innerText = state.user.username;

    // Load initial dashboard data
    loadDashboardData();
    // Load job roles
    loadJobRoles();
    // Load resume data
    loadResumeData();
}

function switchTab(tabId, event) {
    if (event) event.preventDefault();
    
    state.activeTab = tabId;

    // Update sidebar active state
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.classList.remove('active');
    });
    
    if (event) {
        event.currentTarget.classList.add('active');
    } else {
        // Find by tabId
        const activeLink = Array.from(document.querySelectorAll('.sidebar-item')).find(item => 
            item.getAttribute('onclick').includes(tabId)
        );
        if (activeLink) activeLink.classList.add('active');
    }

    // Update tab title
    const titles = {
        'dashboard': 'Dashboard',
        'generator': 'Professional ATS Resume Generator',
        'analyzer': 'Skill Gap Analyzer'
    };
    document.getElementById('tab-title').innerText = titles[tabId];

    // Show/Hide panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.add('hidden');
    });
    document.getElementById(`tab-${tabId}`).classList.remove('hidden');

    if (tabId === 'dashboard') {
        loadDashboardData();
    }
}

// ==========================================
//            2. AUTHENTICATION HANDLERS      
// ==========================================

function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    })
    .then(async response => {
        const data = await response.json();
        if (response.ok) {
            state.user = { username: data.username };
            showToast('Signed in successfully!', 'success');
            showDashboard();
        } else {
            throw new Error(data.detail || 'Login failed');
        }
    })
    .catch(err => {
        showToast(err.message, 'error');
    });
}

function handleSignup(e) {
    e.preventDefault();
    const username = document.getElementById('signup-username').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirm = document.getElementById('signup-confirm').value;

    if (password !== confirm) {
        showToast('Passwords do not match.', 'error');
        return;
    }

    fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    })
    .then(async response => {
        const data = await response.json();
        if (response.ok) {
            showToast('Account registered successfully! Please sign in.', 'success');
            // Auto-populate into login form for instant sign in
            document.getElementById('login-username').value = username;
            document.getElementById('login-password').value = password;
            toggleAuthMode('login');
        } else {
            throw new Error(data.detail || 'Registration failed');
        }
    })
    .catch(err => {
        showToast(err.message, 'error');
    });
}

function handleLogout() {
    fetch('/api/auth/logout', { method: 'POST' })
        .then(() => {
            state.user = null;
            showToast('Logged out successfully.', 'success');
            showLandingPage();
        })
        .catch(err => {
            showToast('Logout failed.', 'error');
        });
}

// ==========================================
//            3. DASHBOARD DATA LOADER        
// ==========================================

function loadDashboardData() {
    // Load history from API
    fetch('/api/history')
        .then(response => {
            if (response.ok) return response.json();
            throw new Error('Failed to load history');
        })
        .then(history => {
            const tableBody = document.getElementById('history-table-body');
            
            // Calculate Stats
            const totalAnalyses = history.length;
            let avgScore = 0;
            let topRole = "Data Science";
            if (totalAnalyses > 0) {
                const sum = history.reduce((acc, curr) => acc + curr.match_score, 0);
                avgScore = Math.round(sum / totalAnalyses);
                topRole = history[0].job_role || "Data Science";
            }
            
            document.getElementById('stat-total-analyses').innerText = totalAnalyses;
            document.getElementById('stat-avg-score').innerText = `${avgScore}%`;
            const topRoleElem = document.getElementById('stat-top-role');
            if (topRoleElem) topRoleElem.innerText = topRole;

            if (totalAnalyses === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center text-muted">No searches analyzed yet. Navigate to the Skill Analyzer to run your first check!</td>
                    </tr>
                `;
                return;
            }

            tableBody.innerHTML = history.map(item => {
                const matchedBadges = item.matched_skills.slice(0, 3).map(s => `<span class="badge badge-matched">${s}</span>`).join('');
                const missingBadges = item.missing_skills.slice(0, 3).map(s => `<span class="badge badge-missing">${s}</span>`).join('');
                
                const extraMatchedCount = item.matched_skills.length > 3 ? ` +${item.matched_skills.length - 3}` : '';
                const extraMissingCount = item.missing_skills.length > 3 ? ` +${item.missing_skills.length - 3}` : '';

                const matchedArg = encodeURIComponent(JSON.stringify(item.matched_skills));
                const missingArg = encodeURIComponent(JSON.stringify(item.missing_skills));
                const roleArg = encodeURIComponent(item.job_role);

                return `
                    <tr>
                        <td><strong>${item.job_role}</strong></td>
                        <td><span class="text-primary font-weight-bold" style="font-size: 1.1rem; font-weight: 700;">${item.match_score}%</span></td>
                        <td>${matchedBadges}${extraMatchedCount ? `<span class="text-muted" style="font-size: 0.8rem;">${extraMatchedCount}</span>` : ''}</td>
                        <td>${missingBadges}${extraMissingCount ? `<span class="text-muted" style="font-size: 0.8rem;">${extraMissingCount}</span>` : ''}</td>
                        <td class="text-muted">${item.analyzed_at}</td>
                        <td style="text-align: right;">
                            <button type="button" class="btn btn-outline btn-xs" onclick="downloadHistoricalReport('${roleArg}', ${item.match_score}, '${matchedArg}', '${missingArg}')" style="font-size: 0.75rem; padding: 4px 10px; border-radius: 6px; font-weight: 600;">
                                <i class="fa-solid fa-download"></i> PDF
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        })
        .catch(err => {
            console.error(err);
        });
}

// ==========================================
//            4. RESUME GENERATOR HANDLERS    
// ==========================================

function loadResumeData() {
    fetch('/api/resume/load')
        .then(response => {
            if (response.ok) return response.json();
            throw new Error('Failed to load resume draft');
        })
        .then(data => {
            // Update Dashboard Stat
            const hasResume = data.name && data.email;
            document.getElementById('stat-resume-status').innerText = hasResume ? 'Saved' : 'Not Created';
            if (hasResume) {
                document.getElementById('stat-resume-status').classList.remove('text-muted');
                document.getElementById('stat-resume-status').classList.add('text-success');
            }

            // Fill Form
            document.getElementById('res-name').value = data.name || '';
            document.getElementById('res-email').value = data.email || '';
            document.getElementById('res-phone').value = data.phone || '';
            document.getElementById('res-linkedin').value = data.linkedin || '';
            document.getElementById('res-location').value = data.location || '';
            document.getElementById('res-objective').value = data.objective || '';
            document.getElementById('res-education').value = data.education || '';
            document.getElementById('res-languages').value = data.languages || '';
            document.getElementById('res-database').value = data.database || '';
            document.getElementById('res-tools').value = data.tools || '';
            document.getElementById('res-concepts').value = data.concepts || '';
            document.getElementById('res-achievements').value = data.achievements || '';
            document.getElementById('res-activities').value = data.activities || '';
            document.getElementById('res-extra-curricular').value = data.extra_curricular || '';

            // Render projects
            const container = document.getElementById('projects-container');
            container.innerHTML = '';
            state.projectsCount = 0;
            if (data.projects && data.projects.length > 0) {
                data.projects.forEach(proj => {
                    addProjectField(proj.title, proj.desc);
                });
            } else {
                // Add two default blank project fields
                addProjectField();
                addProjectField();
            }
        })
        .catch(err => {
            console.error(err);
        });
}

window.selectTemplate = function(templateName) {
    state.selectedTemplate = templateName;
    document.getElementById('selected-template-name').innerText = templateName;
    
    // Switch to form input step
    document.getElementById('generator-step-template').classList.add('hidden');
    document.getElementById('generator-step-form').classList.remove('hidden');
};

window.changeTemplate = function() {
    document.getElementById('generator-step-template').classList.remove('hidden');
    document.getElementById('generator-step-form').classList.add('hidden');
};

function reindexProjectFields() {
    const container = document.getElementById('projects-container');
    if (!container) return;
    const cards = container.querySelectorAll('.project-card');
    cards.forEach((card, idx) => {
        const header = card.querySelector('h4');
        if (header) header.innerText = `Project #${idx + 1}`;
    });
}

window.addProjectField = function(title = '', desc = '') {
    const container = document.getElementById('projects-container');
    if (!container) return;
    
    const projectCard = document.createElement('div');
    projectCard.className = 'project-card';
    projectCard.innerHTML = `
        <div class="project-card-header">
            <h4>Project #${container.children.length + 1}</h4>
            <button type="button" class="remove-proj-btn"><i class="fa-solid fa-trash-can"></i> Remove</button>
        </div>
        <div class="grid-2">
            <div class="form-group grid-colspan-2">
                <label>Project Title</label>
                <input type="text" class="proj-title-input" value="${title}" placeholder="Project Title" required>
            </div>
            <div class="form-group grid-colspan-2">
                <label>Project Description (Separate bullet points with new lines)</label>
                <textarea class="proj-desc-input" rows="3" placeholder="Key responsibilities, technologies, and measurable achievements..." required>${desc}</textarea>
            </div>
        </div>
    `;
    
    const removeBtn = projectCard.querySelector('.remove-proj-btn');
    if (removeBtn) {
        removeBtn.onclick = function() {
            projectCard.remove();
            reindexProjectFields();
        };
    }
    
    container.appendChild(projectCard);
    reindexProjectFields();
};

window.removeProjectField = function(btn) {
    const card = btn.closest('.project-card');
    if (card) {
        card.remove();
        reindexProjectFields();
    }
};

function getResumePayload() {
    const projects = [];
    document.querySelectorAll('.project-card').forEach(card => {
        const title = card.querySelector('.proj-title-input').value;
        const desc = card.querySelector('.proj-desc-input').value;
        if (title || desc) {
            projects.push({ title, desc });
        }
    });

    return {
        name: document.getElementById('res-name').value,
        email: document.getElementById('res-email').value,
        phone: document.getElementById('res-phone').value,
        linkedin: document.getElementById('res-linkedin').value,
        location: document.getElementById('res-location').value,
        objective: document.getElementById('res-objective').value,
        education: document.getElementById('res-education').value,
        languages: document.getElementById('res-languages').value,
        database: document.getElementById('res-database').value,
        tools: document.getElementById('res-tools').value,
        concepts: document.getElementById('res-concepts').value,
        achievements: document.getElementById('res-achievements').value,
        activities: document.getElementById('res-activities').value,
        extra_curricular: document.getElementById('res-extra-curricular').value,
        projects: projects
    };
}

window.saveResumeDraft = function() {
    const payload = getResumePayload();

    fetch('/api/resume/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(async response => {
        if (response.ok) {
            showToast('Resume draft saved successfully!', 'success');
            loadResumeData(); // reload status
        } else {
            const data = await response.json();
            throw new Error(data.detail || 'Save failed');
        }
    })
    .catch(err => {
        showToast(err.message, 'error');
    });
};

function handleGenerateResume(e) {
    e.preventDefault();
    const payload = getResumePayload();
    const btn = document.getElementById('btn-generate-resume');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating Resume...';
    }

    fetch(`/api/resume/generate?template=${encodeURIComponent(state.selectedTemplate)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (response.ok) return response.blob();
        throw new Error('Failed to generate PDF. Please check required fields.');
    })
    .then(blob => {
        if (state.compiledResumeUrl) {
            window.URL.revokeObjectURL(state.compiledResumeUrl);
        }
        state.compiledResumeBlob = blob;
        state.compiledResumeUrl = window.URL.createObjectURL(blob);
        
        const optPanel = document.getElementById('resume-generated-options');
        if (optPanel) {
            optPanel.classList.remove('hidden');
            optPanel.scrollIntoView({ behavior: 'smooth' });
        }
        showToast('ATS Resume compiled! Choose an option below to Download or Preview.', 'success');
    })
    .catch(err => {
        showToast(err.message, 'error');
    })
    .finally(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Generate ATS Resume';
        }
    });
}

window.downloadCompiledResume = function() {
    if (!state.compiledResumeBlob) {
        showToast('Please generate a resume first.', 'warning');
        return;
    }
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = state.compiledResumeUrl || window.URL.createObjectURL(state.compiledResumeBlob);
    const candidateName = (document.getElementById('res-name').value.trim() || 'Candidate').replace(/[\s\/]+/g, '_');
    a.download = `${candidateName}_ATS_Resume.pdf`;
    document.body.appendChild(a);
    a.click();
    showToast('Resume PDF downloaded successfully!', 'success');
};

window.previewCompiledResume = function() {
    if (!state.compiledResumeBlob) {
        showToast('Please generate a resume first.', 'warning');
        return;
    }
    const pdfUrl = state.compiledResumeUrl || window.URL.createObjectURL(state.compiledResumeBlob);
    window.open(pdfUrl, '_blank');
};

// ==========================================
//            5. SKILL ANALYZER HANDLERS      
// ==========================================

function loadJobRoles() {
    fetch('/api/jobs')
        .then(response => {
            if (response.ok) return response.json();
            throw new Error('Failed to load job roles');
        })
        .then(jobs => {
            state.jobsList = jobs;
            const select = document.getElementById('analyzer-template-select');
            if (!select) return;
            select.innerHTML = '<option value="">-- Load Sample JD --</option>';
            
            // Group jobs by category for a polished UI
            const categories = {};
            jobs.forEach(job => {
                const cat = job.category || "General Tech";
                if (!categories[cat]) categories[cat] = [];
                categories[cat].push(job);
            });

            for (const [catName, roleList] of Object.entries(categories)) {
                const group = document.createElement('optgroup');
                group.label = catName;
                roleList.forEach(job => {
                    const opt = document.createElement('option');
                    opt.value = job.role;
                    opt.innerText = `${job.role}`;
                    group.appendChild(opt);
                });
                select.appendChild(group);
            }
        })
        .catch(err => {
            console.error(err);
        });
}

window.applyJdTemplate = function(roleName) {
    if (!roleName) return;
    const role = (state.jobsList || []).find(r => r.role === roleName);
    const textarea = document.getElementById('analyzer-jd');
    if (role && textarea) {
        const jdText = `Position: ${role.role} (${role.experience_level || 'All Levels'})\nCategory: ${role.category || 'Technology'}\n\nKey Requirements & Core Skills:\n- Must-Have Skills: ${role.must_have_skills.join(', ')}\n- Desired / Secondary Tools: ${role.good_to_have_skills.join(', ')}\n\nJob Description & Responsibilities:\n${role.description}`;
        textarea.value = jdText;
        showToast(`Loaded template for ${role.role}!`, 'info');
    }
};

// Drag and drop setup
function setupDragAndDrop() {
    const dropzone = document.getElementById('dropzone');
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            setSelectedFile(files[0]);
        }
    }, false);
}

window.triggerFileInput = function() {
    document.getElementById('analyzer-file').click();
};

window.handleFileSelect = function(e) {
    if (e.target.files.length > 0) {
        setSelectedFile(e.target.files[0]);
    }
};

function setSelectedFile(file) {
    const fileExt = file.name.split('.').pop().toLowerCase();
    if (fileExt !== 'pdf' && fileExt !== 'txt') {
        showToast('Unsupported file type! Only .pdf and .txt files are allowed.', 'error');
        return;
    }

    state.selectedFile = file;
    document.getElementById('selected-file-name').innerText = file.name;
    document.getElementById('selected-file-info').classList.remove('hidden');
    document.getElementById('dropzone').classList.add('hidden');
}

window.removeSelectedFile = function() {
    state.selectedFile = null;
    document.getElementById('analyzer-file').value = '';
    document.getElementById('selected-file-info').classList.add('hidden');
    document.getElementById('dropzone').classList.remove('hidden');
};

function handleRunAnalysis(e) {
    e.preventDefault();
    if (!state.selectedFile) {
        showToast('Please upload a resume file (.pdf or .txt) first.', 'warning');
        return;
    }
    const jdText = document.getElementById('analyzer-jd').value.trim();
    if (!jdText) {
        showToast('Please paste a Job Description (JD) or choose a sample template.', 'warning');
        return;
    }

    // Toggle Loading State
    const btn = document.getElementById('btn-run-analysis');
    const btnText = document.getElementById('analysis-btn-text');
    const spinner = document.getElementById('analysis-spinner');
    
    btn.disabled = true;
    btnText.classList.add('hidden');
    spinner.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', state.selectedFile);
    formData.append('job_description', jdText);

    fetch('/api/analyze', {
        method: 'POST',
        body: formData
    })
    .then(async response => {
        const data = await response.json();
        if (response.ok) {
            state.latestAnalysis = data;
            renderAnalysisResults(data);
            showToast('NLP Skill Gap Analysis Complete!', 'success');
            loadDashboardData(); // Refresh history
        } else {
            throw new Error(data.detail || 'Analysis failed');
        }
    })
    .catch(err => {
        showToast(err.message, 'error');
    })
    .finally(() => {
        btn.disabled = false;
        btnText.classList.remove('hidden');
        spinner.classList.add('hidden');
    });
}

function renderAnalysisResults(data) {
    document.getElementById('results-placeholder').classList.add('hidden');
    const content = document.getElementById('results-content');
    content.classList.remove('hidden');

    // Show Report Download Button
    const dlBtn = document.getElementById('btn-download-report');
    if (dlBtn) dlBtn.classList.remove('hidden');

    // 1. Composite Readiness Score Ring & Performance Tier
    const score = data.composite_score || data.match_score || 0;
    document.getElementById('score-val').innerText = `${score}%`;
    const circle = document.getElementById('score-ring-fill');
    
    // Circumference of radius 50 is 2 * PI * 50 = 314
    const offset = 314 - (314 * Math.min(100, score)) / 100;
    circle.style.strokeDashoffset = offset;
    
    if (score >= 80) {
        circle.style.stroke = "#10b981"; // Emerald
    } else if (score >= 50) {
        circle.style.stroke = "#7c3aed"; // Purple
    } else if (score > 0) {
        circle.style.stroke = "#f59e0b"; // Amber
    } else {
        circle.style.stroke = "#ef4444"; // Red
    }

    // Tier badge
    const tierBadge = document.getElementById('tier-badge');
    if (tierBadge) {
        tierBadge.innerText = data.match_tier || "Assessment Completed";
        if (data.tier_color === "success") {
            tierBadge.style.background = "rgba(16, 185, 129, 0.1)";
            tierBadge.style.color = "#10b981";
            tierBadge.style.borderColor = "rgba(16, 185, 129, 0.2)";
        } else if (data.tier_color === "warning") {
            tierBadge.style.background = "rgba(124, 58, 237, 0.1)";
            tierBadge.style.color = "#7c3aed";
            tierBadge.style.borderColor = "rgba(124, 58, 237, 0.2)";
        } else {
            tierBadge.style.background = "rgba(239, 68, 68, 0.1)";
            tierBadge.style.color = "#ef4444";
            tierBadge.style.borderColor = "rgba(239, 68, 68, 0.2)";
        }
    }

    const roleDisplay = document.getElementById('target-role-display');
    if (roleDisplay) {
        roleDisplay.innerText = `${data.job_role} • ${data.experience_level || 'All Levels'}`;
    }

    // 2. Sub-Metric Cards
    const subs = data.sub_scores || {};
    document.getElementById('sub-metric-must-have').innerText = `${subs.must_have_score || 0}%`;
    document.getElementById('sub-metric-tfidf').innerText = `${subs.semantic_similarity || 0}%`;
    document.getElementById('sub-metric-format').innerText = `${subs.ats_format_score || 0}%`;
    document.getElementById('sub-metric-impact').innerText = `${subs.impact_score || 0}%`;

    // 3. Category Breakdown Bars
    const catContainer = document.getElementById('category-bars-container');
    if (catContainer && data.category_breakdown) {
        if (data.category_breakdown.length === 0) {
            catContainer.innerHTML = '<p class="text-muted" style="font-size:0.85rem;">No technical categories mapped for this role.</p>';
        } else {
            catContainer.innerHTML = data.category_breakdown.map(cat => `
                <div class="category-bar-item" style="background: #f8fafc; padding: 10px 14px; border-radius: 10px; border: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.82rem; font-weight: 700; color: #334155; margin-bottom: 6px;">
                        <span>${cat.category}</span>
                        <span>${cat.matched_count}/${cat.required_count} Skills (${cat.score}%)</span>
                    </div>
                    <div style="height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden;">
                        <div style="width: ${cat.score}%; height: 100%; background: ${cat.score >= 70 ? '#10b981' : (cat.score >= 40 ? '#7c3aed' : '#f59e0b')}; border-radius: 3px; transition: width 0.6s ease;"></div>
                    </div>
                </div>
            `).join('');
        }
    }

    // 4. Matched & Missing Badges
    document.getElementById('stat-matched-count').innerText = (data.matched_skills || []).length;
    document.getElementById('stat-missing-count').innerText = (data.missing_skills || []).length;

    const matchedContainer = document.getElementById('matched-badges');
    if (matchedContainer) {
        if ((data.matched_skills || []).length > 0) {
            matchedContainer.innerHTML = data.matched_skills.map(s => `<span class="badge badge-matched"><i class="fa-solid fa-check" style="font-size: 0.7rem; margin-right: 4px;"></i>${s}</span>`).join('');
        } else {
            matchedContainer.innerHTML = '<p class="text-muted" style="font-size:0.85rem; font-style:italic; padding: 6px 0;">No matching skills detected in uploaded resume.</p>';
        }
    }

    renderMissingBadges('all');

    // 5. Strategic ATS Keyword Advice
    const adviceContainer = document.getElementById('strategic-advice-container');
    if (adviceContainer) {
        const adviceList = data.strategic_advice || [];
        if (adviceList.length > 0) {
            adviceContainer.innerHTML = `
                <h4 style="font-size: 0.95rem; font-weight: 700; color: #334155; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                    <i class="fa-solid fa-lightbulb text-warning"></i> Strategic ATS Optimization Tips
                </h4>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    ${adviceList.map(a => `
                        <div style="background: rgba(124, 58, 237, 0.04); border-left: 3px solid #7c3aed; padding: 10px 14px; border-radius: 0 8px 8px 0;">
                            <h5 style="font-size: 0.88rem; font-weight: 700; color: #0f172a; margin-bottom: 2px;">${a.title}</h5>
                            <p style="font-size: 0.82rem; color: #475569; margin: 0; line-height: 1.4;">${a.text}</p>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            adviceContainer.innerHTML = '';
        }
    }

    // 6. Explainable AI Learning Roadmaps
    const recsList = document.getElementById('recommendations-list');
    const recs = data.structured_recommendations || [];
    if (recs.length > 0) {
        recsList.innerHTML = recs.map((r, idx) => `
            <div class="roadmap-card" style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; box-shadow: var(--shadow-sm); transition: transform 0.2s ease;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                    <div>
                        <h4 style="font-size: 1rem; font-weight: 800; color: #0f172a; margin-bottom: 2px;">
                            ${idx + 1}. ${r.skill}
                        </h4>
                        <span style="font-size: 0.75rem; color: #64748b; font-weight: 600;">${r.category}</span>
                    </div>
                    <div style="display: flex; gap: 6px; align-items: center;">
                        <span class="badge ${r.badge_class}" style="font-size: 0.75rem; padding: 3px 10px; border-radius: 20px; font-weight: 700;">${r.priority}</span>
                        <span style="font-size: 0.75rem; background: #f1f5f9; color: #475569; padding: 3px 8px; border-radius: 6px; font-weight: 600;"><i class="fa-regular fa-clock"></i> ${r.estimated_time}</span>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.85rem; color: #334155;">
                    <p style="margin: 0;"><strong style="color: #0f172a;"><i class="fa-solid fa-book-open text-primary" style="margin-right: 6px;"></i>Key Concepts:</strong> ${r.topics}</p>
                    <p style="margin: 0;"><strong style="color: #0f172a;"><i class="fa-solid fa-laptop-code text-success" style="margin-right: 6px;"></i>Hands-on Project:</strong> ${r.project_idea}</p>
                    <div style="background: #f8fafc; padding: 8px 12px; border-radius: 8px; border: 1px dashed #cbd5e1; font-size: 0.8rem; color: #475569;">
                        <strong><i class="fa-solid fa-wand-magic-sparkles text-warning" style="margin-right: 4px;"></i>ATS Keyword Tip:</strong> ${r.ats_tip}
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        recsList.innerHTML = '<p class="text-success" style="font-size:0.9rem; font-weight:600; padding: 12px 0;"><i class="fa-solid fa-circle-check"></i> Exceptional Match! No skill gaps identified for this role.</p>';
    }

    // Scroll to results
    document.getElementById('analyzer-results-card').scrollIntoView({ behavior: 'smooth' });
}

window.filterMissingBadges = function(type, event) {
    if (event) {
        document.querySelectorAll('.priority-filters .btn-filter').forEach(b => b.classList.remove('active'));
        event.target.classList.add('active');
    }
    renderMissingBadges(type);
};

function renderMissingBadges(filterType = 'all') {
    const missingContainer = document.getElementById('missing-badges');
    if (!missingContainer || !state.latestAnalysis) return;

    const data = state.latestAnalysis;
    const missingMust = new Set(data.missing_must_have || []);
    let itemsToRender = data.missing_skills || [];

    if (filterType === 'high') {
        itemsToRender = itemsToRender.filter(s => missingMust.has(s));
    }

    if (itemsToRender.length > 0) {
        missingContainer.innerHTML = itemsToRender.map(s => {
            const isMust = missingMust.has(s);
            const badgeClass = isMust ? 'badge-missing-critical' : 'badge-missing';
            const label = isMust ? `${s} (Must-Have)` : s;
            return `<span class="badge ${badgeClass}"><i class="fa-solid fa-triangle-exclamation" style="font-size:0.7rem; margin-right:4px;"></i>${label}</span>`;
        }).join('');
    } else {
        missingContainer.innerHTML = `<p class="text-muted" style="font-size:0.85rem; font-style:italic; padding: 6px 0;">No ${filterType === 'high' ? 'critical ' : ''}missing skills.</p>`;
    }
}

window.downloadAnalysisReport = function() {
    if (!state.latestAnalysis) {
        showToast('No analysis available to download. Please run a skill scan first.', 'warning');
        return;
    }

    showToast('Generating comprehensive Assessment PDF Report...', 'info');

    fetch('/api/report/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis_data: state.latestAnalysis })
    })
    .then(response => {
        if (response.ok) return response.blob();
        throw new Error('Failed to generate report PDF');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        const role = (state.latestAnalysis.job_role || 'Report').replace(/[\s\/]+/g, '_');
        a.download = `Elevora_Skill_Gap_Report_${role}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        showToast('Skill Gap PDF Report downloaded successfully!', 'success');
    })
    .catch(err => {
        showToast(err.message, 'error');
    });
};

window.downloadHistoricalReport = function(encodedRole, score, encodedMatched, encodedMissing) {
    try {
        const role = decodeURIComponent(encodedRole);
        const matched = JSON.parse(decodeURIComponent(encodedMatched));
        const missing = JSON.parse(decodeURIComponent(encodedMissing));
        
        showToast(`Preparing PDF report for ${role}...`, 'info');
        
        const payloadData = {
            job_role: role,
            composite_score: score,
            match_score: score,
            matched_skills: matched,
            missing_skills: missing,
            missing_must_have: missing.slice(0, 4),
            missing_good_to_have: missing.slice(4),
            sub_scores: {
                skill_coverage: score,
                must_have_score: score,
                good_to_have_score: score,
                semantic_similarity: score,
                ats_format_score: 85.0,
                impact_score: 75.0
            }
        };

        fetch('/api/report/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ analysis_data: payloadData })
        })
        .then(response => {
            if (response.ok) return response.blob();
            throw new Error('Failed to generate PDF');
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `Elevora_Skill_Gap_Report_${role.replace(/[\s\/]+/g, '_')}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            showToast(`Downloaded assessment report for ${role}!`, 'success');
        })
        .catch(err => {
            showToast(err.message, 'error');
        });
    } catch(e) {
        showToast('Failed to generate report from history.', 'error');
    }
};

// ==========================================
//            6. UI HELPERS (TOASTS)          
// ==========================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        'success': '<i class="fa-solid fa-circle-check toast-icon"></i>',
        'error': '<i class="fa-solid fa-triangle-exclamation toast-icon"></i>',
        'warning': '<i class="fa-solid fa-circle-exclamation toast-icon"></i>',
        'info': '<i class="fa-solid fa-circle-info toast-icon"></i>'
    };

    toast.innerHTML = `
        ${icons[type] || icons['info']}
        <div class="toast-message">${message}</div>
    `;
    
    container.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 400);
    }, 4000);
}

// ==========================================
//            7. THEME MANAGEMENT (DARK/LIGHT) 
// ==========================================

function initTheme() {
    const savedTheme = localStorage.getItem('elevora-theme') || 
        (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    applyTheme(savedTheme);
}

window.toggleTheme = function() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
};

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('elevora-theme', theme);
    
    const isDark = theme === 'dark';
    const iconClass = isDark ? 'fa-sun' : 'fa-moon';
    const iconColor = isDark ? '#fbbf24' : '#7c3aed';
    
    // Update theme toggle button icons
    ['landing-theme-toggle', 'app-theme-toggle'].forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.innerHTML = `<i class="fa-solid ${iconClass}"></i>`;
            btn.style.color = iconColor;
            btn.title = `Switch to ${isDark ? 'Light' : 'Dark'} Mode`;
        }
    });

    // Swap logos to ensure 100% sharp visibility in both Light and Dark modes
    const horizLogos = document.querySelectorAll('.brand-logo-horizontal');
    horizLogos.forEach(img => {
        if (img.id === 'footer-logo') return;
        img.src = isDark ? '/assets/logo_horizontal_dark.png' : '/assets/logo_horizontal.png';
    });

    const vertLogos = document.querySelectorAll('.brand-logo-vertical');
    vertLogos.forEach(img => {
        img.src = isDark ? '/assets/logo_dark.png' : '/assets/logo.png';
    });
}
