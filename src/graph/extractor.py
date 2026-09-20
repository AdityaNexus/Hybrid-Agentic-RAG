import json 

from src.generation.llm import generate 
from src.graph.models import GraphExtraction

SYSTEM_PROMPT = """
You are an information extraction system.

Extract entities and relationships ONLY from the provided text.

Rules:
- Do not use outside knowledge.
- Do not infer facts that are not explicitly stated.
- Every relationship must be directly supported by the text.
- Use short, canonical entity names.
- Return ONLY valid JSON.
"""

def extract_graph(text : str)->GraphExtraction:
    prompt = f"""
Extract entities and relationships from this text.

Return exactly this JSON structure:

{{
  "entities": [
    {{
      "name": "entity name",
      "entity_type": "PERSON | ORGANIZATION | LOCATION | PRODUCT | CONCEPT | DATE | OTHER"
    }}
  ],
  "relationships": [
    {{
      "source": "source entity",
      "relationship": "relationship",
      "target": "target entity"
    }}
  ]
}}

TEXT:
{text}
"""

    response = generate(
        prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.0,
        max_tokens = 512,
    )

    try:
        data  = json.loads(response)
        return GraphExtraction.model_validate(data)
    except (json.JSONDecodeError,ValueError):
        return GraphExtraction()