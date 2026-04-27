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
                document.querySelectorAll('.gender-btn').forEach(b => b.className = "gender-btn flex items-center justify-center space-x-3 py-4 md:py-6 px-4 rounded-2xl border-2 border-outline-variant bg-surface-container-low text-on-surface-variant transition-all");
                btn.className = "gender-btn flex items-center justify-center space-x-3 py-4 md:py-6 px-4 rounded-2xl border-2 border-primary-container bg-primary-container/5 text-primary shadow-md transition-all";
                btn.classList.add('selected');
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
                    document.querySelectorAll('.' + className).forEach(b => b.className = `${className} py-4 md:py-5 rounded-2xl border-2 border-outline-variant bg-surface-container-low font-bold`);
                    btn.className = `${className} py-4 md:py-5 rounded-2xl border-2 border-primary bg-primary/5 text-primary font-bold selected`;
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

        // Condition Toggle Logic
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
                    document.querySelectorAll('.' + className).forEach(b => b.className = `${className} py-4 rounded-xl border-2 border-outline-variant text-sm font-bold`);
                    btn.className = `${className} py-4 rounded-xl border-2 border-primary bg-primary/5 text-primary text-sm font-bold selected`;
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

        if (riskPercentage) riskPercentage.innerText = result.risk_score.toFixed(1) + '%';
        if (riskBar) riskBar.style.width = result.risk_score + '%';
        if (riskExplanation) riskExplanation.innerText = result.explanation;

        if (result.top_factors && factorsList) {
            factorsContainer.classList.remove('hidden');
            factorsList.innerHTML = result.top_factors.map(f => `
                <div class="px-4 py-2 bg-white/20 rounded-xl text-xs font-bold border border-white/30 backdrop-blur-sm">
                    ${f.feature}: +${(f.impact * 100).toFixed(1)}%
                </div>
            `).join('');
        }

        document.getElementById('download-report-btn')?.addEventListener('click', async () => {
            const formData = getFormData();
            try {
                const response = await fetch('/api/download-report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ...formData, ...result })
                });
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `OsteoScan_Report_${formData.Name || 'Patient'}.pdf`;
                a.click();
            } catch (err) {
                alert("Failed to generate report.");
            }
        });
    }
});
