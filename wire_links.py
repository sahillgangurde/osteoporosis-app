import os

def replace_in_file(filename, replacements):
    if not os.path.exists(filename):
        return
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

# DASHBOARD
replace_in_file('dashboard.html', [
    ('href="#">Home', 'href="dashboard.html">Home'),
    ('href="#">How it Works', 'href="about.html">How it Works'),
    ('<button class="bg-primary-container text-on-primary px-6 py-2.5 rounded-full font-headline font-bold text-sm shadow-[0px_4px_12px_rgba(74,58,255,0.2)] active:scale-95 transition-all">\n                Get Started\n            </button>',
     '<button onclick="window.location.href=\'ui.html\'" class="bg-primary-container text-on-primary px-6 py-2.5 rounded-full font-headline font-bold text-sm shadow-[0px_4px_12px_rgba(74,58,255,0.2)] active:scale-95 transition-all">\n                Get Started\n            </button>'),
    ('<button class="bg-primary-container text-on-primary px-8 py-4 rounded-xl font-headline font-bold text-lg shadow-[0px_8px_24px_rgba(74,58,255,0.25)] hover:translate-y-[-2px] transition-all flex items-center justify-center gap-3">\n                            Start Free Check',
     '<button onclick="window.location.href=\'ui.html\'" class="bg-primary-container text-on-primary px-8 py-4 rounded-xl font-headline font-bold text-lg shadow-[0px_8px_24px_rgba(74,58,255,0.25)] hover:translate-y-[-2px] transition-all flex items-center justify-center gap-3">\n                            Start Free Check'),
    ('<button class="bg-surface-container-lowest text-primary px-8 py-4 rounded-xl font-headline font-bold text-lg border border-outline-variant/15 hover:bg-surface-container-low transition-all flex items-center justify-center gap-3">\n                            Learn Methodology\n                        </button>',
     '<button onclick="window.location.href=\'about.html\'" class="bg-surface-container-lowest text-primary px-8 py-4 rounded-xl font-headline font-bold text-lg border border-outline-variant/15 hover:bg-surface-container-low transition-all flex items-center justify-center gap-3">\n                            Learn Methodology\n                        </button>')
])

# UI (Assessment)
replace_in_file('ui.html', [
    ('<button class="flex-[2] py-3 text-sm font-bold bg-primary text-white rounded-xl shadow-lg shadow-primary/30 active:scale-95 transition-all">Analyze My Risk</button>',
     '<button onclick="window.location.href=\'risk_assessment.html\'" class="flex-[2] py-3 text-sm font-bold bg-primary text-white rounded-xl shadow-lg shadow-primary/30 active:scale-95 transition-all">Analyze My Risk</button>'),
    ('<div class="flex flex-col items-center justify-center p-2 text-slate-400 dark:text-slate-500 hover:text-[#4A3AFF] transition-all">',
     '<div onclick="window.location.href=\'dashboard.html\'" class="cursor-pointer flex flex-col items-center justify-center p-2 text-slate-400 dark:text-slate-500 hover:text-[#4A3AFF] transition-all">'),
    ('<div class="flex flex-col items-center justify-center p-2 text-slate-400 dark:text-slate-500 hover:text-[#4A3AFF] transition-all">\n<span class="material-symbols-outlined text-[24px]">description</span>\n<span class="font-[\'Plus_Jakarta_Sans\'] text-[9px] font-bold uppercase tracking-tight">Results</span>\n</div>',
     '<div onclick="window.location.href=\'results.html\'" class="cursor-pointer flex flex-col items-center justify-center p-2 text-slate-400 dark:text-slate-500 hover:text-[#4A3AFF] transition-all">\n<span class="material-symbols-outlined text-[24px]">description</span>\n<span class="font-[\'Plus_Jakarta_Sans\'] text-[9px] font-bold uppercase tracking-tight">Results</span>\n</div>'),
    ('<div class="flex flex-col items-center justify-center p-2 text-slate-400 dark:text-slate-500 hover:text-[#4A3AFF] transition-all">\n<span class="material-symbols-outlined text-[24px]">lightbulb</span>\n<span class="font-[\'Plus_Jakarta_Sans\'] text-[9px] font-bold uppercase tracking-tight">Tips</span>\n</div>',
     '<div onclick="window.location.href=\'tips.html\'" class="cursor-pointer flex flex-col items-center justify-center p-2 text-slate-400 dark:text-slate-500 hover:text-[#4A3AFF] transition-all">\n<span class="material-symbols-outlined text-[24px]">lightbulb</span>\n<span class="font-[\'Plus_Jakarta_Sans\'] text-[9px] font-bold uppercase tracking-tight">Tips</span>\n</div>'),
     ('<div class="flex flex-col items-center justify-center p-2 text-slate-400 dark:text-slate-500 hover:text-[#4A3AFF] transition-all">\n<span class="material-symbols-outlined text-[24px]">info</span>\n<span class="font-[\'Plus_Jakarta_Sans\'] text-[9px] font-bold uppercase tracking-tight">About</span>\n</div>',
     '<div onclick="window.location.href=\'about.html\'" class="cursor-pointer flex flex-col items-center justify-center p-2 text-slate-400 dark:text-slate-500 hover:text-[#4A3AFF] transition-all">\n<span class="material-symbols-outlined text-[24px]">info</span>\n<span class="font-[\'Plus_Jakarta_Sans\'] text-[9px] font-bold uppercase tracking-tight">About</span>\n</div>')
])

# RISK ASSESSMENT
replace_in_file('risk_assessment.html', [
    ('href="#">Assessments</a>', 'href="ui.html">Assessments</a>'),
    ('href="#">Methodology</a>', 'href="about.html">Methodology</a>'),
    ('<button class="flex items-center justify-center gap-2 px-8 py-4 rounded-full font-bold text-primary ghost-border hover:bg-surface-container-high transition-all active:scale-95">\n<span class="material-symbols-outlined" data-icon="arrow_back">arrow_back</span>\n                                    Previous Step\n                                </button>',
     '<button onclick="window.location.href=\'ui.html\'" class="flex items-center justify-center gap-2 px-8 py-4 rounded-full font-bold text-primary ghost-border hover:bg-surface-container-high transition-all active:scale-95">\n<span class="material-symbols-outlined" data-icon="arrow_back">arrow_back</span>\n                                    Previous Step\n                                </button>'),
    ('<button class="flex items-center justify-center gap-2 px-12 py-4 rounded-full font-bold bg-primary-container text-on-primary shadow-[0px_4px_12px_rgba(74,58,255,0.2)] hover:opacity-90 transition-all active:scale-95">\n                                    Save &amp; Continue\n                                    <span class="material-symbols-outlined" data-icon="arrow_forward">arrow_forward</span>\n</button>',
     '<button onclick="window.location.href=\'results.html\'" class="flex items-center justify-center gap-2 px-12 py-4 rounded-full font-bold bg-primary-container text-on-primary shadow-[0px_4px_12px_rgba(74,58,255,0.2)] hover:opacity-90 transition-all active:scale-95">\n                                    Save &amp; Continue\n                                    <span class="material-symbols-outlined" data-icon="arrow_forward">arrow_forward</span>\n</button>'),
     ('<button class="bg-[#4a3aff] text-white px-6 py-2 rounded-full font-bold active:scale-95 transition-transform">Get Started</button>',
      '<button onclick="window.location.href=\'ui.html\'" class="bg-[#4a3aff] text-white px-6 py-2 rounded-full font-bold active:scale-95 transition-transform">Get Started</button>')
])

# RESULTS AND HIGH RISK RESULTS
for f in ['results.html', 'high_risk_result.html']:
    replace_in_file(f, [
        ('href="#">Dashboard</a>', 'href="dashboard.html">Dashboard</a>'),
        ('href="#">Results</a>', 'href="results.html">Results</a>'),
        ('href="#">Resources</a>', 'href="tips.html">Resources</a>'),
        ('<button class="w-full bg-surface-container-high text-on-surface font-headline font-bold py-3 px-6 rounded-xl hover:bg-outline-variant/30 transition-colors active:scale-95 flex items-center justify-center gap-2">\n<span class="material-symbols-outlined text-xl">refresh</span>\n                            Check Again\n                        </button>',
         '<button onclick="window.location.href=\'ui.html\'" class="w-full bg-surface-container-high text-on-surface font-headline font-bold py-3 px-6 rounded-xl hover:bg-outline-variant/30 transition-colors active:scale-95 flex items-center justify-center gap-2">\n<span class="material-symbols-outlined text-xl">refresh</span>\n                            Check Again\n                        </button>'),
        ('<button class="bg-primary-container text-on-primary px-6 py-2 rounded-lg font-manrope font-bold text-lg tracking-tight active:scale-95 transition-transform shadow-[0px_4px_12px_rgba(74,58,255,0.2)]">\n                Get Started\n            </button>',
         '<button onclick="window.location.href=\'ui.html\'" class="bg-primary-container text-on-primary px-6 py-2 rounded-lg font-manrope font-bold text-lg tracking-tight active:scale-95 transition-transform shadow-[0px_4px_12px_rgba(74,58,255,0.2)]">\n                Get Started\n            </button>'),
        ('<button class="text-[#4A3AFF] font-bold py-2 px-6 rounded-full border border-primary-container/10 active:scale-95 transition-transform">Get Started</button>',
         '<button onclick="window.location.href=\'ui.html\'" class="text-[#4A3AFF] font-bold py-2 px-6 rounded-full border border-primary-container/10 active:scale-95 transition-transform">Get Started</button>'),
        ('<button class="text-slate-600 dark:text-slate-400 font-medium font-plus-jakarta hover:text-[#4A3AFF] transition-colors duration-200">History</button>',
         '<button onclick="window.location.href=\'dashboard.html\'" class="text-slate-600 dark:text-slate-400 font-medium font-plus-jakarta hover:text-[#4A3AFF] transition-colors duration-200">Dashboard</button>')
    ])

# TIPS
replace_in_file('tips.html', [
    ('href="#">Analysis</a>', 'href="ui.html">Analysis</a>'),
    ('href="#">Health Tips</a>', 'href="tips.html">Health Tips</a>'),
    ('href="#">Technology</a>', 'href="about.html">Technology</a>'),
    ('href="#">Clinical Profile</a>', 'href="dashboard.html">Clinical Profile</a>'),
    ('href="#">Start Analysis</a>', 'href="ui.html">Start Analysis</a>')
])

# ABOUT
replace_in_file('about.html', [
    ('href="#">Analysis</a>', 'href="ui.html">Analysis</a>'),
    ('href="#">Health Tips</a>', 'href="tips.html">Health Tips</a>'),
    ('href="#">Technology</a>', 'href="about.html">Technology</a>'),
    ('href="#">About Us</a>', 'href="about.html">About Us</a>')
])

print("Wiring done")
