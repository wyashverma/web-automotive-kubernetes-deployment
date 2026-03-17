from datetime import datetime
from typing import List, Dict, Optional


class CarSpecs:
    def __init__(self, brand=None, model=None, year=None, horsepower=None,
                 acceleration=None, top_speed=None, battery_capacity=None,
                 range_miles=None, price=None, drivetrain=None):
        self.brand = brand
        self.model = model
        self.year = year
        self.horsepower = horsepower
        self.acceleration = acceleration
        self.top_speed = top_speed
        self.battery_capacity = battery_capacity
        self.range_miles = range_miles
        self.price = price
        self.drivetrain = drivetrain

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class CarData:
    def __init__(self, specifications=None, pros=None, cons=None, summary="", sources=None):
        self.specifications = specifications or CarSpecs()
        self.pros = pros or []
        self.cons = cons or []
        self.summary = summary
        self.sources = sources or []
        self.last_updated = datetime.now().isoformat()

    def to_dict(self):
        return {
            "specifications": self.specifications.to_dict(),
            "pros": self.pros,
            "cons": self.cons,
            "summary": self.summary,
            "sources": self.sources,
            "last_updated": self.last_updated
        }