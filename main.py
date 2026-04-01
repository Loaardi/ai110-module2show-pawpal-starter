from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime, date

def main():
    # Create an Owner
    owner = Owner(name="Alice", age=30)
    
    # Create two Pets
    pet1 = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
    pet2 = Pet(name="Whiskers", kind_of_animal="Cat", owner=owner)
    
    # Add pets to owner
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    
    # Create Tasks with different times (all on today's date), intentionally out of order
    today = date.today()
    task_a = Task(description="Walk Buddy", time=datetime.combine(today, datetime.min.time().replace(hour=12)), frequency="daily", pet=pet1)
    task_b = Task(description="Clean Whiskers' litter box", time=datetime.combine(today, datetime.min.time().replace(hour=18)), frequency="daily", pet=pet2)
    task_c = Task(description="Feed Buddy", time=datetime.combine(today, datetime.min.time().replace(hour=8)), frequency="daily", pet=pet1)
    task_d = Task(description="Groom Whiskers", time=datetime.combine(today, datetime.min.time().replace(hour=9)), frequency="weekly", pet=pet2)
    task_e = Task(description="Brush Buddy", time=datetime.combine(today, datetime.min.time().replace(hour=12)), frequency="none", pet=pet1)  # Same time as task_a

    # Add tasks to pets (order intentionally mixed)
    pet1.add_task(task_a)
    pet2.add_task(task_b)
    pet1.add_task(task_c)
    pet2.add_task(task_d)
    pet1.add_task(task_e)
    
    # Create Scheduler
    scheduler = Scheduler(owner)
    
    # Get today's tasks using the new helper
    today_tasks = scheduler.get_today_tasks(on_date=today)

    # Print pet care needs
    print("\nPet Care Needs:")
    for pet in owner.pets:
        print(f"- {pet.name} ({pet.kind_of_animal}): {pet.get_animal_needs()}")

    # Check for same-time conflicts
    print("\nBuddy tasks (pending):")
    buddy_pending = scheduler.filter_tasks(pet_name="Buddy", completed=False)
    for task in buddy_pending:
        print(f"- {task.time.strftime('%H:%M')}: {task.description} (status={task.completion_status})")

    print("\nWhiskers tasks (pending):")
    whiskers_pending = scheduler.filter_tasks(pet_name="Whiskers", completed=False)
    for task in whiskers_pending:
        print(f"- {task.time.strftime('%H:%M')}: {task.description} (status={task.completion_status})")

    # Mark one task done and show completed filter
    task_c.complete_task()
    print("\nCompleted tasks:")
    for task in scheduler.get_tasks_by_status(completed=True):
        print(f"- {task.time.strftime('%H:%M')}: {task.description} for {task.pet.name}")

    # Check for same-time conflicts
    warning = scheduler.check_for_conflicts()
    if warning:
        print(f"\n{warning}")
    else:
        print("\n✅ No conflicts detected.")


if __name__ == "__main__":
    main()

