from contextlib import asynccontextmanager
import os
import warnings
import logging
import time
from typing import Dict, Any
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from langchain_core._api import LangChainBetaWarning
from langserve import add_routes

from app.agent import graph as agent_graph
from app.db import db_pool

# Load environment variables
load_dotenv()

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress LangChain warnings
warnings.filterwarnings("ignore", category=LangChainBetaWarning)

logger.info(f"Graph imported successfully: {type(agent_graph)}")


def init_db():
    if db_pool is None:
        return
    with db_pool.connection() as conn:  # type: ignore[union-attr]
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback_analysis (
                    id SERIAL PRIMARY KEY,
                    feedback TEXT NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    entities TEXT,
                    summary TEXT,
                    sentiment VARCHAR(20),
                    priority VARCHAR(20),
                    route VARCHAR(50),
                    action_items TEXT,
                    trend_analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS analysis_summaries (
                    id SERIAL PRIMARY KEY,
                    summary_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

# Pydantic models for request validation
class FeedbackRequest(BaseModel):
    feedback: str
    
    model_config = {
        "str_strip_whitespace": True,
        "str_min_length": 1,
        "str_max_length": 10000
    }

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    environment: str

app = FastAPI(
    title="Customer Feedback Analysis API",
    description="AI-powered customer feedback analysis service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT", "development") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT", "development") == "development" else None
)

# Security middleware - only allow specific hosts in production
if os.getenv("ENVIRONMENT") == "production":
    trusted_hosts = os.getenv("TRUSTED_HOSTS", "localhost").split(",")
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=[host.strip() for host in trusted_hosts]
    )

# Configure CORS for frontend deployments
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_env.strip() == "*":
    allowed_origins = ["*"]
    if os.getenv("ENVIRONMENT") == "production":
        logger.warning("CORS set to allow all origins in production - this should be restricted")
else:
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
    logger.info(f"CORS configured for origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

# Global exception handler
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"Validation error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": "error", "message": "Invalid input data", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "Internal server error"}
    )

@app.get("/", response_model=Dict[str, Any])
async def index():
    """Root endpoint with API information"""
    return {
        "status": "ok",
        "service": "Customer Feedback Analysis API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "demo_mode": os.getenv("DEMO_MODE", "false").lower() == "true",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "docs": "/docs" if os.getenv("ENVIRONMENT", "development") == "development" else "disabled",
            "langserve": {
                "invoke": "/invoke",
                "stream": "/stream",
                "input_schema": "/input_schema",
                "output_schema": "/output_schema",
                "playground": "/playground"
            }
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with system information"""
    try:
        # Test database connection if configured
        db_status = "not_configured"
        if db_pool is not None:
            try:
                with db_pool.connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                        db_status = "healthy"
            except Exception as e:
                logger.error(f"Database health check failed: {e}")
                db_status = "unhealthy"
        
        return HealthResponse(
            status="healthy",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            version="1.0.0",
            environment=os.getenv("ENVIRONMENT", "development")
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

@app.post("/analyze")
async def analyze_feedback(request: FeedbackRequest):
    """Analyze customer feedback and return insights"""
    try:
        feedback = request.feedback.strip()
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback text cannot be empty"
            )
        
        if len(feedback) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback text too long (max 10,000 characters)"
            )
        
        logger.info(f"Analyzing feedback (length: {len(feedback)})")
        
        # Check if demo mode is enabled (when no OpenAI key or quota exceeded)
        demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"  # Default to demo mode
        
        if demo_mode:
            logger.info("Running in demo mode - using mock responses")
            
            # Generate smart mock responses based on feedback content
            feedback_lower = feedback.lower()
            
            # Determine category
            if any(word in feedback_lower for word in ["hate", "terrible", "awful", "worst", "complaint", "problem", "issue", "broken"]):
                category = "Complaint"
                sentiment = "Negative"
                priority = "High"
                route = "Customer Service Team"
                action_items = [
                    "Contact customer within 24 hours to address concerns",
                    "Investigate reported issues and provide solutions",
                    "Follow up to ensure customer satisfaction"
                ]
            elif any(word in feedback_lower for word in ["love", "amazing", "excellent", "great", "fantastic", "wonderful", "praise"]):
                category = "Praise"
                sentiment = "Positive"
                priority = "Medium"
                route = "HR/Employee Recognition"
                action_items = [
                    "Share positive feedback with relevant team members",
                    "Consider featuring this feedback in marketing materials",
                    "Recognize employees mentioned in the feedback"
                ]
            elif any(word in feedback_lower for word in ["suggest", "could", "should", "improve", "idea", "recommendation"]):
                category = "Suggestion"
                sentiment = "Neutral"
                priority = "Medium"
                route = "Product Development"
                action_items = [
                    "Review suggestion with product development team",
                    "Assess feasibility of implementing suggested improvements",
                    "Consider including in product roadmap"
                ]
            else:
                category = "Query"
                sentiment = "Neutral"
                priority = "Low"
                route = "FAQ/Knowledge Base Update"
                action_items = [
                    "Provide detailed response to customer query",
                    "Update FAQ if this is a common question",
                    "Ensure knowledge base has relevant information"
                ]
            
            # Extract mock entities (simple keyword extraction)
            entities = []
            entity_keywords = ["product", "service", "staff", "website", "app", "delivery", "quality", "price", "support"]
            for keyword in entity_keywords:
                if keyword in feedback_lower:
                    entities.append(keyword)
            
            if not entities:
                entities = ["general feedback"]
            
            return {
                "status": "success",
                "result": {
                    "feedback": feedback,
                    "category": category,
                    "entities": entities,
                    "summary": f"Customer provided {sentiment.lower()} feedback regarding {', '.join(entities)}",
                    "sentiment": sentiment,
                    "priority": priority,
                    "route": route,
                    "action_items": action_items,
                    "trend_analysis": f"{sentiment} customer sentiment in {category.lower()} category"
                }
            }
        
        # Production mode - use LangGraph
        try:
            from app.state import State
            
            # Create initial state using the State class
            initial_state = State(feedback=feedback)
            logger.info("Created initial state for LangGraph")
            
            # Run the graph with timeout
            logger.info("Invoking LangGraph...")
            result = agent_graph.invoke(initial_state)
            logger.info("Graph execution completed successfully")
            
            # Convert result to dict for JSON response
            if hasattr(result, '__dict__'):
                result_dict = result.__dict__
            else:
                result_dict = result
                
            return {"status": "success", "result": result_dict}
            
        except Exception as graph_error:
            logger.error(f"LangGraph execution failed: {graph_error}", exc_info=True)
            # Fallback to mock response if LangGraph fails
            logger.warning("Falling back to demo mode due to LangGraph error")
            return {
                "status": "success",
                "result": {
                    "feedback": feedback,
                    "category": "Query",
                    "entities": ["general feedback"],
                    "summary": "Customer feedback processed with fallback analysis",
                    "sentiment": "Neutral",
                    "priority": "Medium",
                    "route": "General Support",
                    "action_items": ["Review customer feedback manually"],
                    "trend_analysis": "Fallback analysis due to system limitations"
                },
                "note": "Processed with fallback analysis"
            }
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process feedback analysis"
        )
# Configure LangServe routes (optional, disabled in production by default)
if os.getenv("ENABLE_LANGSERVE", "false").lower() == "true":
    logger.info("Adding LangServe routes...")
    try:
        # Add routes with proper configuration for LangGraph
        add_routes(
            app,
            agent_graph,
            path="/langserve",
            enable_feedback_endpoint=True,
            enable_public_trace_link_endpoint=False,  # Disable for security
            playground_type="default" if os.getenv("ENVIRONMENT") != "production" else None
        )
        logger.info("LangServe routes added successfully!")
        
        # Add a simple test endpoint to verify the graph works
        @app.post("/test-graph")
        async def test_graph_endpoint(request: FeedbackRequest):
            """Test endpoint for LangGraph (development only)"""
            if os.getenv("ENVIRONMENT") == "production":
                raise HTTPException(status_code=404, detail="Not found")
            
            try:
                from app.state import State
                initial_state = State(feedback=request.feedback)
                result = agent_graph.invoke(initial_state)
                return {"status": "success", "result": result}
            except Exception as e:
                logger.error(f"Test graph error: {e}", exc_info=True)
                return {"status": "error", "error": str(e)}
                
    except Exception as e:
        logger.error(f"Error adding LangServe routes: {e}", exc_info=True)
else:
    logger.info("LangServe routes disabled (set ENABLE_LANGSERVE=true to enable)")

# Add startup event logging
@app.on_event("startup")
async def startup_event():
    logger.info("Customer Feedback Analysis API starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Demo mode: {os.getenv('DEMO_MODE', 'false')}")
    logger.info(f"Database configured: {'Yes' if db_pool else 'No'}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Customer Feedback Analysis API shutting down...")