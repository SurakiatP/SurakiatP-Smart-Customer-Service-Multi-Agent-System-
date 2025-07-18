"""
Deployment Script

Automated deployment script for the Customer Service AI system.
"""

import subprocess
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
import docker
import yaml

class DeploymentManager:
    """Deployment manager for Customer Service AI"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.docker_client = None
        
        # Try to connect to Docker
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            print(f"⚠️  Docker not available: {e}")
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}")
        
        # Check Docker
        if not self.docker_client:
            print("❌ Docker not available")
            return False
        print("✅ Docker available")
        
        # Check required files
        required_files = [
            "requirements.txt",
            "Dockerfile",
            "docker-compose.yml",
            "app/main.py"
        ]
        
        for file in required_files:
            if not (self.project_root / file).exists():
                print(f"❌ Missing file: {file}")
                return False
        print("✅ All required files present")
        
        return True
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        print("📦 Installing dependencies...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, cwd=self.project_root)
            
            print("✅ Dependencies installed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def setup_environment(self) -> bool:
        """Setup environment variables"""
        print("🔧 Setting up environment...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if not env_file.exists() and env_example.exists():
            # Copy example to .env
            with open(env_example, 'r') as src:
                with open(env_file, 'w') as dst:
                    dst.write(src.read())
            print("✅ Created .env from .env.example")
        
        # Create logs directory
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        print("✅ Created logs directory")
        
        # Create data directories
        data_dirs = [
            "data/chroma_db",
            "data/analytics",
            "data/knowledge_base"
        ]
        
        for dir_path in data_dirs:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
        
        print("✅ Environment setup complete")
        return True
    
    def build_docker_image(self) -> bool:
        """Build Docker image"""
        print("🐳 Building Docker image...")
        
        try:
            image, build_logs = self.docker_client.images.build(
                path=str(self.project_root),
                tag="customer-service-ai:latest",
                rm=True
            )
            
            print("✅ Docker image built successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to build Docker image: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run test suite"""
        print("🧪 Running tests...")
        
        try:
            # Run unit tests
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/unit_tests/",
                "-v", "--tb=short"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Unit tests passed")
            else:
                print(f"❌ Unit tests failed:\n{result.stdout}")
                return False
            
            # Run basic integration tests
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/integration_tests/test_workflow.py",
                "-v", "--tb=short"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Integration tests passed")
            else:
                print(f"⚠️  Integration tests failed (non-critical):\n{result.stdout}")
            
            return True
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False
    
    def deploy_development(self) -> bool:
        """Deploy to development environment"""
        print("🚀 Deploying to development...")
        
        try:
            # Start services with docker-compose
            subprocess.run([
                "docker-compose", "up", "-d", "--build"
            ], check=True, cwd=self.project_root)
            
            # Wait for services to be ready
            print("⏳ Waiting for services to start...")
            time.sleep(10)
            
            # Check service health
            if self.check_service_health():
                print("✅ Development deployment successful")
                return True
            else:
                print("❌ Service health check failed")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Development deployment failed: {e}")
            return False
    
    def deploy_production(self) -> bool:
        """Deploy to production environment"""
        print("🚀 Deploying to production...")
        
        # Production deployment would include:
        # - Environment variable validation
        # - Database migrations
        # - Load balancer configuration
        # - Monitoring setup
        # - Backup procedures
        
        print("⚠️  Production deployment not implemented yet")
        print("📋 Production deployment checklist:")
        print("   - Set up environment variables")
        print("   - Configure database persistence")
        print("   - Set up monitoring and logging")
        print("   - Configure SSL/TLS")
        print("   - Set up backup procedures")
        
        return False
    
    def check_service_health(self) -> bool:
        """Check if deployed services are healthy"""
        print("🏥 Checking service health...")
        
        try:
            import requests
            
            # Check API health
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("✅ API service healthy")
            else:
                print(f"❌ API service unhealthy: {response.status_code}")
                return False
            
            # Check frontend (if accessible)
            try:
                response = requests.get("http://localhost:8501", timeout=5)
                if response.status_code == 200:
                    print("✅ Frontend service healthy")
                else:
                    print("⚠️  Frontend service may be starting...")
            except:
                print("⚠️  Frontend service not accessible (may be starting)")
            
            return True
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def show_deployment_info(self):
        """Show deployment information"""
        print("\n🎉 Deployment Complete!")
        print("=" * 40)
        print("📍 Service URLs:")
        print("   API:      http://localhost:8000")
        print("   Frontend: http://localhost:8501")
        print("   Docs:     http://localhost:8000/docs")
        print("   Health:   http://localhost:8000/health")
        print("\n🔧 Management Commands:")
        print("   Stop:     docker-compose down")
        print("   Logs:     docker-compose logs -f")
        print("   Restart:  docker-compose restart")

def main():
    """Main deployment function"""
    print("🚀 Customer Service AI Deployment")
    print("=" * 50)
    
    # Parse arguments
    environment = "development"
    if len(sys.argv) > 1:
        environment = sys.argv[1]
    
    # Initialize deployment manager
    deployer = DeploymentManager(environment)
    
    # Deployment steps
    steps = [
        ("Check Prerequisites", deployer.check_prerequisites),
        ("Install Dependencies", deployer.install_dependencies),
        ("Setup Environment", deployer.setup_environment),
        ("Build Docker Image", deployer.build_docker_image),
        ("Run Tests", deployer.run_tests),
    ]
    
    # Add environment-specific deployment
    if environment == "development":
        steps.append(("Deploy Development", deployer.deploy_development))
    elif environment == "production":
        steps.append(("Deploy Production", deployer.deploy_production))
    
    # Execute steps
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} failed!")
            return 1
    
    # Show deployment info
    if environment == "development":
        deployer.show_deployment_info()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)