import os
import re
from pathlib import Path


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Извлекает YAML front matter и тело документа"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', text, re.DOTALL)
    if not match:
        return {}, text

    front_text = match.group(1)
    body = match.group(2)

    metadata = {}
    for line in front_text.split('\n'):
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()

        # Массив: ["tag1", "tag2"]
        if value.startswith('[') and value.endswith(']'):
            inner = value[1:-1]
            value = [t.strip().strip('"').strip("'") for t in inner.split(',') if t.strip()]
        # Строка в кавычках
        elif (value.startswith('"') and value.endswith('"')) or \
                (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        # Булево
        elif value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False

        metadata[key] = value

    return metadata, body


def parse_sections(body: str) -> dict:
    """Разбивает тело на секции по ## заголовкам, корректно обрабатывая code blocks"""
    sections = {}
    current_section = None
    current_lines = []
    in_code_block = False

    for line in body.split('\n'):
        # Отслеживаем code blocks (```), чтобы не разбивать их заголовками
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            current_lines.append(line)
            continue

        # Новый заголовок ## (только если не внутри code block)
        if line.startswith('## ') and not in_code_block:
            # Сохраняем предыдущую секцию
            if current_section is not None:
                sections[current_section] = '\n'.join(current_lines).strip()

            # Начинаем новую секцию
            section_name = line[3:].strip()
            # Ключ: lowercase + underscore
            current_section = section_name.lower().replace(' ', '_').replace('-', '_')
            current_lines = []
        else:
            current_lines.append(line)

    # Сохраняем последнюю секцию
    if current_section is not None:
        sections[current_section] = '\n'.join(current_lines).strip()

    return sections


def parse_md_file(filepath: str) -> dict:
    """Полный парсинг MD-файла: front matter + секции"""
    if not os.path.exists(filepath):
        return {"error": f"Файл не найден: {filepath}"}

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    metadata, body = parse_front_matter(content)
    sections = parse_sections(body)

    # ID из имени файла
    filename = Path(filepath).stem
    metadata['id'] = filename

    # Объединяем всё
    result = {**metadata, **sections}
    return result


def get_all_md_files(folder_path: str) -> list:
    """Получает все MD-файлы из папки"""
    if not os.path.exists(folder_path):
        return []

    files = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith('.md') and not filename.startswith('.'):
            filepath = os.path.join(folder_path, filename)
            data = parse_md_file(filepath)
            if 'error' not in data:
                files.append(data)

    return files