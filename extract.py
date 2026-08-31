import json

with open(r'C:\Users\ADMIN\.gemini\antigravity-ide\brain\7eec4ace-0575-4393-8d54-b360b82d9f1d\.system_generated\steps\123\content.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith('{'):
            data = json.loads(line.strip())
            print(f"Blog: {data.get('blog')}")
            print(f"Bio: {data.get('bio')}")
            print(f"Name: {data.get('name')}")
            break
