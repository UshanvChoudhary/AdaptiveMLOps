import os

def fix_react(file_path):
    if not os.path.exists(file_path): return
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix React unused
    content = content.replace("import React, {", "import {")
    content = content.replace("import React from", "// import React from")
    
    if "Governance.tsx" in file_path:
        content = content.replace("{pb-2  +", "{\"pb-2 \" +")
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

fix_react('frontend/src/App.tsx')
fix_react('frontend/src/components/Governance.tsx')
fix_react('frontend/src/components/PredictionFlow.tsx')
