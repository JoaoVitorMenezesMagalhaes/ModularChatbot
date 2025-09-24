"""Math Agent - handles mathematical expressions and calculations."""
import time
import re
from typing import Union
from openai import OpenAI
from models import AgentType, MathResponse, ChatMessage
from utils.logger import StructuredLogger
from utils.security import SecurityValidator
from config import Config

class MathAgent:
    """Math agent that interprets and solves mathematical expressions."""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.logger = StructuredLogger("MathAgent")
        self.security_validator = SecurityValidator()
    
    def _extract_math_expression(self, message: str) -> str:
        """Extract mathematical expression from user message."""
        # Remove common question words and phrases
        question_patterns = [
            r"how much is\s*",
            r"what is\s*",
            r"calculate\s*",
            r"compute\s*",
            r"solve\s*",
            r"what's\s*",
            r"can you\s*",
            r"please\s*",
            r"could you\s*",
            r"would you\s*"
        ]
        
        expression = message.strip()
        
        # Remove question patterns
        for pattern in question_patterns:
            expression = re.sub(pattern, "", expression, flags=re.IGNORECASE)
        
        # Remove question marks and extra whitespace
        expression = expression.rstrip("?").strip()
        
        # If the expression is just a number, return as is
        if expression.replace(".", "").replace("-", "").isdigit():
            return expression
        
        # Extract mathematical expression using regex
        math_pattern = r"[\d\+\-\*\/\(\)\.\s]+"
        matches = re.findall(math_pattern, expression)
        
        if matches:
            # Take the longest match that looks like a math expression
            math_expressions = [match.strip() for match in matches if len(match.strip()) > 1]
            if math_expressions:
                return max(math_expressions, key=len)
        
        return expression
    
    def _safe_eval(self, expression: str) -> Union[float, str]:
        """Safely evaluate mathematical expression."""
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Replace common mathematical symbols
            expression = expression.replace("×", "*").replace("÷", "/")
            
            # Validate that the expression only contains safe characters
            safe_chars = set("0123456789+-*/.() ")
            if not all(c in safe_chars for c in expression):
                return "Invalid characters in expression"
            
            # Evaluate the expression
            result = eval(expression)
            
            # Ensure result is a number
            if isinstance(result, (int, float)):
                return float(result)
            else:
                return "Invalid mathematical expression"
                
        except ZeroDivisionError:
            return "Division by zero error"
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"
    
    def _get_llm_interpretation(self, message: str, expression: str) -> str:
        """Use LLM to interpret and explain the mathematical expression."""
        try:
            prompt = f"""
            The user asked: "{message}"
            The mathematical expression extracted is: "{expression}"
            
            Please provide a clear, step-by-step explanation of how to solve this mathematical expression.
            Include the final answer and show your work.
            Be concise but thorough.
            """
            
            response = self.client.chat.completions.create(
                model=Config.MATH_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.log_error(AgentType.MATH, f"LLM interpretation failed: {str(e)}")
            return f"I can solve the expression {expression}, but I had trouble generating a detailed explanation."
    
    def solve_math_problem(self, chat_message: ChatMessage) -> MathResponse:
        """Solve mathematical problem from user message."""
        start_time = time.time()
        
        try:
            # Sanitize input message
            sanitized_message = self.security_validator.sanitize_input(chat_message.message)
            
            # Check for prompt injection
            injection_check = self.security_validator.detect_prompt_injection(sanitized_message)
            if injection_check["is_suspicious"]:
                self.logger.log_info(
                    "Prompt injection detected in math query",
                    metadata={
                        "confidence": injection_check["confidence"],
                        "patterns": injection_check["patterns_found"]
                    }
                )
                
                return MathResponse(
                    answer="Desculpe, mas sua pergunta contém instruções não permitidas. Por favor, faça uma pergunta sobre matemática ou Infinitepay.",
                    expression="",
                    result=0.0,
                    execution_time=time.time() - start_time,
                    timestamp=chat_message.timestamp,
                    user_message=chat_message.message
                )
            
            # Extract mathematical expression from sanitized message
            expression = self._extract_math_expression(sanitized_message)
            
            if not expression:
                return MathResponse(
                    answer="I couldn't find a mathematical expression in your message. Please provide a clear math problem.",
                    expression="",
                    result=0.0,
                    execution_time=time.time() - start_time,
                    timestamp=chat_message.timestamp,
                    user_message=chat_message.message
                )
            
            # Solve the expression
            result = self._safe_eval(expression)
            
            if isinstance(result, str):
                # Error occurred during evaluation
                return MathResponse(
                    answer=f"I encountered an error: {result}",
                    expression=expression,
                    result=0.0,
                    execution_time=time.time() - start_time,
                    timestamp=chat_message.timestamp,
                    user_message=chat_message.message
                )
            
            # Get LLM interpretation for better explanation
            explanation = self._get_llm_interpretation(sanitized_message, expression)
            
            # Format the answer
            answer = f"**Expression:** {expression}\n**Result:** {result}\n\n**Explanation:**\n{explanation}"
            
            execution_time = time.time() - start_time
            
            # Log execution with full observability
            self.logger.log_agent_execution(
                agent_type=AgentType.MATH,
                message=chat_message.message,
                execution_time=execution_time,
                conversation_id=chat_message.conversation_id,
                user_id=chat_message.user_id,
                processed_content=f"Expression: {expression}, Result: {result}",
                metadata={
                    "expression": expression,
                    "result": result,
                    "calculation_successful": True
                }
            )
            
            return MathResponse(
                answer=answer,
                expression=expression,
                result=result,
                execution_time=execution_time,
                timestamp=chat_message.timestamp,
                user_message=chat_message.message
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.log_error(
                AgentType.MATH, 
                f"Math problem solving failed: {str(e)}",
                conversation_id=chat_message.conversation_id,
                user_id=chat_message.user_id,
                execution_time=execution_time,
                metadata={"error_type": "math_processing_failure"}
            )
            
            return MathResponse(
                answer="Desculpe, ocorreu um erro ao processar seu problema matemático. Tente reformular sua pergunta.",
                expression="",
                result=0.0,
                execution_time=execution_time,
                timestamp=chat_message.timestamp,
                user_message=chat_message.message
            )
