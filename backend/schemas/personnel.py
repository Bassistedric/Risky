from typing import Optional

from pydantic import BaseModel


class PersonArchiveRequest(BaseModel):
    reason: Optional[str] = None