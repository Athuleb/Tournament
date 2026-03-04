import os

file_path = r'd:\project\Tournament\tournament\templates\tournament\admin_dashboard.html'

# The exact target lines that are broken
broken_lines = [
    '<option value="Thiagarajar Polytechnic, Amballur" {% if',
    'selected_college=="Thiagarajar Polytechnic, Amballur" %}selected{% endif %}>Theyagaraja',
    'polytechnic, amballur</option>',
    '<option value="Sree rama polytechnic, thriprayar" {% if',
    'selected_college=="Sree rama polytechnic, thriprayar" %}selected{% endif %}>Sree rama',
    'polytechnic, thriprayar</option>',
    '<option value="Govt. Polytechnic, kunnakulam" {% if',
    'selected_college=="Govt. Polytechnic, kunnakulam" %}selected{% endif %}>Govt. Polytechnic,',
    'kunnakulam</option>',
    '<option value="Model polytechnic, vadakara" {% if',
    'selected_college=="Model polytechnic, vadakara" %}selected{% endif %}>Model polytechnic,',
    'vadakara</option>'
]

# The correct hardcoded list
colleges = [
    "Thiagarajar Polytechnic, Amballur",
    "Sree rama polytechnic, thriprayar",
    "Govt. Polytechnic, kunnakulam",
    "Model polytechnic, vadakara",
    "Kkmmptc, kallettumkara",
    "Holy grace polytechnic, mala",
    "Mets polytechnic, mala",
    "Iccs polytechnic, mupliyam"
]

fixed_template = ""
for c in colleges:
    fixed_template += f'                        <option value="{c}" {{% if selected_college == "{c}" %}}selected{{% endif %}}>{c}</option>\n'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Find the select block and replace it
# Match from <select to </select>
pattern = re.compile(r'<select name="college" class="filter-select" onchange="this.form.submit\(\)">\s*<option value="">All Colleges</option>.*?</select>', re.DOTALL)

replacement = f'<select name="college" class="filter-select" onchange="this.form.submit()">\n                        <option value="">All Colleges</option>\n{fixed_template}                    </select>'

# If basic replacement doesn't work, we'll try something else
new_text = re.sub(pattern, replacement, text)

with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_text)

print("SUCCESS: Finished writing the fixed template.")
