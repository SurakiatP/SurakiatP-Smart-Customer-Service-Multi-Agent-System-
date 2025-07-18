"""
Load Knowledge Base Script

Loads initial data into ChromaDB and prepares the knowledge base for the AI agents.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.chroma_client import ChromaClient
from app.core.logger import get_logger, setup_logging

# Setup logging
setup_logging()
logger = get_logger(__name__)

class KnowledgeBaseLoader:
    """Knowledge base loader for ChromaDB"""
    
    def __init__(self):
        self.chroma_client = ChromaClient()
        self.data_path = Path("data/knowledge_base")
    
    async def load_products(self) -> int:
        """Load product information into ChromaDB"""
        products_file = self.data_path / "products.json"
        
        if not products_file.exists():
            logger.error(f"Products file not found: {products_file}")
            return 0
        
        try:
            with open(products_file, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
            
            loaded_count = 0
            
            for product in products_data.get("products", []):
                # Create comprehensive product description
                content = f"""
                Product: {product['name']}
                Description: {product['description']}
                Price: {product['price']}
                Features: {', '.join(product['features'])}
                Category: {product['category']}
                Popular: {'Yes' if product.get('popular', False) else 'No'}
                """
                
                # Add to ChromaDB
                await self.chroma_client.add_product(
                    content=content.strip(),
                    metadata={
                        "product_id": product['id'],
                        "name": product['name'],
                        "price": product['price'],
                        "category": product['category'],
                        "popular": product.get('popular', False)
                    },
                    doc_id=product['id']
                )
                
                loaded_count += 1
                logger.info(f"Loaded product: {product['name']}")
            
            logger.info(f"Successfully loaded {loaded_count} products")
            return loaded_count
            
        except Exception as e:
            logger.error(f"Failed to load products: {e}")
            return 0
    
    async def load_faqs(self) -> int:
        """Load FAQ data into ChromaDB"""
        faqs_file = self.data_path / "faqs.json"
        
        if not faqs_file.exists():
            logger.error(f"FAQs file not found: {faqs_file}")
            return 0
        
        try:
            with open(faqs_file, 'r', encoding='utf-8') as f:
                faqs_data = json.load(f)
            
            loaded_count = 0
            
            for faq in faqs_data.get("faqs", []):
                # Create FAQ content
                content = f"""
                Question: {faq['question']}
                Answer: {faq['answer']}
                Category: {faq['category']}
                """
                
                # Add to ChromaDB FAQs collection
                self.chroma_client.faqs_collection.add(
                    documents=[content.strip()],
                    metadatas=[{
                        "faq_id": faq['id'],
                        "question": faq['question'],
                        "category": faq['category'],
                        "popularity": faq.get('popularity', 0)
                    }],
                    ids=[faq['id']]
                )
                
                loaded_count += 1
                logger.info(f"Loaded FAQ: {faq['question'][:50]}...")
            
            logger.info(f"Successfully loaded {loaded_count} FAQs")
            return loaded_count
            
        except Exception as e:
            logger.error(f"Failed to load FAQs: {e}")
            return 0
    
    async def load_policies(self) -> int:
        """Load policy information into ChromaDB"""
        policies_file = self.data_path / "policies.json"
        
        if not policies_file.exists():
            logger.error(f"Policies file not found: {policies_file}")
            return 0
        
        try:
            with open(policies_file, 'r', encoding='utf-8') as f:
                policies_data = json.load(f)
            
            loaded_count = 0
            
            # Load refund policy
            refund_policy = policies_data.get("refund_policy", {})
            for policy_type, policy_info in refund_policy.items():
                if isinstance(policy_info, dict) and "period" in policy_info:
                    content = f"""
                    Policy Type: {policy_type.replace('_', ' ').title()}
                    Period: {policy_info['period']}
                    Conditions: {', '.join(policy_info.get('conditions', []))}
                    """
                    
                    self.chroma_client.faqs_collection.add(
                        documents=[content.strip()],
                        metadatas=[{
                            "policy_type": policy_type,
                            "category": "refund_policy",
                            "source": "policies"
                        }],
                        ids=[f"policy_{policy_type}"]
                    )
                    
                    loaded_count += 1
            
            logger.info(f"Successfully loaded {loaded_count} policies")
            return loaded_count
            
        except Exception as e:
            logger.error(f"Failed to load policies: {e}")
            return 0
    
    async def load_troubleshooting(self) -> int:
        """Load troubleshooting information into ChromaDB"""
        troubleshooting_file = self.data_path / "troubleshooting.json"
        
        if not troubleshooting_file.exists():
            logger.error(f"Troubleshooting file not found: {troubleshooting_file}")
            return 0
        
        try:
            with open(troubleshooting_file, 'r', encoding='utf-8') as f:
                troubleshooting_data = json.load(f)
            
            loaded_count = 0
            
            for issue in troubleshooting_data.get("troubleshooting", []):
                # Create troubleshooting content
                solutions = []
                for solution in issue.get("solutions", []):
                    solutions.append(f"Step {solution['step']}: {solution['action']}")
                
                content = f"""
                Issue: {issue['issue_type'].replace('_', ' ').title()}
                Common Causes: {', '.join(issue.get('common_causes', []))}
                Solutions: {'; '.join(solutions)}
                Escalation: {issue.get('escalation_criteria', 'Contact support if issue persists')}
                """
                
                self.chroma_client.faqs_collection.add(
                    documents=[content.strip()],
                    metadatas=[{
                        "issue_type": issue['issue_type'],
                        "category": "troubleshooting",
                        "source": "technical_support"
                    }],
                    ids=[f"troubleshoot_{issue['issue_type']}"]
                )
                
                loaded_count += 1
                logger.info(f"Loaded troubleshooting: {issue['issue_type']}")
            
            logger.info(f"Successfully loaded {loaded_count} troubleshooting guides")
            return loaded_count
            
        except Exception as e:
            logger.error(f"Failed to load troubleshooting: {e}")
            return 0
    
    async def load_all(self) -> Dict[str, int]:
        """Load all knowledge base data"""
        logger.info("Starting knowledge base loading...")
        
        results = {
            "products": await self.load_products(),
            "faqs": await self.load_faqs(),
            "policies": await self.load_policies(),
            "troubleshooting": await self.load_troubleshooting()
        }
        
        total = sum(results.values())
        logger.info(f"Knowledge base loading completed. Total items: {total}")
        
        return results
    
    async def verify_data(self) -> bool:
        """Verify loaded data by testing searches"""
        logger.info("Verifying loaded data...")
        
        try:
            # Test product search
            products = await self.chroma_client.search_products("premium plan", limit=1)
            if not products:
                logger.error("Product search verification failed")
                return False
            
            # Test FAQ search
            faqs = await self.chroma_client.search_faqs("refund policy", limit=1)
            if not faqs:
                logger.error("FAQ search verification failed")
                return False
            
            logger.info("Data verification successful")
            return True
            
        except Exception as e:
            logger.error(f"Data verification failed: {e}")
            return False

async def main():
    """Main function to load knowledge base"""
    print("🚀 Loading Knowledge Base...")
    print("=" * 50)
    
    loader = KnowledgeBaseLoader()
    
    # Load all data
    results = await loader.load_all()
    
    # Display results
    print("\n📊 Loading Results:")
    print("-" * 30)
    for data_type, count in results.items():
        print(f"{data_type.title()}: {count} items")
    
    total = sum(results.values())
    print(f"\nTotal: {total} items loaded")
    
    # Verify data
    print("\n🔍 Verifying data...")
    if await loader.verify_data():
        print("✅ Knowledge base loaded and verified successfully!")
    else:
        print("❌ Data verification failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)