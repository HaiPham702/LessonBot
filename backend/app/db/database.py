import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

db = Database()

async def get_database() -> AsyncIOMotorDatabase:
    return db.database

async def connect_to_db():
    """Create database connection"""
    logger.info("Connecting to MongoDB...")
    try:
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=10,
        )
        db.database = db.client[settings.DATABASE_NAME]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.DATABASE_NAME}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_db_connection():
    """Close database connection"""
    logger.info("Closing connection to MongoDB...")
    if db.client:
        db.client.close()

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Chat sessions indexes
        await db.database.chat_sessions.create_index("user_id")
        await db.database.chat_sessions.create_index("created_at")
        
        # Chat messages indexes
        await db.database.chat_messages.create_index([("session_id", 1), ("created_at", 1)])
        
        # Lectures indexes
        await db.database.lectures.create_index("user_id")
        await db.database.lectures.create_index("subject")
        await db.database.lectures.create_index("created_at")
        
        # Slides indexes
        await db.database.slides.create_index("user_id")
        await db.database.slides.create_index("subject")
        await db.database.slides.create_index("created_at")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
