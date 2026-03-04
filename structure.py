import os

EXCLUDED_DIRS = {'.venv', '__pycache__', '.git'}
EXCLUDED_FILES = {'.pyc', '.log', '.png', '.jpg'}

FILE_ICONS = {
    ".py": "🐍",    
    ".dockerfile": "🐳",  
    ".Dockerfile": "🐳",  
    ".jenkinsfile": "🐙",  
    ".json": "📝",  
}

def print_dir_structure(startpath, indent_level=0):
    indent = ' ' * (indent_level * 4)
    try:
        items = sorted(os.listdir(startpath))
    except PermissionError:
        return

    if indent_level == 0:
        service_name = os.path.basename(startpath)
        print(f"Service: {service_name}\n")
    
    dirs = []  
    files = []  
    
    for item in items:
        item_path = os.path.join(startpath, item)

        if os.path.isdir(item_path) and item not in EXCLUDED_DIRS:
            dirs.append(item)
        
        elif os.path.isfile(item_path) and not any(item.endswith(ext) for ext in EXCLUDED_FILES):
            files.append(item)
    
    for dir_item in dirs:
        print(f"{indent}📂 {dir_item}")
        print_dir_structure(os.path.join(startpath, dir_item), indent_level + 1)
    
    for file_item in files:
        file_icon = FILE_ICONS.get(os.path.splitext(file_item)[1], "📄")  
        print(f"{indent}{file_icon} {file_item}")

if __name__ == "__main__":
    project_root = os.getcwd()
    print(f"Project Structure: {project_root}\n")
    print_dir_structure(project_root)
