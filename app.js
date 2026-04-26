document.addEventListener("DOMContentLoaded", () => {
    // --- Global State Management (Context-like using LocalStorage) ---
    const getFormData = () => JSON.parse(localStorage.getItem("osteo_formData") || "{}");
    const setFormData = (data) => {
        const current = getFormData();
        const updated = { ...current, ...data };
        localStorage.setItem("osteo_formData", JSON.stringify(updated));
        return updated;
    };
    const getResult = () => JSON.parse(localStorage.getItem("osteo_result") || "null");
    const setResult = (res) => localStorage.setItem("osteo_result", JSON.stringify(res));

    // --- Mobile Sidebar Toggle Logic ---
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.getElementById('menu-btn');
    const closeBtn = document.getElementById('close-sidebar');

    if (menuBtn && sidebar) {
        menuBtn.addEventListener('click', () => {
            sidebar.classList.remove('-translate-x-full');
        });
    }

    if (closeBtn && sidebar) {
        closeBtn.addEventListener('click', () => {
            sidebar.classList.add('-translate-x-full');
        });
    }

    // --- UI Utility: Button Group Selection ---
    const setupButtonGroup = (selector, activeClass, inactiveClass, callback = null) => {
        const buttons = document.querySelectorAll(selector);
        buttons.forEach(btn => {
            btn.addEventListener("click", () => {
                buttons.forEach(b => {
                    b.classList.remove(...activeClass.split(' '));
                    b.classList.add(...inactiveClass.split(' '));
                });
                btn.classList.add(...activeClass.split(' '));
                btn.classList.remove(...inactiveClass.split(' '));
                if (callback) callback(btn.dataset.value);
            });
        });
    };

    // --- Page 1: ui.html (Patient Info) ---
    if (document.getElementById('gender-group')) {
        setupButtonGroup('.gender-btn', 'border-primary-container bg-primary-container/5 text-primary', 'bg-surface-container-low text-on-surface-variant', (val) => {
            setFormData({ 'Gender': val });
        });
        
        // Autofill
        const data = getFormData();
        if (data.Name) document.getElementById('patient-name').value = data.Name;
        if (data.Age) document.getElementById('patient-age').value = data.Age;
        if (data['Race/Ethnicity']) document.getElementById('patient-ethnicity').value = data['Race/Ethnicity'];
        if (data.Gender) {
            document.querySelectorAll('.gender-btn').forEach(btn => {
                if (btn.dataset.value === data.Gender) btn.click();
            });
        }

        document.getElementById('next-btn')?.addEventListener('click', () => {
            const currentData = {
                'Name': document.getElementById('patient-name')?.value || 'Guest',
                'Age': parseInt(document.getElementById('patient-age')?.value || 50),
                'Race/Ethnicity': document.getElementById('patient-ethnicity')?.value || 'Caucasian',
                'Gender': document.querySelector('.gender-btn.text-primary')?.dataset.value || 'Female'
            };
            setFormData(currentData);
            window.location.href = "medical_records.html";
        });
    }

    // --- Page 2: medical_records.html (Clinical Data) ---
    if (document.getElementById('medical-form')) {
        setupButtonGroup('.family-btn', 'border-primary bg-primary/5 text-primary', 'border-surface-container-high', (val) => setFormData({'Family History': val}));
        setupButtonGroup('.fracture-btn', 'border-primary bg-primary/5 text-primary', 'border-surface-container-high', (val) => setFormData({'Prior Fractures': val}));

        setupButtonGroup('.condition-toggle-btn', 'bg-primary text-white', 'bg-transparent', (val) => {
            const container = document.getElementById('medical-conditions-container');
            if (val === 'Yes') container.classList.remove('hidden');
            else {
                container.classList.add('hidden');
                setFormData({'Medical Conditions': 'None'});
            }
        });

        setupButtonGroup('.meds-toggle-btn', 'bg-primary text-white', 'bg-transparent', (val) => {
            const container = document.getElementById('medications-container');
            if (val === 'Yes') container.classList.remove('hidden');
            else {
                container.classList.add('hidden');
                setFormData({'Medications': 'None'});
            }
        });

        // Autofill Step 2
        const data = getFormData();
        if (data['Hormonal Changes']) document.getElementById('hormonal-changes').value = data['Hormonal Changes'];
        if (data['Family History']) {
            document.querySelectorAll('.family-btn').forEach(btn => {
                if(btn.dataset.value === data['Family History']) btn.click();
            });
        }
        if (data['Prior Fractures']) {
            document.querySelectorAll('.fracture-btn').forEach(btn => {
                if(btn.dataset.value === data['Prior Fractures']) btn.click();
            });
        }
        if (data['Medical Conditions'] && data['Medical Conditions'] !== 'None') {
            document.querySelector('.condition-toggle-btn[data-value="Yes"]')?.click();
            document.getElementById('medical-conditions').value = data['Medical Conditions'];
        }
        if (data['Medications'] && data['Medications'] !== 'None') {
            document.querySelector('.meds-toggle-btn[data-value="Yes"]')?.click();
            document.getElementById('medications').value = data['Medications'];
        }

        document.getElementById('next-btn-step2')?.addEventListener('click', () => {
            const hasConditions = document.querySelector('.condition-toggle-btn.bg-primary')?.dataset.value === 'Yes';
            const hasMeds = document.querySelector('.meds-toggle-btn.bg-primary')?.dataset.value === 'Yes';

            const currentData = {
                'Hormonal Changes': document.getElementById('hormonal-changes')?.value || 'Normal',
                'Family History': document.querySelector('.family-btn.text-primary')?.dataset.value || 'No',
                'Medical Conditions': hasConditions ? document.getElementById('medical-conditions')?.value : 'None',
                'Prior Fractures': document.querySelector('.fracture-btn.text-primary')?.dataset.value || 'No',
                'Medications': hasMeds ? document.getElementById('medications')?.value : 'None'
            };
            setFormData(currentData);
            window.location.href = "lifestyle_diet.html";
        });
    }

    // --- Page 3: lifestyle_diet.html (Lifestyle Data) ---
    if (document.getElementById('analyze-btn')) {
        setupButtonGroup('.weight-btn-step3', 'border-primary bg-primary/5 text-primary', 'border-outline-variant bg-surface-container-low', (val) => setFormData({'Body Weight': val}));
        setupButtonGroup('.activity-btn', 'border-primary bg-primary/5 text-primary', 'border-outline-variant bg-surface-container-low', (val) => setFormData({'Physical Activity': val}));
        setupButtonGroup('.vitamin-btn', 'border-primary bg-primary/5 text-primary', 'border-outline-variant bg-surface-container-low', (val) => setFormData({'Vitamin D Intake': val}));
        setupButtonGroup('.calcium-btn', 'border-primary bg-primary/5 text-primary', 'border-outline-variant bg-surface-container-low', (val) => setFormData({'Calcium Intake': val}));
        setupButtonGroup('.alcohol-btn', 'border-primary bg-primary/5 text-primary', 'border-outline-variant bg-surface-container-low', (val) => setFormData({'Alcohol Consumption': val}));
        setupButtonGroup('.smoking-btn', 'border-primary bg-primary/5 text-primary', 'border-outline-variant bg-surface-container-low', (val) => setFormData({'Smoking': val}));

        // Autofill Step 3
        const data = getFormData();
        const mapping = {
            'Body Weight': '.weight-btn-step3',
            'Physical Activity': '.activity-btn',
            'Vitamin D Intake': '.vitamin-btn',
            'Calcium Intake': '.calcium-btn',
            'Alcohol Consumption': '.alcohol-btn',
            'Smoking': '.smoking-btn'
        };
        Object.keys(mapping).forEach(key => {
            if (data[key]) {
                document.querySelectorAll(mapping[key]).forEach(btn => {
                    if (btn.dataset.value === data[key]) btn.click();
                });
            }
        });

        document.getElementById('analyze-btn')?.addEventListener('click', function() {
            const finalData = setFormData({
                'Body Weight': document.querySelector('.weight-btn-step3.text-primary')?.dataset.value || 'Normal',
                'Physical Activity': document.querySelector('.activity-btn.text-primary')?.dataset.value || 'Active',
                'Vitamin D Intake': document.querySelector('.vitamin-btn.text-primary')?.dataset.value || 'Sufficient',
                'Calcium Intake': document.querySelector('.calcium-btn.text-primary')?.dataset.value || 'Adequate',
                'Alcohol Consumption': document.querySelector('.alcohol-btn.text-primary')?.dataset.value || 'Unknown',
                'Smoking': document.querySelector('.smoking-btn.text-primary')?.dataset.value || 'No'
            });

            this.innerText = "Analyzing Risk...";
            this.disabled = true;

            fetch("/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(finalData)
            })
            .then(r => r.json())
            .then(res => {
                if (res.error) throw new Error(res.error);
                
                res.explanation = generateExplanation(finalData, res);
                setResult(res);
                window.location.href = res.high_risk ? "high_risk_result.html" : "results.html";
            })
            .catch(err => {
                console.error(err);
                alert("Analysis failed: " + err.message);
                this.innerText = "Analyze My Risk";
                this.disabled = false;
            });
        });
    }

    // --- Results Display Logic (Shared across all pages) ---
    const updateRiskDisplay = () => {
        const res = getResult();
        if (res) {
            const score = res.risk_score.toFixed(2);
            document.querySelectorAll(".risk-score-display").forEach(el => {
                el.innerText = score + "%";
            });
            
            const explanationEl = document.getElementById('risk-explanation');
            if (explanationEl) explanationEl.innerText = res.explanation;

            // Update progress bars if they exist
            const riskBar = document.getElementById('risk-bar');
            if (riskBar) riskBar.style.width = score + "%";

            // Render SHAP factors (Risk Drivers)
            const factorsContainer = document.getElementById('factors-container');
            const factorsList = document.getElementById('factors-list');
            if (factorsContainer && factorsList && res.top_factors && res.top_factors.length > 0) {
                factorsContainer.classList.remove('hidden');
                factorsList.innerHTML = res.top_factors.map(f => `
                    <div class="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-3 py-1.5 rounded-full border border-white/30 text-xs font-bold text-white shadow-sm">
                        <span class="material-symbols-outlined text-[14px]">shield_health</span>
                        ${f.factor}
                    </div>
                `).join('');
            }

            // Handle legacy text replacements
            document.querySelectorAll("h1, h2, p, span").forEach(el => {
                if (el.innerText.includes("12%") || el.innerText.includes("84%")) {
                    el.innerText = el.innerText.replace(/12%|84%/g, score + "%");
                }
            });

            // Add Persistent Risk Badge to Nav if not on result page
            if (!window.location.href.includes("result")) {
                const navContainer = document.querySelector('header .max-w-7xl') || document.querySelector('nav .max-w-7xl') || document.querySelector('nav div');
                if (navContainer && !document.getElementById('nav-risk-badge')) {
                    const badge = document.createElement('div');
                    badge.id = 'nav-risk-badge';
                    badge.className = 'hidden md:flex items-center gap-2 bg-primary/10 text-primary px-4 py-1.5 rounded-full text-sm font-bold border border-primary/20 mr-4';
                    badge.innerHTML = `<span class="material-symbols-outlined text-sm">analytics</span> Last Risk: ${score}%`;
                    
                    // Find a good spot in the nav (before the 'Get Started' button or at the end of links)
                    const target = navContainer.querySelector('.flex.items-center.gap-8') || navContainer.querySelector('.md\\:flex');
                    if (target) {
                        target.appendChild(badge);
                    } else {
                        // Fallback: prepend to the right-side container
                        navContainer.appendChild(badge);
                    }
                }
            }
        }
    };

    updateRiskDisplay();

    // --- Download Report Logic ---
    // Opens the styled report.html in a new tab with ?autoprint=1
    // That page auto-triggers window.print() so the user saves it as a PDF
    // preserving the exact visual design of the clinical report.
    const downloadBtn = document.getElementById('download-report-btn') || document.querySelector('.download-btn');
    downloadBtn?.addEventListener('click', (e) => {
        e.preventDefault();
        const res = getResult();
        const formData = getFormData();

        if (!res || !formData || Object.keys(formData).length === 0) {
            alert("No assessment result found. Please complete the assessment first.");
            return;
        }

        // Open styled report in new tab — that page will auto-trigger print
        window.open('report.html?autoprint=1', '_blank');
    });

    function generateExplanation(inputs, result) {
        let factors = [];
        if (inputs.Age > 65) factors.push("advanced age");
        if (inputs['Prior Fractures'] === 'Yes') factors.push("history of fractures");
        if (inputs['Family History'] === 'Yes') factors.push("genetic predisposition");
        if (inputs['Body Weight'] === 'Underweight') factors.push("low body mass");
        if (inputs['Smoking'] === 'Yes') factors.push("smoking habits");
        if (inputs['Calcium Intake'] === 'Low') factors.push("insufficient calcium");

        if (factors.length === 0) return "Your profile shows standard bone density markers with no immediate alarm factors.";
        
        const riskLevel = result.high_risk ? "significant" : "minor";
        return `Your ${result.risk_score.toFixed(2)}% risk score is primarily influenced by ${factors.join(", ")}. These are ${riskLevel} contributors to bone density variance.`;
    }
});

