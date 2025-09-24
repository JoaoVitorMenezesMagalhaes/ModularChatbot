"""Security middleware for FastAPI application."""
import time
from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from utils.security import SecurityValidator
from utils.logger import StructuredLogger

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for input validation and rate limiting."""
    
    def __init__(self, app, rate_limit_per_minute: int = 60):
        super().__init__(app)
        self.security_validator = SecurityValidator()
        self.logger = StructuredLogger("SecurityMiddleware")
        self.rate_limit_per_minute = rate_limit_per_minute
        self.request_counts: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security checks."""
        start_time = time.time()
        
        try:
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Rate limiting check
            if not self._check_rate_limit(client_ip):
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": self.security_validator.get_safe_error_message("rate_limit")
                    }
                )
            
            # Security headers
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            # Log request
            processing_time = time.time() - start_time
            self.logger.log_info(
                f"Request processed: {request.method} {request.url.path}",
                metadata={
                    "client_ip": client_ip,
                    "processing_time": processing_time,
                    "status_code": response.status_code
                }
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.log_error(
                None,
                f"Security middleware error: {str(e)}",
                metadata={"client_ip": client_ip}
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": self.security_validator.get_safe_error_message("general")
                }
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limit."""
        current_time = time.time()
        minute_window = int(current_time // 60)
        
        # Clean old entries
        self.request_counts = {
            ip: data for ip, data in self.request_counts.items()
            if data.get("minute_window", 0) >= minute_window - 1
        }
        
        # Get or create client data
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {
                "count": 0,
                "minute_window": minute_window
            }
        
        client_data = self.request_counts[client_ip]
        
        # Reset count if new minute
        if client_data["minute_window"] != minute_window:
            client_data["count"] = 0
            client_data["minute_window"] = minute_window
        
        # Check rate limit
        if client_data["count"] >= self.rate_limit_per_minute:
            self.logger.log_info(
                "Rate limit exceeded",
                metadata={
                    "client_ip": client_ip,
                    "count": client_data["count"],
                    "limit": self.rate_limit_per_minute
                }
            )
            return False
        
        # Increment count
        client_data["count"] += 1
        return True

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for input validation and sanitization."""
    
    def __init__(self, app):
        super().__init__(app)
        self.security_validator = SecurityValidator()
        self.logger = StructuredLogger("InputValidationMiddleware")
    
    async def dispatch(self, request: Request, call_next):
        """Validate and sanitize input data."""
        try:
            # Only validate POST requests to chat endpoints
            if request.method == "POST" and request.url.path.startswith("/chat"):
                # Get request body
                body = await request.body()
                
                if body:
                    # Parse JSON
                    import json
                    try:
                        data = json.loads(body.decode())
                        
                        # Validate and sanitize message
                        if "message" in data:
                            original_message = data["message"]
                            
                            # Check for prompt injection
                            injection_check = self.security_validator.detect_prompt_injection(original_message)
                            if injection_check["is_suspicious"]:
                                self.logger.log_info(
                                    "Prompt injection attempt blocked",
                                    metadata={
                                        "client_ip": self._get_client_ip(request),
                                        "confidence": injection_check["confidence"],
                                        "patterns": injection_check["patterns_found"]
                                    }
                                )
                                
                                return JSONResponse(
                                    status_code=400,
                                    content={
                                        "error": "Invalid input",
                                        "message": self.security_validator.get_safe_error_message("prompt_injection")
                                    }
                                )
                            
                            # Validate message length
                            if not self.security_validator.validate_message_length(original_message):
                                return JSONResponse(
                                    status_code=400,
                                    content={
                                        "error": "Message too long",
                                        "message": "A mensagem é muito longa. Por favor, encurte sua pergunta."
                                    }
                                )
                            
                            # Sanitize message
                            sanitized_message = self.security_validator.sanitize_input(original_message)
                            data["message"] = sanitized_message
                            
                            # Validate user_id if present
                            if "user_id" in data and not self.security_validator.validate_user_id(data["user_id"]):
                                return JSONResponse(
                                    status_code=400,
                                    content={
                                        "error": "Invalid user ID",
                                        "message": "ID de usuário inválido."
                                    }
                                )
                            
                            # Validate conversation_id if present
                            if "conversation_id" in data and not self.security_validator.validate_conversation_id(data["conversation_id"]):
                                return JSONResponse(
                                    status_code=400,
                                    content={
                                        "error": "Invalid conversation ID",
                                        "message": "ID de conversa inválido."
                                    }
                                )
                            
                            # Create new request with sanitized data
                            new_body = json.dumps(data).encode()
                            
                            # Replace request body
                            async def receive():
                                return {"type": "http.request", "body": new_body}
                            
                            request._receive = receive
                    
                    except json.JSONDecodeError:
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "Invalid JSON",
                                "message": "Formato JSON inválido."
                            }
                        )
            
            # Process request
            response = await call_next(request)
            return response
            
        except Exception as e:
            self.logger.log_error(
                None,
                f"Input validation error: {str(e)}",
                metadata={"client_ip": self._get_client_ip(request)}
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": self.security_validator.get_safe_error_message("general")
                }
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
