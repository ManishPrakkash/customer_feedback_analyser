from contextlib import asynccontextmanager
import os
import warnings
from dotenv import load_dotenv

from fastapi import FastAPI
from langchain_core._api import LangChainBetaWarning
from langserve import add_routes

from app.agent import graph as agent_graph
from app.db import db_pool

load_dotenv()

warnings.filterwarnings("ignore", category=LangChainBetaWarning)

print(f"Graph imported successfully: {agent_graph}")
print(f"Graph type: {type(agent_graph)}")


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

app = FastAPI(
        title="Agent Service v2",
        version="Text Analyis Pipeline Agent",
        lifespan=lifespan
    )

@app.get("/")
async def index():
    return {
        "status": "ok",
        "message": "Customer Feedback Analysis service",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "docs": "/docs",
            "langserve": {
                "invoke": "/invoke",
                "stream": "/stream",
                "input_schema": "/input_schema",
                "output_schema": "/output_schema",
                "playground": "/playground"
            }
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_feedback(request: dict):
    """Direct endpoint to analyze feedback without LangServe"""
    try:
        feedback = request.get("feedback", "")
        if not feedback:
            return {"error": "No feedback provided"}
        
        print(f"Analyzing feedback: {feedback}")
        
        # Check if demo mode is enabled (when no OpenAI key or quota exceeded)
        demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"  # Default to demo mode
        
        if demo_mode:
            print("Running in demo mode - using mock responses")
            
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
        
        # Import State here to avoid circular imports
        from app.state import State
        
        # Create initial state using the State class
        initial_state = State(feedback=feedback)
        print(f"Created initial state: {initial_state}")
        
        # Run the graph with the State object
        print("Invoking graph...")
        result = agent_graph.invoke(initial_state)
        print(f"Graph result: {result}")
        
        # Convert result to dict for JSON response
        if hasattr(result, '__dict__'):
            result_dict = result.__dict__
        else:
            result_dict = result
            
        return {"status": "success", "result": result_dict}
        
    except Exception as e:
        print(f"Analysis error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {"status": "error", "error": str(e)}

print("Adding LangServe routes...")
try:
    # Import the runnable directly
    from app.agent import graph as agent_graph
    
    # Add routes with proper configuration for LangGraph
    add_routes(
        app,
        agent_graph,
        path="/",
        enable_feedback_endpoint=True,
        enable_public_trace_link_endpoint=True,
        playground_type="default"
    )
    print("LangServe routes added successfully!")
    
    # Add a simple test endpoint to verify the graph works
    @app.post("/test-graph")
    async def test_graph_endpoint(request: dict):
        try:
            result = agent_graph.invoke(request)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
            
except Exception as e:
    print(f"Error adding LangServe routes: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")
    import traceback
    traceback.print_exc()