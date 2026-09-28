"""
Export OpenAPI JSON schema from FastAPI application.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.main import app

openapi_schema = app.openapi()

output_path = os.path.join(os.path.dirname(__file__), "openapi.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(openapi_schema, f, indent=2)

print(f"OpenAPI schema successfully written to {output_path}")
