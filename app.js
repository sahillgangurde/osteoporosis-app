document.addEventListener('DOMContentLoaded', () => {
    // --- State Management ---
    const getFormData = () => JSON.parse(localStorage.getItem("osteo_formData") || "{}");
    const setFormData = (data) => {
        const current = getFormData();
        localStorage.setItem("osteo_formData", JSON.stringify({ ...current, ...data }));
    };
    const getResult = () => JSON.parse(localStorage.getItem("osteo_result") || "null");
    const setResult = (res) => localStorage.setItem("osteo_result", JSON.stringify(res));
    const clearAllData = () => {
        localStorage.removeItem("osteo_formData");
        localStorage.removeItem("osteo_result");
    };

    // --- Utility: Show Validation Warning ---
    const showWarning = (message) => {
        let warningDiv = document.getElementById('validation-warning');
        if (!warningDiv) {
            warningDiv = document.createElement('div');
            warningDiv.id = 'validation-warning';
            warningDiv.className = "fixed top-24 left-1/2 -translate-x-1/2 bg-red-600 text-white px-6 py-3 rounded-full shadow-2xl z-[100] font-bold flex items-center gap-2 animate-bounce";
            document.body.appendChild(warningDiv);
        }
        warningDiv.innerHTML = `<span class="material-symbols-outlined">warning</span> ${message}`;
        warningDiv.style.display = 'flex';
        setTimeout(() => { warningDiv.style.display = 'none'; }, 4000);
    };

    // --- Sidebar Logic ---
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.getElementById('menu-btn');
    const closeBtn = document.getElementById('close-sidebar');

    menuBtn?.addEventListener('click', () => sidebar?.classList.remove('-translate-x-full'));
    closeBtn?.addEventListener('click', () => sidebar?.classList.add('-translate-x-full'));

    // --- Page 1: ui.html (Patient Info) ---
    if (document.getElementById('step1-form')) {
        document.querySelectorAll('.gender-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.gender-btn').forEach(b => {
                    b.classList.remove('selected', 'border-primary-container', 'bg-primary-container/5', 'text-primary', 'shadow-md');
                    b.classList.add('border-slate-100', 'bg-slate-50');
                });
                btn.classList.add('selected', 'border-primary-container', 'bg-primary-container/5', 'text-primary', 'shadow-md');
                btn.classList.remove('border-slate-100', 'bg-slate-50');
            });
        });

        document.getElementById('next-btn')?.addEventListener('click', () => {
            const name = document.getElementById('patient-name')?.value.trim();
            const age = document.getElementById('patient-age')?.value;
            const ethnicity = document.getElementById('patient-ethnicity')?.value;
            const genderBtn = document.querySelector('.gender-btn.selected');

            if (!name || !age || !ethnicity || !genderBtn) {
                showWarning("Please enter Name, Age, Ethnicity and Select Gender.");
                return;
            }

            setFormData({
                'Name': name,
                'Age': parseInt(age),
                'Race/Ethnicity': ethnicity,
                'Gender': genderBtn.dataset.value
            });
            window.location.href = "medical_records.html";
        });
    }

    // --- Page 2: medical_records.html ---
    if (document.getElementById('medical-form')) {
        const setupButtonGroup = (className) => {
            document.querySelectorAll('.' + className).forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.' + className).forEach(b => {
                        b.classList.remove('selected', 'border-primary', 'bg-primary/5', 'text-primary');
                        b.classList.add('border-slate-100', 'bg-slate-50');
                    });
                    btn.classList.add('selected', 'border-primary', 'bg-primary/5', 'text-primary');
                    btn.classList.remove('border-slate-100', 'bg-slate-50');
                });
            });
        };

        setupButtonGroup('family-btn');
        setupButtonGroup('fracture-btn');
        setupButtonGroup('condition-toggle-btn');

        document.getElementById('next-btn-step2')?.addEventListener('click', () => {
            const hormonal = document.getElementById('hormonal-changes').value;
            const familyBtn = document.querySelector('.family-btn.selected');
            const fractureBtn = document.querySelector('.fracture-btn.selected');
            const conditionBtn = document.querySelector('.condition-toggle-btn.selected');

            if (!familyBtn || !fractureBtn || !conditionBtn) {
                showWarning("Please select all medical options to proceed.");
                return;
            }

            setFormData({
                'Hormonal Changes': hormonal,
                'Family History': familyBtn.dataset.value,
                'Prior Fractures': fractureBtn.dataset.value,
                'Medical Conditions': conditionBtn.dataset.value === 'Yes' ? document.getElementById('medical-conditions').value : 'None'
            });
            window.location.href = "lifestyle_diet.html";
        });

        document.querySelectorAll('.condition-toggle-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const container = document.getElementById('medical-conditions-container');
                if (btn.dataset.value === 'Yes') container.classList.remove('hidden');
                else container.classList.add('hidden');
            });
        });
    }

    // --- Page 3: lifestyle_diet.html ---
    if (document.getElementById('lifestyle-form')) {
        const setupButtonGroup = (className) => {
            document.querySelectorAll('.' + className).forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.' + className).forEach(b => {
                        b.classList.remove('selected', 'border-primary-container', 'bg-primary-container/5', 'text-primary');
                        b.classList.add('border-slate-100', 'bg-slate-50');
                    });
                    btn.classList.add('selected', 'border-primary-container', 'bg-primary-container/5', 'text-primary');
                    btn.classList.remove('border-slate-100', 'bg-slate-50');
                });
            });
        };

        setupButtonGroup('weight-btn-step3');
        setupButtonGroup('activity-btn');
        setupButtonGroup('calcium-btn');
        setupButtonGroup('vitamin-btn');
        setupButtonGroup('smoking-btn');
        setupButtonGroup('alcohol-btn');

        document.getElementById('analyze-btn')?.addEventListener('click', async () => {
            const weightBtn = document.querySelector('.weight-btn-step3.selected');
            const activityBtn = document.querySelector('.activity-btn.selected');
            const calciumBtn = document.querySelector('.calcium-btn.selected');
            const vitaminBtn = document.querySelector('.vitamin-btn.selected');
            const smokingBtn = document.querySelector('.smoking-btn.selected');
            const alcoholBtn = document.querySelector('.alcohol-btn.selected');

            if (!weightBtn || !activityBtn || !calciumBtn || !vitaminBtn || !smokingBtn || !alcoholBtn) {
                showWarning("Please complete all lifestyle markers.");
                return;
            }

            const finalData = {
                ...getFormData(),
                'Body Weight': weightBtn.dataset.value,
                'Physical Activity': activityBtn.dataset.value,
                'Calcium Intake': calciumBtn.dataset.value,
                'Vitamin D Intake': vitaminBtn.dataset.value,
                'Smoking History': smokingBtn.dataset.value,
                'Alcohol Consumption': alcoholBtn.dataset.value
            };

            const btn = document.getElementById('analyze-btn');
            btn.innerHTML = `<span class="animate-spin material-symbols-outlined">sync</span> Analyzing...`;
            btn.disabled = true;

            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(finalData)
                });
                const result = await response.json();
                setResult(result);
                window.location.href = result.risk_score > 50 ? "high_risk_result.html" : "results.html";
            } catch (err) {
                showWarning("Server error. Please try again.");
                btn.innerHTML = `Analyze My Risk <span class="material-symbols-outlined">analytics</span>`;
                btn.disabled = false;
            }
        });
    }

    // --- Result Pages Logic ---
    const result = getResult();
    if (result && (window.location.pathname.includes('result'))) {
        const riskPercentage = document.getElementById('risk-percentage');
        const riskBar = document.getElementById('risk-bar');
        const riskExplanation = document.getElementById('risk-explanation');
        const factorsList = document.getElementById('factors-list');
        const factorsContainer = document.getElementById('factors-container');
        const patientSummary = document.getElementById('patient-summary');

        if (riskPercentage) riskPercentage.innerText = result.risk_score.toFixed(1) + '%';
        if (riskBar) riskBar.style.width = result.risk_score + '%';
        if (riskExplanation) riskExplanation.innerText = result.explanation || "Clinical assessment complete.";

        const formData = getFormData();
        if (patientSummary) {
            patientSummary.innerHTML = `
                <div class="flex justify-between border-b border-white/10 pb-2"><span>Full Name:</span> <span>${formData.Name || 'N/A'}</span></div>
                <div class="flex justify-between border-b border-white/10 pb-2"><span>Age:</span> <span>${formData.Age || 'N/A'}</span></div>
                <div class="flex justify-between border-b border-white/10 pb-2"><span>Gender:</span> <span>${formData.Gender || 'N/A'}</span></div>
                <div class="flex justify-between border-b border-white/10 pb-2"><span>Origin:</span> <span>${formData['Race/Ethnicity'] || 'N/A'}</span></div>
            `;
        }

        if (result.top_factors && factorsList) {
            factorsContainer.classList.remove('hidden');
            factorsList.innerHTML = result.top_factors.map(f => `
                <div class="px-4 py-2 bg-white/20 rounded-xl text-xs font-bold border border-white/30 backdrop-blur-sm">
                    ${f.factor}: +${(f.impact * 100).toFixed(1)}%
                </div>
            `).join('');
        }

        // --- DIRECT PDF DOWNLOAD USING PROFESSIONAL REPORT TEMPLATE ---
        document.getElementById('download-report-btn')?.addEventListener('click', () => {
            const btn = document.getElementById('download-report-btn');
            const originalText = btn.innerHTML;
            btn.innerHTML = `<span class="animate-spin material-symbols-outlined" style="margin-right: 8px; animation: spin 1s linear infinite;">sync</span> Generating PDF...`;
            btn.disabled = true;

            // Fetch the professional report template
            fetch('report.html')
                .then(res => res.text())
                .then(html => {
                    // Parse the template
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const reportContainer = doc.querySelector('.report-container');
                    
                    // Manually populate the template with local data
                    const data = { ...getFormData(), ...getResult() };
                    
                    if(reportContainer.querySelector('#p-name')) reportContainer.querySelector('#p-name').innerText = data.Name || 'N/A';
                    if(reportContainer.querySelector('#p-age')) reportContainer.querySelector('#p-age').innerText = data.Age || 'N/A';
                    if(reportContainer.querySelector('#p-gender')) reportContainer.querySelector('#p-gender').innerText = data.Gender || 'N/A';
                    if(reportContainer.querySelector('#report-date')) reportContainer.querySelector('#report-date').innerText = "Date: " + new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
                    
                    const score = parseFloat(data.risk_score || 0).toFixed(2);
                    if(reportContainer.querySelector('#risk-val')) reportContainer.querySelector('#risk-val').innerText = score + "%";
                    
                    const levelTag = reportContainer.querySelector('#risk-lvl-tag');
                    if(levelTag) {
                        if (score < 30) {
                            levelTag.innerText = "Low Risk";
                            levelTag.className = "risk-level-indicator level-low";
                            levelTag.style.background = "#e6fffa"; levelTag.style.color = "#2c7a7b"; levelTag.style.padding = "6px 16px"; levelTag.style.borderRadius = "20px";
                        } else if (score < 60) {
                            levelTag.innerText = "Moderate Risk";
                            levelTag.className = "risk-level-indicator level-medium";
                            levelTag.style.background = "#fffaf0"; levelTag.style.color = "#975a16"; levelTag.style.padding = "6px 16px"; levelTag.style.borderRadius = "20px";
                        } else {
                            levelTag.innerText = "High Risk";
                            levelTag.className = "risk-level-indicator level-high";
                            levelTag.style.background = "#fff5f5"; levelTag.style.color = "#c53030"; levelTag.style.padding = "6px 16px"; levelTag.style.borderRadius = "20px";
                        }
                    }
                    if(reportContainer.querySelector('#risk-analysis')) reportContainer.querySelector('#risk-analysis').innerText = data.explanation || "Clinical assessment complete.";
                    
                    const inputDataContainer = reportContainer.querySelector('#input-data-container');
                    if(inputDataContainer) {
                        inputDataContainer.innerHTML = '';
                        const fields = ['Body Weight', 'Physical Activity', 'Vitamin D Intake', 'Calcium Intake', 'Alcohol Consumption', 'Smoking', 'Race/Ethnicity', 'Hormonal Changes', 'Family History', 'Medical Conditions', 'Prior Fractures', 'Medications'];
                        fields.forEach(field => {
                            inputDataContainer.innerHTML += `<div class="data-row" style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #f0f0f0; font-size:13px;"><span class="data-label" style="font-weight:600; color:#4a4a4a;">${field}</span><span class="data-value" style="font-weight:700;">${data[field] || 'Unknown'}</span></div>`;
                        });
                    }

                    // Extract styles
                    const style = doc.querySelector('style').cloneNode(true);
                    
                    // Create an off-screen wrapper for html2pdf to process
                    const wrapper = document.createElement('div');
                    wrapper.style.position = 'absolute';
                    wrapper.style.left = '-9999px';
                    wrapper.style.top = '0';
                    wrapper.style.background = 'white';
                    wrapper.appendChild(style);
                    wrapper.appendChild(reportContainer);
                    document.body.appendChild(wrapper);

                    const opt = {
                        margin:       0,
                        filename:     `OsteoScan_Report_${data.Name || 'Patient'}.pdf`,
                        image:        { type: 'jpeg', quality: 1.0 },
                        html2canvas:  { scale: 2, useCORS: true, logging: false },
                        jsPDF:        { unit: 'in', format: 'a4', orientation: 'portrait' }
                    };

                    html2pdf().set(opt).from(reportContainer).save().then(() => {
                        document.body.removeChild(wrapper);
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                    }).catch(err => {
                        console.error("PDF Generation Error", err);
                        document.body.removeChild(wrapper);
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                        alert("Could not generate PDF. Please try again.");
                    });
                }).catch(err => {
                    console.error("Template Fetch Error", err);
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                    alert("Could not fetch report template.");
                });
        });
    }
});
