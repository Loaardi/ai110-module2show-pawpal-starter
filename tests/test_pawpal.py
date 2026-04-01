import unittest
from datetime import datetime, timedelta, date
from pawpal_system import Task, Pet, Owner, Scheduler


class TestPawPal(unittest.TestCase):
    def test_task_completion(self):
        pet = Pet(name="TestPet", kind_of_animal="Dog", owner=None)
        task = Task(description="Test Task", time=datetime.now(), frequency="daily", pet=pet)
        self.assertFalse(task.completion_status)
        task.complete_task()
        self.assertTrue(task.completion_status)

    def test_task_addition(self):
        pet = Pet(name="TestPet", kind_of_animal="Dog", owner=None)
        initial_count = len(pet.tasks)
        task = Task(description="Test Task", time=datetime.now(), frequency="daily", pet=pet)
        pet.add_task(task)
        self.assertEqual(len(pet.tasks), initial_count + 1)

    def test_animal_needs(self):
        dog = Pet(name="Buddy", kind_of_animal="Dog", owner=None)
        cat = Pet(name="Whiskers", kind_of_animal="Cat", owner=None)
        unknown = Pet(name="Mystery", kind_of_animal="Alien", owner=None)

        self.assertIn("Daily walks", dog.get_animal_needs())
        self.assertIn("Litter box", cat.get_animal_needs())
        self.assertEqual("Basic care for Alien", unknown.get_animal_needs())

    def test_scheduler_sorting_and_filtering(self):
        owner = Owner(name="OwnerA", age=35)
        pet1 = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        pet2 = Pet(name="Whiskers", kind_of_animal="Cat", owner=owner)
        owner.add_pet(pet1)
        owner.add_pet(pet2)

        now = datetime(2026, 3, 30, 9, 0)
        task1 = Task(description="Walk", time=now + timedelta(hours=2), frequency="daily", pet=pet1)
        task2 = Task(description="Feed", time=now + timedelta(hours=1), frequency="daily", pet=pet2)
        task3 = Task(description="Vet", time=now + timedelta(hours=3), frequency="none", pet=pet1)

        pet1.add_task(task1)
        pet1.add_task(task3)
        pet2.add_task(task2)

        scheduler = Scheduler(owner)

        all_tasks = scheduler.get_all_tasks()
        self.assertEqual([t.description for t in all_tasks], ["Feed", "Walk", "Vet"])

        buddy_tasks = scheduler.get_tasks_for_pet("Buddy")
        self.assertEqual([t.description for t in buddy_tasks], ["Walk", "Vet"])

        pending_tasks = scheduler.get_tasks_by_status(completed=False)
        self.assertEqual(len(pending_tasks), 3)

        task2.complete_task()
        completed = scheduler.get_tasks_by_status(completed=True)
        self.assertEqual(len(completed), 1)

        buddy_pending = scheduler.filter_tasks(pet_name="Buddy", completed=False)
        self.assertEqual([t.description for t in buddy_pending], ["Walk", "Vet"])

        cat_completed = scheduler.filter_tasks(pet_name="Whiskers", completed=True)
        self.assertEqual(len(cat_completed), 1)

    def test_recurring_task_next_occurrence_and_today_tasks(self):
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        base = datetime(2026, 3, 30, 8, 0)
        daily_task = Task(description="Feed", time=base, frequency="daily", pet=pet)
        pet.add_task(daily_task)

        scheduler = Scheduler(owner)
        next_occ = daily_task.next_occurrence(after=base + timedelta(hours=1))
        self.assertEqual(next_occ.date(), date(2026, 3, 31))

        today_tasks = scheduler.get_today_tasks(on_date=date(2026, 3, 30))
        self.assertEqual(len(today_tasks), 1)

        tomorrow_tasks = scheduler.get_today_tasks(on_date=date(2026, 3, 31))
        self.assertEqual(len(tomorrow_tasks), 1)

    def test_recurring_task_auto_add_next_on_complete(self):
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        base = datetime(2026, 3, 30, 8, 0)
        recurring = Task(description="Feed", time=base, frequency="daily", pet=pet)
        pet.add_task(recurring)

        recurring.complete_task()

        # original is complete
        self.assertTrue(recurring.completion_status)

        # a new task should be added for next day
        all_tasks = pet.get_tasks()
        self.assertEqual(len(all_tasks), 2)
        next_task = [t for t in all_tasks if t is not recurring][0]
        self.assertEqual(next_task.frequency, "daily")
        self.assertEqual(next_task.description, "Feed")
        self.assertEqual(next_task.completion_status, False)
        self.assertEqual(next_task.time.date(), date(2026, 3, 31))

    def test_conflict_detection(self):
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        time1 = datetime(2026, 3, 31, 10, 0)
        task1 = Task(description="Walk", time=time1, frequency="none", pet=pet)
        pet.add_task(task1)

        candidate = Task(description="Vaccine", time=time1 + timedelta(minutes=3), frequency="none", pet=pet)
        scheduler = Scheduler(owner)

        conflicts = scheduler.get_conflicts_for_task(candidate, window_mins=5)
        self.assertEqual(len(conflicts), 1)
        self.assertTrue(scheduler.has_conflict(candidate, window_mins=5))

    def test_same_time_conflicts(self):
        owner = Owner(name="OwnerA", age=35)
        pet1 = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        pet2 = Pet(name="Whiskers", kind_of_animal="Cat", owner=owner)
        owner.add_pet(pet1)
        owner.add_pet(pet2)

        same_time = datetime(2026, 3, 31, 10, 0)
        task1 = Task(description="Walk Buddy", time=same_time, frequency="none", pet=pet1)
        task2 = Task(description="Feed Whiskers", time=same_time, frequency="none", pet=pet2)
        task3 = Task(description="Groom Buddy", time=same_time + timedelta(hours=1), frequency="none", pet=pet1)

        pet1.add_task(task1)
        pet2.add_task(task2)
        pet1.add_task(task3)

        scheduler = Scheduler(owner)

        conflicts = scheduler.get_same_time_conflicts()
        self.assertEqual(len(conflicts), 1)
        self.assertIn((task1, task2), conflicts)
        self.assertTrue(scheduler.has_same_time_conflicts())

        # No conflicts if times differ
        task2.time = same_time + timedelta(minutes=30)
        conflicts_after = scheduler.get_same_time_conflicts()
        self.assertEqual(len(conflicts_after), 0)
        self.assertFalse(scheduler.has_same_time_conflicts())

    def test_check_for_conflicts(self):
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        # No conflicts initially
        scheduler = Scheduler(owner)
        self.assertIsNone(scheduler.check_for_conflicts())

        # Add conflicting tasks
        same_time = datetime(2026, 3, 31, 10, 0)
        task1 = Task(description="Walk", time=same_time, frequency="none", pet=pet)
        task2 = Task(description="Feed", time=same_time, frequency="none", pet=pet)
        pet.add_task(task1)
        pet.add_task(task2)

        warning = scheduler.check_for_conflicts()
        self.assertIsNotNone(warning)
        self.assertIn("Warning", warning)
        self.assertIn("1 task(s)", warning)


if __name__ == "__main__":
    unittest.main()
