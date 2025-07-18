class CustomerServiceAIException(Exception):
    """Base exception for the application"""
    pass

class AgentProcessingError(CustomerServiceAIException):
    """Error during agent processing"""
    pass

class DatabaseConnectionError(CustomerServiceAIException):
    """Database connection error"""
    pass

class HuggingFaceAPIError(CustomerServiceAIException):
    """Hugging Face API error"""
    pass

class InvalidInputError(CustomerServiceAIException):
    """Invalid user input error"""
    pass