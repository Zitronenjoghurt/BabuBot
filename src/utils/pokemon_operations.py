from src.utils.dict_operations import get_safe_from_path

def parse_localized_names(names: list[dict], languages: list[str]) -> dict[str, str]:
    language_name_map = {}
    for entry in names:
        language = get_safe_from_path(entry, ["language", "name"])
        if not isinstance(language, str) or language not in languages:
            continue
        name = entry.get("name", None)
        if not isinstance(name, str):
            continue
        language_name_map[language] = name
    return language_name_map

# Returns in format {version: {language: text}}
def parse_localized_flavor_texts(texts: list[dict], languages: list[str]) -> dict[str, dict[str, str]]:
    version_language_text_map = {}
    for entry in texts:
        language = get_safe_from_path(entry, ["language", "name"])
        if not isinstance(language, str) or language not in languages:
            continue
        
        # Fallback to version_group if version doesnt exist
        version = get_safe_from_path(entry, ["version", "name"])
        if not isinstance(version, str):
            version = get_safe_from_path(entry, ["version_group", "name"])
        if not isinstance(version, str):
            continue

        text = entry.get("flavor_text", None)
        if not isinstance(text, str):
            continue
        if version not in version_language_text_map:
            version_language_text_map[version] = {}
        version_language_text_map[version][language] = text.replace("\n", " ")
    return version_language_text_map