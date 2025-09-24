"""Secure error handling utilities."""
import traceback
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from models import AgentType
from utils.logger import StructuredLogger
from utils.security import SecurityValidator

class SecureErrorHandler:
    """Secure error handler that never exposes raw exceptions to clients."""
    
    def __init__(self):
        self.logger = StructuredLogger("SecureErrorHandler")
        self.security_validator = SecurityValidator()
        
        # Error type mappings for better error messages
        self.error_type_mappings = {
            "ValidationError": "validation",
            "ValueError": "validation",
            "TypeError": "validation",
            "KeyError": "validation",
            "AttributeError": "general",
            "ConnectionError": "service_unavailable",
            "TimeoutError": "timeout",
            "PermissionError": "authorization",
            "FileNotFoundError": "not_found",
            "MemoryError": "service_unavailable",
            "RecursionError": "service_unavailable",
        }
    
    def get_error_type(self, exception: Exception) -> str:
        """Determine error type from exception."""
        exception_name = type(exception).__name__
        return self.error_type_mappings.get(exception_name, "general")
    
    def log_error_safely(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with full details for debugging without exposing to client."""
        error_id = f"ERR_{int(time.time() * 1000)}"
        
        # Extract context information
        conversation_id = context.get("conversation_id") if context else None
        user_id = context.get("user_id") if context else None
        execution_time = context.get("execution_time") if context else None
        
        self.logger.log_error(
            AgentType.KNOWLEDGE,  # Default agent type for errors
            f"Error {error_id}: {str(exception)}",
            conversation_id=conversation_id,
            user_id=user_id,
            execution_time=execution_time,
            metadata={
                "error_id": error_id,
                "error_type": type(exception).__name__,
                "error_message": str(exception),
                "traceback": traceback.format_exc(),
                "context": context or {}
            }
        )
        
        return error_id
    
    def create_error_response(self, exception: Exception, context: Optional[Dict[str, Any]] = None) -> JSONResponse:
        """Create a safe error response without exposing system details."""
        error_id = self.log_error_safely(exception, context)
        error_type = self.get_error_type(exception)
        
        # Get safe error message
        safe_message = self.security_validator.get_safe_error_message(error_type)
        
        # Create response
        response_data = {
            "error": "An error occurred",
            "message": safe_message,
            "error_id": error_id,
            "timestamp": time.time()
        }
        
        # Determine appropriate status code
        status_code = self._get_status_code(exception, error_type)
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    def _get_status_code(self, exception: Exception, error_type: str) -> int:
        """Determine appropriate HTTP status code."""
        if isinstance(exception, HTTPException):
            return exception.status_code
        
        status_codes = {
            "validation": 400,
            "authorization": 403,
            "not_found": 404,
            "timeout": 408,
            "rate_limit": 429,
            "service_unavailable": 503,
            "general": 500
        }
        
        return status_codes.get(error_type, 500)
    
    def handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions securely."""
        error_id = self.log_error_safely(exc, {"path": request.url.path, "method": request.method})
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Request error",
                "message": self.security_validator.get_safe_error_message("general"),
                "error_id": error_id
            }
        )
    
    def handle_validation_error(self, request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors securely."""
        error_id = self.log_error_safely(exc, {"path": request.url.path, "method": request.method})
        
        return JSONResponse(
            status_code=400,
            content={
                "error": "Validation error",
                "message": self.security_validator.get_safe_error_message("validation"),
                "error_id": error_id
            }
        )
    
    def handle_general_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions securely."""
        return self.create_error_response(exc, {
            "path": request.url.path,
            "method": request.method,
            "client_ip": self._get_client_ip(request)
        })
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address safely."""
        try:
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
            
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip
            
            return request.client.host if request.client else "unknown"
        except Exception:
            return "unknown"

# Global error handler instance
error_handler = SecureErrorHandler()

# Import time for error IDs
import time
