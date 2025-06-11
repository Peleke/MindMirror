import strawberry
import uvicorn
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from src.engine import CoachingEngine
from typing import Optional
import os
import base64

# Initialize the engine globally
print("Initializing CoachingEngine...")
engine = CoachingEngine()
print("CoachingEngine initialized.")

@strawberry.type
class PerformanceReview:
    key_success: str
    improvement_area: str
    journal_prompt: str

@strawberry.type
class Query:
    @strawberry.field
    def ask(self, query: str) -> str:
        """Answers a question using the underlying RAG chain."""
        return engine.ask(query)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def generate_review(self, user_id: str) -> PerformanceReview:
        """
        Generates a bi-weekly performance review for a user.
        Currently returns a static mock response.
        """
        # In a real application, this would fetch user data
        # and use a structured prompt with the engine.
        print(f"Generating review for user: {user_id}")
        return PerformanceReview(
            key_success="You consistently met your protein goals this week, which is fantastic for muscle recovery.",
            improvement_area="Your sleep duration was a bit lower than average on workout days. Let's focus on winding down earlier.",
            journal_prompt="Reflect on a moment this week where you felt most energized. What were the circumstances?"
        )

    @strawberry.mutation
    def upload_document(self, file_name: str, content: strawberry.scalars.Base64) -> bool:
        """
        Uploads a new document to the knowledge base.
        The content should be a Base64 encoded string.
        """
        try:
            # Ensure the PDF directory exists
            os.makedirs(engine.pdf_dir, exist_ok=True)
            
            file_path = os.path.join(engine.pdf_dir, file_name)
            
            # Decode the Base64 content
            file_content = base64.b64decode(content)

            with open(file_path, "wb") as f:
                f.write(file_content)

            print(f"Document '{file_name}' uploaded. Reloading engine...")
            engine.reload()
            print("Engine reloaded.")
            return True
        except Exception as e:
            print(f"Error uploading document: {e}")
            return False

schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema, graphiql=True)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 