from pydantic import BaseModel, Field 

class ExtractedEntity(BaseModel):
    name : str 
    entity_type : str 

class ExtractedRelationship(BaseModel):
    source : str 
    relationship : str 
    target : str 
    
class GraphExtraction(BaseModel):
    entities : list[ExtractedEntity] = Field(default_factory=list )
    relationships : list[ExtractedRelationship] = Field(default_factory=list )