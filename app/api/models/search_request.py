from enum import Enum
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator

class SearchParams(BaseModel):
    skills: Optional[List[str]] = Field(default_factory=list)
    jobRole: Optional[List[str]] = Field(default_factory=list)
    jobTitle: Optional[List[str]] = Field(default_factory=list)
    location: Optional[List[str]] = Field(default_factory=list)
    experienceMin: Optional[int] = Field(None, ge=0)
    experienceMax: Optional[int] = Field(None, ge=0)
    expectedSalaryMin: Optional[int] = Field(None, ge=0)
    expectedSalaryMax: Optional[int] = Field(None, ge=0)

    @field_validator("skills", "jobRole", "jobTitle", "location", mode="before")
    def normalize_strings(cls, v):
        if not v:
            return v
        return [str(item).strip().lower() for item in v if isinstance(item, str)]

    @field_validator("skills", "jobRole", "jobTitle", "location", mode="before")
    def no_empty_strings(cls, v):
        if isinstance(v, list) and any(not item.strip() for item in v):
            raise ValueError("Empty strings are not allowed")
        return v
    
    @model_validator(mode="after")
    def validate_ranges_and_filters(self):
        if self.experienceMin is not None and self.experienceMax is not None:
            if self.experienceMin > self.experienceMax:
                raise ValueError("experienceMin cannot be greater than experienceMax")
        if self.expectedSalaryMin is not None and self.expectedSalaryMax is not None:
            if self.expectedSalaryMin > self.expectedSalaryMax:
                raise ValueError("expectedSalaryMin cannot be greater than expectedSalaryMax")

        if not any([
            self.skills, self.jobRole, self.jobTitle, self.location
        ]):
            raise ValueError("At least one search filter must be provided")

        return self

class SearchType(Enum):
    lexical = "lexical"
    semantic = "semantic"
    both = "both"   

class SearchRequest(BaseModel):
    searchType: Optional[SearchType]= SearchType.both 
    searchParams: SearchParams
