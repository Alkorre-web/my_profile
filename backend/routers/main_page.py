from fastapi import APIRouter
import os

router = APIRouter()


@router.get("/artifacts", summary="Получить список артефактов")
def get_artifacts():
    try:
        from utils.md_parser import get_all_md_files
        artifacts = get_all_md_files("/docs/artifacts")

        return [
            {
                "id": a.get("id"),
                "title": a.get("title", "Без названия"),
                "short_description": a.get("краткое_описание", ""),
                "category": a.get("category", ""),
                "tags": a.get("tags", []),
            }
            for a in artifacts
        ]
    except Exception as e:
        return {"error": str(e)}


@router.get("/artifacts/{artifact_id}", summary="Получить артефакт полностью")
def get_artifact(artifact_id: str):
    try:
        from utils.md_parser import parse_md_file
        filepath = f"/docs/artifacts/{artifact_id}.md"

        if not os.path.exists(filepath):
            return {"error": "Артефакт не найден"}

        return parse_md_file(filepath)
    except Exception as e:
        return {"error": str(e)}


@router.get("/resume", summary="Получить текст резюме")
def get_resume():
    try:
        resume_path = "/docs/resume.md"
        if not os.path.exists(resume_path):
            return {"error": "Файл docs/resume.md не найден"}

        with open(resume_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {"content": content}
    except Exception as e:
        return {"error": str(e)}


@router.get("/debug/artifacts", summary="Отладка: сырые данные артефактов")
def debug_artifacts():
    """Показывает, что именно парсит бэкенд"""
    try:
        from utils.md_parser import get_all_md_files
        return get_all_md_files("/docs/artifacts")
    except Exception as e:
        return {"error": str(e)}