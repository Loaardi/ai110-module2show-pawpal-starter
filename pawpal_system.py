from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict


@dataclass
class Task:
    """Represents a single activity."""
    description: str
    time: datetime
    frequency: str
    pet: 'Pet'  # Reference to the pet this task belongs to
    completion_status: bool = False
    
    def complete_task(self):
        """Mark this task as complete."""
        self.completion_status = True
    
    def get_description(self) -> str:
        """Return the description of this task."""
        return self.description


@dataclass
class Pet:
    """Represents a pet with its attributes and care information."""
    name: str
    kind_of_animal: str
    owner: 'Owner'  # Reference to the owner
    tasks: List[Task] = field(default_factory=list)
    
    def get_animal_type(self) -> str:
        """Return the type of animal this pet is."""
        return self.kind_of_animal
    
    def get_animal_needs(self) -> str:
        """Return the care needs for this animal."""
        # This could be expanded based on animal type
        return f"Basic care for {self.kind_of_animal}"
    
    def get_priority(self) -> int:
        """Return the priority level for this pet's care."""
        # Priority could be calculated based on tasks or animal type
        return 1  # Default priority
    
    def add_task(self, task: Task):
        """Add a task to this pet."""
        self.tasks.append(task)
        task.pet = self
    
    def get_tasks(self) -> List[Task]:
        """Return the list of tasks for this pet."""
        return self.tasks


class Scheduler:
    """The "Brain" that retrieves, organizes, and manages tasks across pets."""
    
    def __init__(self, owner: 'Owner'):
        """Initialize the scheduler with an owner."""
        self.owner = owner
    
    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks from the owner's pets."""
        return self.owner.get_all_tasks()
    
    def organize_tasks_by_date(self) -> Dict[date, List[Task]]:
        """Organize tasks by their due date."""
        tasks = self.get_all_tasks()
        organized = {}
        for task in tasks:
            task_date = task.time.date()
            if task_date not in organized:
                organized[task_date] = []
            organized[task_date].append(task)
        return organized
    
    def view_schedule(self):
        """Display the organized schedule."""
        organized = self.organize_tasks_by_date()
        for task_date, tasks in sorted(organized.items()):
            print(f"{task_date}: {[task.description for task in tasks]}")


class Owner:
    """Represents a pet owner with basic information."""
    
    def __init__(self, name: str, age: int):
        """Initialize an owner with name and age."""
        self.name = name
        self.age = age
        self.pets: List[Pet] = []
    
    def get_name(self) -> str:
        """Return the owner's name."""
        return self.name
    
    def get_age(self) -> int:
        """Return the owner's age."""
        return self.age
    
    def add_pet(self, pet: Pet):
        """Add a pet to this owner."""
        self.pets.append(pet)
        pet.owner = self
    
    def get_all_tasks(self) -> List[Task]:
        """Return all tasks from all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks
