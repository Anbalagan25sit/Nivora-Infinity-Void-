import ast
import os
import sys

imports = set()
for root, dirs, files in os.walk('.'):
    if '.venv' in root or '__pycache__' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            try:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module.split('.')[0])
            except Exception:
                pass

stdlib = sys.stdlib_module_names if hasattr(sys, 'stdlib_module_names') else set()
local_modules = {os.path.splitext(f)[0] for root, dirs, files in os.walk('.') for f in files if f.endswith('.py')}

third_party = imports - local_modules - stdlib - set(sys.builtin_module_names) - {'mcp_client', 'src'}
print('DETECTED_IMPORTS: ' + ' '.join(third_party))
