from typing import List, Optional
from pydantic import BaseModel, Field

class ExecutorInfo(BaseModel):
    name: Optional[str] = Field(None, description="Full name of appointed executor")
    relationship: Optional[str] = Field(None, description="Relationship of executor to principal (e.g., brother, spouse, friend)")

class GiftItem(BaseModel):
    item: str = Field(..., description="Description of the item or asset being gifted")
    recipient: str = Field(..., description="Name of the person or entity receiving the gift")

class PersonalWishesState(BaseModel):
    """
    Explicit structured state schema for the Personal Wishes Document.
    This serves as the single source of truth, independent of conversation history.
    Unknown or unconfirmed fields are explicitly represented as None.
    """
    full_name: Optional[str] = Field(None, description="Full legal name of the person creating the document")
    home_address: Optional[str] = Field(None, description="Full primary residential address")
    covers_worldwide_assets: Optional[bool] = Field(None, description="Whether the document covers worldwide assets (True) or only domestic assets (False)")
    has_children: Optional[bool] = Field(None, description="Whether the person has any children")
    children: Optional[List[str]] = Field(None, description="Names of children if applicable")
    executor: Optional[ExecutorInfo] = Field(None, description="Appointed executor details")
    specific_gifts: Optional[List[GiftItem]] = Field(default_factory=list, description="List of specific gifts or bequests to designated recipients")
    additional_wishes: Optional[List[str]] = Field(default_factory=list, description="Any additional personal, funeral, or medical wishes")

    def completion_percentage(self) -> int:
        """Calculates percentage of core required fields completed."""
        core_fields = [
            self.full_name is not None and len(self.full_name.strip()) > 0,
            self.home_address is not None and len(self.home_address.strip()) > 0,
            self.covers_worldwide_assets is not None,
            self.has_children is not None,
            # If has_children is True, children list must have at least one name; if False, it's satisfied
            (self.has_children is False) or (self.has_children is True and self.children is not None and len(self.children) > 0),
            # Executor needs both name and relationship to be complete
            self.executor is not None and bool(self.executor.name) and bool(self.executor.relationship),
        ]
        completed = sum(1 for f in core_fields if f)
        return int((completed / len(core_fields)) * 100)

    def get_missing_fields(self) -> List[str]:
        """Returns friendly list of fields that are still missing or ambiguous."""
        missing = []
        if not self.full_name:
            missing.append("Full Name")
        if not self.home_address:
            missing.append("Home Address")
        if self.covers_worldwide_assets is None:
            missing.append("Worldwide Assets Scope")
        if self.has_children is None:
            missing.append("Children Status")
        elif self.has_children is True and (not self.children or len(self.children) == 0):
            missing.append("Names of Children")
        
        if not self.executor:
            missing.append("Executor Details")
        else:
            if not self.executor.name and not self.executor.relationship:
                missing.append("Executor Name & Relationship")
            elif not self.executor.name:
                missing.append("Executor Name")
            elif not self.executor.relationship:
                missing.append("Executor Relationship")
                
        return missing

    def is_complete(self) -> bool:
        """Determines if the core legal intake fields are satisfied."""
        return len(self.get_missing_fields()) == 0
