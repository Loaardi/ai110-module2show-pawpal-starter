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
    
    # Create Tasks with different times (all on today's date)
    today = date.today()
    task1 = Task(description="Feed Buddy", time=datetime.combine(today, datetime.min.time().replace(hour=8)), frequency="daily", pet=pet1)
    task2 = Task(description="Walk Buddy", time=datetime.combine(today, datetime.min.time().replace(hour=12)), frequency="daily", pet=pet1)
    task3 = Task(description="Clean Whiskers' litter box", time=datetime.combine(today, datetime.min.time().replace(hour=18)), frequency="daily", pet=pet2)
    
    # Add tasks to pets
    pet1.add_task(task1)
    pet1.add_task(task2)
    pet2.add_task(task3)
    
    # Create Scheduler
    scheduler = Scheduler(owner)
    
    # Get today's tasks
    all_tasks = scheduler.get_all_tasks()
    today_tasks = [task for task in all_tasks if task.time.date() == today]
    
    # Print Today's Schedule
    print("Today's Schedule:")
    if today_tasks:
        for task in sorted(today_tasks, key=lambda t: t.time):
            print(f"- {task.time.strftime('%H:%M')}: {task.description} for {task.pet.name}")
    else:
        print("No tasks for today.")


if __name__ == "__main__":
    main()

