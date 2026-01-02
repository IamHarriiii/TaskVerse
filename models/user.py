from pydantic import EmailStr, Field
from models.base import BaseDomainModal

class User(BaseDomainModal):
    """
    Internal User domain model.
    Represents how users are stored in the system.
    """

    name : str = Field(min_length = 2, max_length = 30) 
    email : EmailStr