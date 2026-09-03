import os

def find_text_in_files(text):
    base_dir = "."
    matches = []
    for root, dirs, files in os.walk(base_dir):
        # Skip pycache and git
        if ".git" in root or "__pycache__" in root or ".streamlit" in root:
            continue
        for file in files:
            if file.endswith(('.py', '.json', '.md', '.html', '.txt')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for idx, line in enumerate(f, 1):
                            if text.lower() in line.lower():
                                matches.append((path, idx, line.strip()))
                except Exception:
                    pass
    return matches

if __name__ == '__main__':
    search_text = "John Doe"
    results = find_text_in_files(search_text)
    if results:
        print(f"Found {len(results)} matches for '{search_text}':")
        for path, line_num, line_content in results:
            print(f"- {path}:{line_num} -> {line_content}")
    else:
        print(f"No matches found for '{search_text}'.")
