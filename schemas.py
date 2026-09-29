from pydantic import BaseModel, Field, field_validator

class PromptRequest(BaseModel):
    story_prompt: str = Field(min_length=5, max_length=1200)
    character_name: str = Field(default="Alex", min_length=1, max_length=60)
    setting: str = Field(default="Enchanted forest", max_length=100)
    tone: str = Field(default="adventurous", max_length=60)
    art_style: str = Field(default="comic book", max_length=60)

    @field_validator("story_prompt", "character_name", "setting", "tone", "art_style")
    @classmethod
    def trim_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value
