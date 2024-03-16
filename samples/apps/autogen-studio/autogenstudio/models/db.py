from enum import Enum
from typing import Any, Callable, Dict, Literal, Optional, Union, List
from sqlmodel import JSON, Column, DateTime, Field, SQLModel, func, Relationship, Enum as SqlEnum
from datetime import datetime


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now(), sa_column=Column(
        DateTime(timezone=True), server_default=func.now()))  # pylint: disable=not-callable
    updated_at: datetime = Field(default=datetime.now(), sa_column=Column(
        DateTime(timezone=True), onupdate=func.now()))  # pylint: disable=not-callable
    user_id: Optional[str] = None
    role: str
    content: str
    session_id: Optional[int] = Field(default=None, foreign_key="session.id")
    workflow_id: Optional[int] = Field(default=None, foreign_key="workflow.id")
    connection_id: Optional[str] = None
    meta: Optional[Dict] = Field(default={}, sa_column=Column(JSON))


class Session(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now(), sa_column=Column(
        DateTime(timezone=True), server_default=func.now()))  # pylint: disable=not-callable
    updated_at: datetime = Field(default=datetime.now(), sa_column=Column(
        DateTime(timezone=True), onupdate=func.now()))  # pylint: disable=not-callable
    user_id: Optional[str] = None
    workflow_id: Optional[int] = Field(default=None, foreign_key="workflow.id")
    title: Optional[str] = None
    description: Optional[str] = None


class AgentSkillLink(SQLModel, table=True):
    agent_id: int = Field(default=None, primary_key=True,
                          foreign_key="agent.id")
    skill_id: int = Field(default=None, primary_key=True,
                          foreign_key="skill.id")


class AgentModelLink(SQLModel, table=True):
    agent_id: int = Field(default=None, primary_key=True,
                          foreign_key="agent.id")
    modele_id: int = Field(default=None, primary_key=True,
                           foreign_key="model.id")


class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, sa_column=Column(
        DateTime(timezone=True), server_default=func.now()))  # pylint: disable=not-callable
    updated_at: datetime = Field(default_factory=datetime.now, sa_column=Column(
        DateTime(timezone=True), onupdate=func.now()))  # pylint: disable=not-callable
    user_id: Optional[str] = None
    title: str
    content: str
    description: Optional[str] = None
    secrets: Optional[Dict] = Field(default={}, sa_column=Column(JSON))
    libraries: Optional[Dict] = Field(default={}, sa_column=Column(JSON))
    agents: List["Agent"] = Relationship(
        back_populates="skills", link_model=AgentSkillLink)


class Model(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now(), sa_column=Column(
        DateTime(timezone=True), server_default=func.now()))  # pylint: disable=not-callable
    updated_at: datetime = Field(default=datetime.now(), sa_column=Column(
        DateTime(timezone=True), onupdate=func.now()))  # pylint: disable=not-callable
    user_id: Optional[str] = None
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    api_type: Optional[str] = None
    api_version: Optional[str] = None
    description: Optional[str] = None
    temperature: float = 0
    cache_seed: Optional[int] = None
    timeout: Optional[int] = None
    max_tokens: Optional[int] = None
    agents: List["Agent"] = Relationship(
        back_populates="models", link_model=AgentModelLink)


class AgentConfig(SQLModel, table=False):
    name: str
    human_input_mode: str = "NEVER"
    max_consecutive_auto_reply: int = 10
    system_message: Optional[str] = None
    is_termination_msg: Optional[Union[bool, str, Callable]] = None
    code_execution_config: Optional[Union[bool, Dict]] = Field(
        default=False, sa_column=Column(JSON))
    default_auto_reply: Optional[str] = ""
    description: Optional[str] = None


class AgentType(str, Enum):
    assistant = "assistant"
    userproxy = "userproxy"
    groupchat = "groupchat"


class Agent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now(), sa_column=Column(
        DateTime(timezone=True), server_default=func.now()))  # pylint: disable=not-callable
    updated_at: datetime = Field(default=datetime.now(), sa_column=Column(
        DateTime(timezone=True), onupdate=func.now()))  # pylint: disable=not-callable
    user_id: Optional[str] = None
    type: AgentType = Field(default=AgentType.assistant,
                            sa_column=Column(SqlEnum(AgentType)))
    config: AgentConfig = Field(
        default_factory=AgentConfig, sa_column=Column(JSON))
    skills: List[Skill] = Relationship(
        back_populates="agents", link_model=AgentSkillLink)
    models: List[Model] = Relationship(
        back_populates="agents", link_model=AgentModelLink)


class GroupChatConfig(SQLModel, table=False):
    agents: List[Agent] = Field(default_factory=list)
    admin_name: str = "Admin"
    messages: List[Dict] = Field(default_factory=list)
    max_round: Optional[int] = 10
    admin_name: Optional[str] = "Admin"
    speaker_selection_method: Optional[str] = "auto"
    allow_repeat_speaker: Optional[Union[bool, List[AgentConfig]]] = True


class GroupChat(SQLModel, table=False):
    type: str = "groupchat"
    config: AgentConfig = Field(
        default_factory=AgentConfig, sa_column=Column(JSON))
    groupchat_config: Optional[GroupChatConfig] = Field(
        default_factory=GroupChatConfig, sa_column=Column(JSON))
    skills: Optional[List[Skill]] = Field(
        default_factory=list, sa_column=Column(JSON))


class WorkFlowType(str, Enum):
    twoagents = "twoagents"
    groupchat = "groupchat"


class WorkFlowSummaryMethod(str, Enum):
    last = "last"
    none = "none"
    llm = "llm"


class Workflow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now(), sa_column=Column(
        DateTime(timezone=True), server_default=func.now()))  # pylint: disable=not-callable
    updated_at: datetime = Field(default=datetime.now(), sa_column=Column(
        DateTime(timezone=True), onupdate=func.now()))  # pylint: disable=not-callable
    user_id: Optional[str] = None
    name: str
    description: str
    sender: Agent = Field(default_factory=Agent, sa_column=Column(JSON))
    receiver: Union[Agent, GroupChat] = Field(
        default_factory=Union[Agent, GroupChat], sa_column=Column(JSON))
    type: WorkFlowType = Field(default=WorkFlowType.twoagents,
                               sa_column=Column(SqlEnum(WorkFlowType)))
    # summary_method: Optional[Literal["last", "none", "llm"]] = "last"
    summary_method: Optional[WorkFlowSummaryMethod] = Field(
        default=WorkFlowSummaryMethod.last, sa_column=Column(SqlEnum(WorkFlowSummaryMethod)))
