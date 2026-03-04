import os

file_path = r'd:\project\Tournament\tournament\templates\tournament\admin_dashboard.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content.replace('selected_college==college', 'selected_college == college')

if new_content == content:
    print('No changes needed or string not found.')
else:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('File updated successfully.')
