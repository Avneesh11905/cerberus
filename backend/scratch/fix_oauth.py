import os

auth_routes_dir = r"d:\Cerberus\v2\cerberus\backend\src\modules\auth\api\routes"

for filename in ["login.py", "register.py"]:
    filepath = os.path.join(auth_routes_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    imports = []
    code = []

    inside_import = False
    for line in lines:
        if line.startswith("import ") or line.startswith("from "):
            imports.append(line)
            if "(" in line and ")" not in line:
                inside_import = True
        elif inside_import:
            imports.append(line)
            if ")" in line:
                inside_import = False
        else:
            code.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(imports)
        f.writelines(code)
