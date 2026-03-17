from datetime import datetime
import hashlib
import json
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict


class AgentType(Enum):
    SUPERVISOR = "supervisor"
    RESEARCHER = "researcher"
    WRITER = "writer"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Message:
    from_agent: AgentType
    to_agent: AgentType
    message_type: str
    content: Dict
    timestamp: str
    message_id: str


@dataclass
class Task:
    task_id: str
    task_type: str
    assigned_to: AgentType
    status: TaskStatus
    input_data: Dict
    output_data: Optional[Dict] = None
    created_at: str = None
    completed_at: str = None
    error: Optional[str] = None


class SharedStateMemory:
    def __init__(self):
        self.research_data = {}
        self.generated_reports = {}
        self.conversation_history = []
        self.tasks = {}
        self.messages = []
        self.last_updated = datetime.now().isoformat()
        self.version = "1.0"
        print("✅ Shared State Memory Initialized")

    def store_research(self, car_model: str, data: Dict) -> str:
        data_id = hashlib.md5(f"{car_model}_{datetime.now()}".encode()).hexdigest()[:8]
        if car_model not in self.research_data:
            self.research_data[car_model] = []
        self.research_data[car_model].append({
            "data_id": data_id,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        self.last_updated = datetime.now().isoformat()
        return data_id

    def get_latest_research(self, car_model: str) -> Optional[Dict]:
        if car_model in self.research_data and self.research_data[car_model]:
            return self.research_data[car_model][-1]["data"]
        return None

    def get_all_research(self, car_model: str) -> List[Dict]:
        return self.research_data.get(car_model, [])

    def store_report(self, report_name: str, report_data: Dict, report_type: str) -> str:
        report_id = hashlib.md5(f"{report_name}_{datetime.now()}".encode()).hexdigest()[:8]
        self.generated_reports[report_id] = {
            "name": report_name,
            "type": report_type,
            "data": report_data,
            "timestamp": datetime.now().isoformat()
        }
        self.last_updated = datetime.now().isoformat()
        return report_id

    def get_report(self, report_id: str) -> Optional[Dict]:
        return self.generated_reports.get(report_id)

    def create_task(self, task_type: str, assigned_to: AgentType, input_data: Dict) -> str:
        task_id = hashlib.md5(f"{task_type}_{datetime.now()}".encode()).hexdigest()[:8]
        task = Task(
            task_id=task_id,
            task_type=task_type,
            assigned_to=assigned_to,
            status=TaskStatus.PENDING,
            input_data=input_data,
            created_at=datetime.now().isoformat()
        )
        self.tasks[task_id] = task
        return task_id

    def update_task(self, task_id: str, status: TaskStatus, output_data: Optional[Dict] = None, error: Optional[str] = None):
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self.tasks[task_id].output_data = output_data
            self.tasks[task_id].error = error
            if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                self.tasks[task_id].completed_at = datetime.now().isoformat()

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def get_pending_tasks(self, agent_type: Optional[AgentType] = None) -> List[Task]:
        pending = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                if agent_type is None or task.assigned_to == agent_type:
                    pending.append(task)
        return pending

    def send_message(self, from_agent: AgentType, to_agent: AgentType,
                     message_type: str, content: Dict) -> str:
        message_id = hashlib.md5(f"{from_agent}_{to_agent}_{datetime.now()}".encode()).hexdigest()[:8]
        message = Message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            timestamp=datetime.now().isoformat(),
            message_id=message_id
        )
        self.messages.append(message)
        return message_id

    def get_messages_for_agent(self, agent: AgentType, limit: int = 10) -> List[Message]:
        agent_messages = [m for m in self.messages if m.to_agent == agent]
        return agent_messages[-limit:]

    def get_conversation_context(self, query: str) -> Dict:
        context = {
            "recent_searches": [],
            "available_cars": list(self.research_data.keys()),
            "recent_reports": list(self.generated_reports.keys())[-3:]
        }
        return context

    def get_state_summary(self) -> Dict:
        return {
            "total_cars_researched": len(self.research_data),
            "total_reports_generated": len(self.generated_reports),
            "pending_tasks": len(self.get_pending_tasks()),
            "total_messages": len(self.messages),
            "last_updated": self.last_updated,
            "available_cars": list(self.research_data.keys())
        }