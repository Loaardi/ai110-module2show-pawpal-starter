from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import calendar


@dataclass
class Task:
    """Represents a single activity."""
    description: str
    time: datetime
    frequency: str
    pet: 'Pet'  # Reference to the pet this task belongs to
    completion_status: bool = False
    
    def complete_task(self):
        """Mark this task as complete and create next occurrence if recurring."""
        self.completion_status = True

        if self.is_recurring() and self.pet is not None:
            next_time = self.next_occurrence(after=self.time)
            if next_time is not None:
                next_task = Task(
                    description=self.description,
                    time=next_time,
                    frequency=self.frequency,
                    pet=self.pet,
                    completion_status=False,
                )
                self.pet.add_task(next_task)
    
    def get_description(self) -> str:
        """Return the description of this task."""
        return self.description

    def __lt__(self, other: 'Task') -> bool:
        """Compare tasks by time for sorting (earlier time first).

        Args:
            other: Another Task instance to compare with.

        Returns:
            True if this task's time is before other's time.
        """
        if not isinstance(other, Task):
            return NotImplemented
        return self.time < other.time

    def is_recurring(self) -> bool:
        """Check if this task repeats periodically.

        Returns:
            True if frequency is 'daily', 'weekly', 'monthly', or 'yearly'.
        """
        return self.frequency.lower() in {"daily", "weekly", "monthly", "yearly"}

    def next_occurrence(self, after: Optional[datetime] = None) -> Optional[datetime]:
        """Calculate the next scheduled time for recurring tasks.

        Args:
            after: Datetime after which to find the next occurrence. Defaults to now.

        Returns:
            Next datetime for the task, or None if not recurring.
        """
        if not self.is_recurring():
            return None

        after_time = after or datetime.now()
        if after_time < self.time:
            candidate = self.time
        else:
            candidate = self.time
            freq = self.frequency.lower()
            while candidate <= after_time:
                if freq == "daily":
                    candidate += timedelta(days=1)
                elif freq == "weekly":
                    candidate += timedelta(weeks=1)
                elif freq == "yearly":
                    candidate = candidate.replace(year=candidate.year + 1)
                elif freq == "monthly":
                    # increment month with roll-over
                    year = candidate.year + (candidate.month // 12)
                    month = candidate.month % 12 + 1
                    day = min(candidate.day, calendar.monthrange(year, month)[1])
                    candidate = candidate.replace(year=year, month=month, day=day)
                else:
                    return None
        return candidate


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
        """Get specific care needs based on the animal type.

        Returns:
            A string describing care requirements for the pet's species.
            Falls back to generic care for unknown types.
        """
        needs_map = {
            "Dog": "Daily walks, feeding twice a day, grooming, exercise",
            "Cat": "Litter box cleaning, feeding, playtime, grooming",
            "Bird": "Fresh water, feeding, cage cleaning, social interaction",
            "Fish": "Water changes, feeding, tank maintenance",
            "Rabbit": "Feeding hay/veggies, litter box, exercise space",
        }
        return needs_map.get(self.kind_of_animal, f"Basic care for {self.kind_of_animal}")

    
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

    def get_all_tasks(self, sort_by_time: bool = True) -> List[Task]:
        """Retrieve all tasks from all pets, optionally sorted by time."""
        tasks = self.owner.get_all_tasks()
        return sorted(tasks) if sort_by_time else list(tasks)

    def get_tasks_for_pet(self, pet_name: str, sort_by_time: bool = True) -> List[Task]:
        """Get all tasks for one pet, with optional sorting."""
        return self.filter_tasks(pet_name=pet_name, sort_by_time=sort_by_time)

    def get_tasks_by_status(self, completed: bool = False, sort_by_time: bool = True) -> List[Task]:
        """Get tasks filtered by completion status."""
        return self.filter_tasks(completed=completed, sort_by_time=sort_by_time)

    def filter_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None, sort_by_time: bool = True) -> List[Task]:
        """Filter tasks by pet name and/or completion status, with optional sorting.

        Args:
            pet_name: Name of the pet to filter by. If None, include all pets.
            completed: Filter by completion status. If None, include both.
            sort_by_time: Whether to sort results by time (earliest first).

        Returns:
            List of filtered and optionally sorted tasks.
        """
        tasks = self.get_all_tasks(sort_by_time=False)

        if pet_name is not None:
            tasks = [task for task in tasks if task.pet and task.pet.name == pet_name]

        if completed is not None:
            tasks = [task for task in tasks if task.completion_status == completed]

        return sorted(tasks) if sort_by_time else tasks

    def get_tasks_for_window(self, start: datetime, end: datetime) -> List[Task]:
        """Get all tasks within a datetime window, expanding recurring tasks.

        Args:
            start: Start of the window (inclusive).
            end: End of the window (inclusive).

        Returns:
            Sorted list of tasks (including expanded recurring instances) in the window.
        """
        tasks = []
        for task in self.get_all_tasks(sort_by_time=False):
            if start <= task.time <= end:
                tasks.append(task)
            if task.is_recurring():
                # Shift recurrence start to after the task's own datetime to avoid duplicates
                anchor = max(task.time, start)
                next_time = task.next_occurrence(after=anchor)
                while next_time and start <= next_time <= end:
                    tasks.append(Task(description=task.description, time=next_time, frequency=task.frequency, pet=task.pet, completion_status=task.completion_status))
                    next_time = Task(description=task.description, time=next_time, frequency=task.frequency, pet=task.pet).next_occurrence(after=next_time)
        return sorted(tasks)

    def get_today_tasks(self, on_date: Optional[date] = None) -> List[Task]:
        """Get all tasks scheduled for a specific date, including recurring expansions.

        Args:
            on_date: Date to get tasks for. Defaults to today.

        Returns:
            Sorted list of tasks for the date.
        """
        on_date = on_date or date.today()
        start = datetime.combine(on_date, datetime.min.time())
        end = datetime.combine(on_date, datetime.max.time())
        return self.get_tasks_for_window(start, end)

    def get_next_task(self, after: Optional[datetime] = None) -> Optional[Task]:
        """Find the next pending task after a given time, including recurring.

        Args:
            after: Datetime to start searching from. Defaults to now.

        Returns:
            The earliest pending task after the given time, or None if none found.
        """
        after = after or datetime.now()
        window_end = after + timedelta(days=7)
        candidates = self.get_tasks_for_window(after, window_end)
        for task in candidates:
            if task.time >= after and not task.completion_status:
                return task
        return None

    def get_conflicts_for_task(self, candidate_task: Task, window_mins: int = 0) -> List[Task]:
        """Find tasks that conflict with a candidate task within a time window.

        Args:
            candidate_task: The task to check for conflicts.
            window_mins: Minutes around candidate_task.time to check for overlaps.

        Returns:
            List of conflicting tasks on the same date within the window.
        """
        conflicts = []
        window_seconds = window_mins * 60
        for task in self.get_all_tasks(sort_by_time=False):
            if task is candidate_task:
                continue
            if task.time.date() == candidate_task.time.date():
                if abs((task.time - candidate_task.time).total_seconds()) <= window_seconds:
                    conflicts.append(task)
        return conflicts

    def has_conflict(self, candidate_task: Task, window_mins: int = 0) -> bool:
        """Check if a candidate task has any conflicts within a window.

        Args:
            candidate_task: The task to check.
            window_mins: Minutes to check around the task time.

        Returns:
            True if there are conflicting tasks.
        """
        return len(self.get_conflicts_for_task(candidate_task, window_mins)) > 0

    def get_same_time_conflicts(self) -> List[Tuple[Task, Task]]:
        """Find all pairs of tasks scheduled at exactly the same time.

        Returns:
            List of tuples, each containing two conflicting tasks.
        """
        tasks = self.get_all_tasks(sort_by_time=False)
        conflicts = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].time == tasks[j].time:
                    conflicts.append((tasks[i], tasks[j]))
        return conflicts

    def has_same_time_conflicts(self) -> bool:
        """Check if there are any tasks at the same time.

        Returns:
            True if same-time conflicts exist.
        """
        return len(self.get_same_time_conflicts()) > 0

    def check_for_conflicts(self) -> Optional[str]:
        """Perform a lightweight check for same-time conflicts.

        Returns:
            Warning message if conflicts found, else None. Handles errors gracefully.
        """
        try:
            same_time_conflicts = self.get_same_time_conflicts()
            if same_time_conflicts:
                return f"Warning: {len(same_time_conflicts)} task(s) scheduled at the same time."
            return None
        except Exception as e:
            return f"Error checking conflicts: {str(e)}"

    def organize_tasks_by_date(self) -> Dict[date, List[Task]]:
        """Organize tasks by their due date."""
        organized: Dict[date, List[Task]] = {}
        for task in self.get_all_tasks(sort_by_time=True):
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
