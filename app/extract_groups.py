import json
from collections import defaultdict

# Путь к файлу Exercises.json
file_path = 'app/Exercises.json'

def extract_groups():
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    groups = defaultdict(set)
    for exercise in data:
        group = exercise.get('group')
        group_code = exercise.get('group_code')
        if group and group_code:
            groups[group].add(group_code)

    # Преобразуем в удобный формат
    return {group: list(codes)[0] for group, codes in groups.items()}

if __name__ == '__main__':
    groups = extract_groups()
    print(groups)
