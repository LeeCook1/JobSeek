from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

class UserJobLink(SQLModel, table=True):
    job_id: Optional[int] = Field(default=None, foreign_key="job.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    match_percent: float = -1.0 
    visited: bool = False
    applied: bool = False

    job: "Job" = Relationship(back_populates="user_links")
    user: "User" = Relationship(back_populates="job_links")

class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    scrape_id: Optional[int] = Field(default=None, foreign_key="scrape.id")
    job_site_id: str
    title: str
    description: str
    location: Optional[str] = None
    salary: Optional[str] = None
    remote: Optional[bool] = False
    match: float = -1.0
    url: str 
    apply_url: str
    site: str    
    provider: str
    viewed: bool = False
    applied: bool = False

    user_links: List[UserJobLink] = Relationship(back_populates="job")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    hash_pass: str
    resume: str

    job_links: List[UserJobLink] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    task_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class Scrape(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)