from datetime import datetime
import hashlib
from typing import Dict, List, Optional
from shared_memory import SharedStateMemory, AgentType, Message, TaskStatus
from researcher_agent import ResearcherAgentWrapper
from writer_agent import WriterAgentWrapper


class SupervisorAgent:
    def __init__(self, shared_memory: SharedStateMemory,
                 researcher: Optional[ResearcherAgentWrapper] = None,
                 writer: Optional[WriterAgentWrapper] = None):
        self.agent_type = AgentType.SUPERVISOR
        self.name = "Main Supervisor"
        self.shared_memory = shared_memory
        self.researcher = researcher
        self.writer = writer
        self.status = "idle"
        self.active_workflows = {}
        print("\n" + "="*60)
        print("✅ SUPERVISOR AGENT INITIALIZED")
        print("="*60)

    def process_user_query(self, query: str, output_format: str = "both") -> Dict:
        print(f"\n🎯 SUPERVISOR: Processing query: '{query}'")
        intent = self._parse_query_intent(query)
        print(f"   Detected intent: {intent['type']}")
        print(f"   Cars mentioned: {intent['cars']}")

        workflow_id = self._create_workflow(intent, output_format)

        if intent['type'] == 'comparison' and len(intent['cars']) >= 2:
            result = self._handle_comparison(intent['cars'], output_format, workflow_id)
        elif intent['type'] == 'single_car' and len(intent['cars']) == 1:
            result = self._handle_single_car(intent['cars'][0], output_format, workflow_id)
        elif intent['type'] == 'research' and len(intent['cars']) >= 1:
            result = self._handle_research(intent['cars'], workflow_id)
        else:
            result = {
                "status": "error",
                "message": "Could not understand query. Please specify cars to compare or research."
            }

        self.shared_memory.conversation_history.append({
            "query": query,
            "intent": intent,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "workflow_id": workflow_id
        })

        return result

    def _parse_query_intent(self, query: str) -> Dict:
        query_lower = query.lower()
        intent = {"type": "unknown", "cars": [], "action": None}
        
        comparison_keywords = ["compare", "vs", "versus", "difference between"]
        research_keywords = ["research", "tell me about", "information on", "specs for", "details about"]
        car_brands = ["tesla", "bmw", "ford", "hyundai", "audi", "mercedes"]

        words = query_lower.split()
        found_cars = []
        for i, word in enumerate(words):
            if word in car_brands and i < len(words) - 1:
                car_parts = [word.capitalize()]
                j = i + 1
                while j < len(words) and words[j] not in car_brands and len(car_parts) < 3:
                    car_parts.append(words[j].capitalize())
                    j += 1
                found_cars.append(' '.join(car_parts))

        if found_cars:
            intent["cars"] = found_cars
            if any(keyword in query_lower for keyword in comparison_keywords):
                intent["type"] = "comparison"
                intent["action"] = "compare"
            elif any(keyword in query_lower for keyword in research_keywords):
                intent["type"] = "research"
                intent["action"] = "research"
            elif len(found_cars) == 1:
                intent["type"] = "single_car"
                intent["action"] = "report"
            else:
                intent["type"] = "comparison"
                intent["action"] = "compare"

        return intent

    def _create_workflow(self, intent: Dict, output_format: str) -> str:
        workflow_id = hashlib.md5(f"{intent}_{datetime.now()}".encode()).hexdigest()[:8]
        self.active_workflows[workflow_id] = {
            "intent": intent,
            "output_format": output_format,
            "status": "started",
            "steps": [],
            "created_at": datetime.now().isoformat()
        }
        return workflow_id

    def _handle_comparison(self, cars: List[str], output_format: str, workflow_id: str) -> Dict:
        print(f"\n🔄 Handling comparison for {cars}")
        need_research = [car for car in cars if not self.shared_memory.get_latest_research(car)]

        if need_research:
            print(f"   Need to research: {need_research}")
            task_id = self.shared_memory.create_task("research", AgentType.RESEARCHER, {"cars": need_research})
            self.active_workflows[workflow_id]["steps"].append({"step": "research", "task_id": task_id, "status": "initiated"})
            
            if self.researcher:
                research_response = self.researcher.process_message(
                    Message(
                        from_agent=self.agent_type,
                        to_agent=AgentType.RESEARCHER,
                        message_type="research_request",
                        content={"cars": need_research, "task_id": task_id},
                        timestamp=datetime.now().isoformat(),
                        message_id=f"req_{task_id}"
                    )
                )
                if research_response and research_response.content.get("status") == "success":
                    self.active_workflows[workflow_id]["steps"][-1]["status"] = "completed"
                else:
                    return {"status": "error", "message": "Failed to research cars", "cars": cars}

        print(f"   Generating comparison report")
        write_task_id = self.shared_memory.create_task("write_comparison", AgentType.WRITER, {"cars": cars, "format": output_format})
        self.active_workflows[workflow_id]["steps"].append({"step": "writing", "task_id": write_task_id, "status": "initiated"})

        if self.writer:
            write_response = self.writer.process_message(
                Message(
                    from_agent=self.agent_type,
                    to_agent=AgentType.WRITER,
                    message_type="writing_request",
                    content={
                        "type": "side_by_side" if len(cars) == 2 else "multi_car",
                        "cars": cars,
                        "format": output_format,
                        "task_id": write_task_id,
                        "workflow_id": workflow_id
                    },
                    timestamp=datetime.now().isoformat(),
                    message_id=f"req_{write_task_id}"
                )
            )

            if write_response and write_response.content.get("status") == "success":
                self.active_workflows[workflow_id]["steps"][-1]["status"] = "completed"
                self.active_workflows[workflow_id]["status"] = "completed"
                return {
                    "status": "success",
                    "type": "comparison",
                    "cars": cars,
                    "message": f"Successfully generated comparison for {', '.join(cars)}",
                    "outputs": write_response.content.get("outputs", {}),
                    "workflow_id": workflow_id
                }

        return {"status": "error", "message": "Failed to generate comparison report", "cars": cars}

    def _handle_single_car(self, car: str, output_format: str, workflow_id: str) -> Dict:
        print(f"\n🔄 Handling single car report for {car}")
        if not self.shared_memory.get_latest_research(car):
            research_result = self._handle_research([car], workflow_id)
            if research_result.get("status") != "success":
                return research_result

        write_task_id = self.shared_memory.create_task("write_report", AgentType.WRITER, {"cars": [car], "format": output_format})
        if self.writer:
            write_response = self.writer.process_message(
                Message(
                    from_agent=self.agent_type,
                    to_agent=AgentType.WRITER,
                    message_type="writing_request",
                    content={
                        "type": "single_report",
                        "cars": [car],
                        "format": output_format,
                        "task_id": write_task_id
                    },
                    timestamp=datetime.now().isoformat(),
                    message_id=f"req_{write_task_id}"
                )
            )
            if write_response and write_response.content.get("status") == "success":
                return {
                    "status": "success",
                    "type": "single_car_report",
                    "car": car,
                    "message": f"Successfully generated report for {car}",
                    "outputs": write_response.content.get("outputs", {}),
                    "workflow_id": workflow_id
                }
        return {"status": "error", "message": f"Failed to generate report for {car}"}

    def _handle_research(self, cars: List[str], workflow_id: str) -> Dict:
        print(f"\n🔄 Handling research for {cars}")
        task_id = self.shared_memory.create_task("research_only", AgentType.RESEARCHER, {"cars": cars})
        
        if self.researcher:
            research_response = self.researcher.process_message(
                Message(
                    from_agent=self.agent_type,
                    to_agent=AgentType.RESEARCHER,
                    message_type="research_request",
                    content={"cars": cars, "task_id": task_id},
                    timestamp=datetime.now().isoformat(),
                    message_id=f"req_{task_id}"
                )
            )
            if research_response and research_response.content.get("status") == "success":
                results = {}
                for car in cars:
                    car_data = self.shared_memory.get_latest_research(car)
                    if car_data:
                        results[car] = car_data
                return {
                    "status": "success",
                    "type": "research",
                    "cars": cars,
                    "message": f"Successfully researched {', '.join(cars)}",
                    "data": results,
                    "workflow_id": workflow_id
                }
        return {"status": "error", "message": f"Failed to research cars: {cars}"}

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        return self.active_workflows.get(workflow_id)

    def get_state_summary(self) -> Dict:
        memory_summary = self.shared_memory.get_state_summary()
        return {
            "shared_memory": memory_summary,
            "supervisor_status": self.status,
            "researcher_status": self.researcher.status if self.researcher else "unknown",
            "writer_status": self.writer.status if self.writer else "unknown",
            "active_workflows": len(self.active_workflows)
        }