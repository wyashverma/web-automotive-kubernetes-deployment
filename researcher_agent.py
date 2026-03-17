from datetime import datetime
from typing import List, Dict, Optional
import os
from car_model import CarData, CarSpecs
from shared_memory import SharedStateMemory, AgentType, Message, TaskStatus
from langchain_google_genai import ChatGoogleGenerativeAI


class AutomotiveResearchTools:
    CAR_DATABASE = {
        "tesla model 3": {
            "brand": "Tesla",
            "model": "Model 3",
            "horsepower": 480,
            "acceleration": 3.1,
            "top_speed": 162,
            "battery_capacity": 75,
            "range_miles": 358,
            "price": 40630,
            "drivetrain": "Dual Motor AWD",
            "pros": [
                "Excellent range and efficiency",
                "Access to Tesla Supercharger network",
                "Over-the-air software updates",
                "Strong acceleration and performance",
                "Minimalist interior with large touchscreen"
            ],
            "cons": [
                "Build quality inconsistencies",
                "Road noise at highway speeds",
                "No Apple CarPlay or Android Auto",
                "Relies on touchscreen for most controls",
                "Higher insurance costs"
            ],
            "summary": "The Tesla Model 3 is an all-electric compact sedan that offers impressive range, strong performance, and access to Tesla's extensive Supercharger network."
        },
        "bmw i4": {
            "brand": "BMW",
            "model": "i4",
            "horsepower": 335,
            "acceleration": 5.5,
            "top_speed": 124,
            "battery_capacity": 83.9,
            "range_miles": 301,
            "price": 52200,
            "drivetrain": "RWD / AWD available",
            "pros": [
                "Luxurious interior with high-quality materials",
                "Traditional BMW driving dynamics",
                "Fast charging capability",
                "Available in multiple variants",
                "Apple CarPlay and Android Auto included"
            ],
            "cons": [
                "Less efficient than Tesla",
                "Smaller trunk opening",
                "Higher price point",
                "Rear seat space is tight",
                "Infotainment system can be complex"
            ],
            "summary": "The BMW i4 combines the familiar BMW driving experience with electric power."
        },
        "ford mustang mach-e": {
            "brand": "Ford",
            "model": "Mustang Mach-E",
            "horsepower": 480,
            "acceleration": 3.5,
            "top_speed": 130,
            "battery_capacity": 88,
            "range_miles": 312,
            "price": 43895,
            "drivetrain": "RWD / AWD",
            "pros": [
                "Sporty Mustang-inspired design",
                "Good range and performance",
                "Spacious interior",
                "User-friendly infotainment",
                "Available tax credit"
            ],
            "cons": [
                "Charging speed could be better",
                "Some cheap interior materials",
                "Limited rear visibility",
                "FordPass app can be glitchy"
            ],
            "summary": "The Ford Mustang Mach-E brings Mustang spirit to the EV world with sporty styling and good performance."
        },
        "hyundai ioniq 6": {
            "brand": "Hyundai",
            "model": "Ioniq 6",
            "horsepower": 320,
            "acceleration": 5.1,
            "top_speed": 115,
            "battery_capacity": 77.4,
            "range_miles": 361,
            "price": 41600,
            "drivetrain": "RWD / AWD",
            "pros": [
                "Excellent efficiency and range",
                "Ultra-fast 800V charging",
                "Unique aerodynamic design",
                "Good value for money",
                "Comfortable ride"
            ],
            "cons": [
                "Polarizing design",
                "Limited rear headroom",
                "No frunk (front trunk)",
                "Touch-sensitive controls"
            ],
            "summary": "The Hyundai Ioniq 6 is an aerodynamic electric sedan that offers exceptional range and ultra-fast charging."
        }
    }

    @staticmethod
    def search_car(car_model: str) -> Dict:
        car_model_lower = car_model.lower()
        if car_model_lower in AutomotiveResearchTools.CAR_DATABASE:
            return AutomotiveResearchTools.CAR_DATABASE[car_model_lower]
        for key, data in AutomotiveResearchTools.CAR_DATABASE.items():
            if car_model_lower in key or key in car_model_lower:
                return data
        brand = car_model.split()[0] if car_model.split() else "Unknown"
        model = ' '.join(car_model.split()[1:]) if len(car_model.split()) > 1 else ""
        return {
            "brand": brand,
            "model": model,
            "horsepower": None,
            "acceleration": None,
            "range_miles": None,
            "price": None,
            "pros": ["Information being gathered"],
            "cons": ["Limited data available"],
            "summary": f"Basic information about {car_model}"
        }

    @staticmethod
    def get_car_data(car_model: str) -> Dict:
        return AutomotiveResearchTools.search_car(car_model)


class ResearcherAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3) if os.getenv("GOOGLE_API_KEY") else None
        self.tools = AutomotiveResearchTools()
        self.research_cache = {}

    def research_car(self, car_model: str) -> CarData:
        print(f"🔍 Researching: {car_model}")
        if car_model in self.research_cache:
            print(f"   Using cached data for {car_model}")
            return self.research_cache[car_model]
        
        db_data = self.tools.get_car_data(car_model)
        specs = CarSpecs(
            brand=db_data.get('brand'),
            model=db_data.get('model'),
            horsepower=db_data.get('horsepower'),
            acceleration=db_data.get('acceleration'),
            range_miles=db_data.get('range_miles'),
            price=db_data.get('price'),
            drivetrain=db_data.get('drivetrain'),
            battery_capacity=db_data.get('battery_capacity'),
            top_speed=db_data.get('top_speed')
        )
        car_data = CarData(
            specifications=specs,
            pros=db_data.get('pros', []),
            cons=db_data.get('cons', []),
            summary=db_data.get('summary', f"Information about {car_model}"),
            sources=["Automotive Research Database 2024"]
        )
        self.research_cache[car_model] = car_data
        print(f"   ✅ Research complete for {car_model}")
        return car_data

    def research_multiple_cars(self, car_models: List[str]) -> Dict[str, CarData]:
        results = {}
        for car in car_models:
            results[car] = self.research_car(car)
        return results


class ResearcherAgentWrapper:
    def __init__(self, shared_memory: SharedStateMemory, researcher_instance=None):
        self.agent_type = AgentType.RESEARCHER
        self.name = "Automotive Researcher"
        self.shared_memory = shared_memory
        self.researcher = researcher_instance or ResearcherAgent()
        self.capabilities = ["research_cars", "get_specs", "find_pros_cons"]
        self.status = "idle"
        print(f"✅ Researcher Agent '{self.name}' initialized")

    def process_message(self, message: Message) -> Optional[Message]:
        self.status = "processing"
        content = message.content
        message_type = message.message_type

        if message_type == "research_request":
            cars = content.get("cars", [])
            task_id = content.get("task_id")
            print(f"🔬 Researching cars: {cars}")
            results = {}
            
            for car in cars:
                print(f"   Researching {car}...")
                car_data = self.researcher.research_car(car)
                if hasattr(car_data, 'to_dict'):
                    car_dict = car_data.to_dict()
                elif isinstance(car_data, dict):
                    car_dict = car_data
                else:
                    car_dict = {"data": str(car_data)}
                
                data_id = self.shared_memory.store_research(car, car_dict)
                summary = getattr(car_data, 'summary', car_dict.get('summary', f"Research data for {car}"))
                
                results[car] = {
                    "data_id": data_id,
                    "summary": summary
                }
                print(f"   ✅ {car} stored with ID: {data_id}")

            if task_id:
                self.shared_memory.update_task(
                    task_id,
                    TaskStatus.COMPLETED,
                    output_data={"results": results}
                )

            self.status = "idle"
            return Message(
                from_agent=self.agent_type,
                to_agent=AgentType.SUPERVISOR,
                message_type="research_response",
                content={
                    "task_id": task_id,
                    "status": "success",
                    "results": results,
                    "cars_completed": cars
                },
                timestamp=datetime.now().isoformat(),
                message_id=f"resp_{abs(hash(str(results))) % 1000000:06d}"
            )

        self.status = "idle"
        return None