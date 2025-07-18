import asyncio
import json
from pathlib import Path
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.chroma_client import ChromaClient
from app.core.logger import get_logger

logger = get_logger(__name__)

async def setup_databases():
    """Initialize all databases with sample data"""
    
    logger.info("Setting up databases...")
    
    # Initialize ChromaDB
    chroma_client = ChromaClient()
    
    # Load and index products
    products_file = Path("data/knowledge_base/products.json")
    if products_file.exists():
        with open(products_file) as f:
            products_data = json.load(f)
        
        for product in products_data["products"]:
            content = f"""
            Product: {product['name']}
            Description: {product['description']}
            Price: {product['price']}
            Features: {', '.join(product['features'])}
            Category: {product['category']}
            """
            
            await chroma_client.add_product(
                content=content,
                metadata=product,
                doc_id=product['id']
            )
        
        logger.info(f"Loaded {len(products_data['products'])} products")
    
    # Load and index FAQs
    faqs_file = Path("data/knowledge_base/faqs.json")
    if faqs_file.exists():
        with open(faqs_file) as f:
            faqs_data = json.load(f)
        
        # Add FAQs to ChromaDB (similar process)
        logger.info(f"Loaded {len(faqs_data['faqs'])} FAQs")
    
    logger.info("Database setup completed!")

if __name__ == "__main__":
    asyncio.run(setup_databases())