from fastapi import APIRouter, HTTPException
import os

router = APIRouter()

ERD_BASE_URL = "/docs/erd/"


@router.get("/", summary="Получить список SQL задач")
def get_sql_tasks(category: str = None, tag: str = None):
    try:
        from utils.md_parser import get_all_md_files
        tasks = get_all_md_files("/docs/sql-tasks")

        if category and category != "all":
            tasks = [t for t in tasks if t.get("category") == category]
        if tag:
            tag_lower = tag.lower()
            tasks = [t for t in tasks
                     if tag_lower in [t_tag.lower() for t_tag in t.get("tags", [])]]

        return [
            {
                "id": t.get("id"),
                "title": t.get("title", "Без названия"),
                "short_description": t.get("описание_задачи", ""),
                "category": t.get("category", ""),
                "tags": t.get("tags", []),
                "erd_image": ERD_BASE_URL + t.get("erd_image", "") if t.get("erd_image") else None,
            }
            for t in tasks
        ]
    except Exception as e:
        return {"error": str(e)}


@router.get("/{task_id}", summary="Получить полную SQL задачу")
def get_sql_task(task_id: str):
    try:
        from utils.md_parser import parse_md_file
        filepath = f"/docs/sql-tasks/{task_id}.md"

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Задача не найдена")

        data = parse_md_file(filepath)

        # Добавляем полный путь к ERD
        if data.get("erd_image"):
            data["erd_image_url"] = ERD_BASE_URL + data["erd_image"]

        return data
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}