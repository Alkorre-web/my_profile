from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import psycopg2
from routers import main_page, sql_tasks

# 1. Подключение к MongoDB (используем имя сервиса 'mongo' из docker-compose)
try:
    mongo_client = MongoClient("mongodb://mongo:27017/", serverSelectionTimeoutMS=2000)
    mongo_client.admin.command('ping')  # Тестовый пинг
    mongo_db = mongo_client["portfolio_db"]
    print("✅ MongoDB подключена успешно")
except Exception as e:
    print(f"❌ Ошибка подключения к MongoDB: {e}")
    mongo_db = None

# 2. Подключение к PostgreSQL (используем имя сервиса 'postgres' из docker-compose)
try:
    pg_conn = psycopg2.connect(
        host="postgres",
        port="5432",
        dbname="portfolio",
        user="user",
        password="pass"
    )
    print("✅ PostgreSQL подключен успешно")
except Exception as e:
    print(f"❌ Ошибка подключения к PostgreSQL: {e}")
    pg_conn = None

# 3. Передаем подключения в роутеры
main_page.mongo_db = mongo_db
main_page.pg_conn = pg_conn

sql_tasks.mongo_db = mongo_db
sql_tasks.pg_conn = pg_conn

# 4. Настройка FastAPI
app = FastAPI(title="Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Подключаем роутеры
app.include_router(main_page.router, prefix="/api/v1/main", tags=["Главная"])
app.include_router(sql_tasks.router, prefix="/api/v1/sql", tags=["SQL Задачи"])

# 6. Тестовый эндпоинт для проверки
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "mongo_connected": mongo_db is not None,
        "postgres_connected": pg_conn is not None
    }

@app.get("/debug-db")
def debug_db():
    try:
        # Проверяем, какие коллекции видит API
        collections = mongo_db.list_collection_names()

        # Пытаемся взять 1 любой документ из artifacts
        sample_artifact = list(mongo_db.artifacts.find().limit(1))
        sample_sql = list(mongo_db.sql_tasks.find().limit(1))

        return {
            "db_name": mongo_db.name,
            "collections_found": collections,
            "sample_artifact": str(sample_artifact),
            "sample_sql": str(sample_sql)
        }
    except Exception as e:
        return {"error": str(e)}