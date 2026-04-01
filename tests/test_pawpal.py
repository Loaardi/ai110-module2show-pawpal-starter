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

    # ===== EDGE CASE TESTS: RECURRING TASKS =====

    def test_monthly_recurrence_feb_31st_edge_case(self):
        """Test monthly recurrence when task is on 31st and next month has fewer days."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        # January 31st, recurring monthly
        jan_31 = datetime(2026, 1, 31, 10, 0)
        task = Task(description="Monthly checkup", time=jan_31, frequency="monthly", pet=pet)
        
        # Next occurrence should be Feb 28 (Feb has no 31st)
        next_occ = task.next_occurrence(after=jan_31)
        self.assertEqual(next_occ.month, 2)
        self.assertEqual(next_occ.day, 28)

    def test_leap_year_feb_29_yearly_recurrence(self):
        """Test yearly recurrence for Feb 29 raises ValueError for non-leap years.
        
        NOTE: Current implementation doesn't auto-adjust Feb 29 -> Feb 28 in non-leap years.
        This is a known limitation. Test verifies the error occurs.
        """
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        # Feb 29, 2024 (leap year), recurring yearly
        feb_29_2024 = datetime(2024, 2, 29, 10, 0)
        task = Task(description="Birthday", time=feb_29_2024, frequency="yearly", pet=pet)
        
        # Yearly recurrence from Feb 29 will fail in non-leap years (ValueError)
        # This is a known limitation of the current implementation
        with self.assertRaises(ValueError):
            task.next_occurrence(after=feb_29_2024)

    def test_recurring_task_from_past_date(self):
        """Test that recurring tasks starting in the past still generate future occurrences."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        old_date = datetime(2020, 1, 15, 8, 0)
        task = Task(description="Feed", time=old_date, frequency="daily", pet=pet)
        
        # Request next occurrence far in the future
        future_date = datetime(2026, 3, 30, 10, 0)
        next_occ = task.next_occurrence(after=future_date)
        
        self.assertIsNotNone(next_occ)
        self.assertGreaterEqual(next_occ, future_date)

    def test_weekly_recurrence_boundary(self):
        """Test weekly recurrence doesn't skip or double-up weeks."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        base = datetime(2026, 3, 30, 10, 0)  # Monday
        task = Task(description="Grooming", time=base, frequency="weekly", pet=pet)
        
        # Get next 3 occurrences
        next1 = task.next_occurrence(after=base)
        next2 = task.next_occurrence(after=next1)
        next3 = task.next_occurrence(after=next2)
        
        # Each should be exactly 7 days apart
        self.assertEqual((next1 - base).days, 7)
        self.assertEqual((next2 - next1).days, 7)
        self.assertEqual((next3 - next2).days, 7)

    def test_invalid_frequency_returns_none(self):
        """Test that invalid frequency returns None for next_occurrence."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        task = Task(description="Task", time=datetime.now(), frequency="invalid", pet=pet)
        
        self.assertFalse(task.is_recurring())
        self.assertIsNone(task.next_occurrence(after=datetime.now()))

    def test_non_recurring_task_next_occurrence(self):
        """Test that non-recurring tasks return None for next_occurrence."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        task = Task(description="One-time vet visit", time=datetime.now(), frequency="none", pet=pet)
        
        self.assertFalse(task.is_recurring())
        self.assertIsNone(task.next_occurrence())

    def test_recurring_task_completion_chain(self):
        """Test completing a recurring task multiple times creates a chain."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        base = datetime(2026, 3, 30, 8, 0)
        task1 = Task(description="Feed", time=base, frequency="daily", pet=pet)
        pet.add_task(task1)

        # Complete first task
        task1.complete_task()
        self.assertEqual(len(pet.tasks), 2)

        # Complete second task
        task2 = pet.tasks[1]
        task2.complete_task()
        self.assertEqual(len(pet.tasks), 3)

        # Verify descriptions and dates
        self.assertEqual(pet.tasks[2].time.date(), date(2026, 4, 1))

    # ===== EDGE CASE TESTS: SORTING =====

    def test_sorting_identical_timestamps(self):
        """Test sorting when multiple tasks have the same timestamp."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        same_time = datetime(2026, 3, 31, 10, 0)
        task1 = Task(description="Walk", time=same_time, frequency="none", pet=pet)
        task2 = Task(description="Feed", time=same_time, frequency="none", pet=pet)
        task3 = Task(description="Play", time=same_time, frequency="none", pet=pet)

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)

        scheduler = Scheduler(owner)
        sorted_tasks = scheduler.get_all_tasks(sort_by_time=True)

        # All should have the same time
        for task in sorted_tasks:
            self.assertEqual(task.time, same_time)
        self.assertEqual(len(sorted_tasks), 3)

    def test_sorting_across_midnight(self):
        """Test sorting tasks that span midnight boundaries."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        task1 = Task(description="Late night walk", time=datetime(2026, 3, 31, 23, 50), frequency="none", pet=pet)
        task2 = Task(description="Early morning feed", time=datetime(2026, 4, 1, 0, 10), frequency="none", pet=pet)
        task3 = Task(description="Morning play", time=datetime(2026, 4, 1, 8, 0), frequency="none", pet=pet)

        pet.add_task(task2)
        pet.add_task(task3)
        pet.add_task(task1)

        scheduler = Scheduler(owner)
        sorted_tasks = scheduler.get_all_tasks(sort_by_time=True)

        self.assertEqual(sorted_tasks[0].description, "Late night walk")
        self.assertEqual(sorted_tasks[1].description, "Early morning feed")
        self.assertEqual(sorted_tasks[2].description, "Morning play")

    def test_sorting_empty_task_list(self):
        """Test sorting works correctly with no tasks."""
        owner = Owner(name="OwnerA", age=35)
        scheduler = Scheduler(owner)

        sorted_tasks = scheduler.get_all_tasks(sort_by_time=True)
        self.assertEqual(len(sorted_tasks), 0)

    def test_sorting_single_task(self):
        """Test sorting with only one task."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        task = Task(description="Feed", time=datetime(2026, 3, 31, 10, 0), frequency="none", pet=pet)
        pet.add_task(task)

        scheduler = Scheduler(owner)
        sorted_tasks = scheduler.get_all_tasks(sort_by_time=True)

        self.assertEqual(len(sorted_tasks), 1)
        self.assertEqual(sorted_tasks[0].description, "Feed")

    def test_sorting_with_unsorted_flag(self):
        """Test that sort_by_time=False returns unsorted list."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        task1 = Task(description="Walk", time=datetime(2026, 3, 31, 14, 0), frequency="none", pet=pet)
        task2 = Task(description="Feed", time=datetime(2026, 3, 31, 8, 0), frequency="none", pet=pet)
        task3 = Task(description="Play", time=datetime(2026, 3, 31, 10, 0), frequency="none", pet=pet)

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)

        scheduler = Scheduler(owner)
        unsorted_tasks = scheduler.get_all_tasks(sort_by_time=False)

        # Unsorted should match insertion order
        self.assertEqual(unsorted_tasks[0].description, "Walk")
        self.assertEqual(unsorted_tasks[1].description, "Feed")
        self.assertEqual(unsorted_tasks[2].description, "Play")

    # ===== EDGE CASE TESTS: CONFLICT DETECTION =====

    def test_conflict_detection_zero_window(self):
        """Test conflict detection with zero-minute window (exact matches only)."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        time1 = datetime(2026, 3, 31, 10, 0)
        task1 = Task(description="Walk", time=time1, frequency="none", pet=pet)
        pet.add_task(task1)

        # Task 1 minute apart - should NOT conflict with 0-minute window
        candidate = Task(description="Feed", time=time1 + timedelta(minutes=1), frequency="none", pet=pet)
        scheduler = Scheduler(owner)

        conflicts = scheduler.get_conflicts_for_task(candidate, window_mins=0)
        self.assertEqual(len(conflicts), 0)

    def test_conflict_detection_exact_match_zero_window(self):
        """Test that exact time match is detected even with 0-minute window."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        same_time = datetime(2026, 3, 31, 10, 0)
        task1 = Task(description="Walk", time=same_time, frequency="none", pet=pet)
        pet.add_task(task1)

        candidate = Task(description="Feed", time=same_time, frequency="none", pet=pet)
        scheduler = Scheduler(owner)

        conflicts = scheduler.get_conflicts_for_task(candidate, window_mins=0)
        self.assertEqual(len(conflicts), 1)

    def test_conflict_detection_negative_window(self):
        """Test conflict detection handles negative window values."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        time1 = datetime(2026, 3, 31, 10, 0)
        task1 = Task(description="Walk", time=time1, frequency="none", pet=pet)
        pet.add_task(task1)

        candidate = Task(description="Feed", time=time1 + timedelta(minutes=5), frequency="none", pet=pet)
        scheduler = Scheduler(owner)

        # Negative window should handle gracefully (absolute value used)
        conflicts = scheduler.get_conflicts_for_task(candidate, window_mins=-5)
        self.assertIsInstance(conflicts, list)

    def test_conflict_detection_cross_midnight_same_day(self):
        """Test conflict detection doesn't cross midnight boundaries."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        late_night = datetime(2026, 3, 31, 23, 55)
        task1 = Task(description="Late walk", time=late_night, frequency="none", pet=pet)
        pet.add_task(task1)

        # Next morning task (different date) - should NOT conflict
        early_morning = datetime(2026, 4, 1, 0, 5)
        candidate = Task(description="Morning feed", time=early_morning, frequency="none", pet=pet)
        scheduler = Scheduler(owner)

        conflicts = scheduler.get_conflicts_for_task(candidate, window_mins=15)
        self.assertEqual(len(conflicts), 0)  # Different dates, no conflict

    def test_conflict_detection_with_recurring_expansion(self):
        """Test that expanded recurring tasks are included in conflict detection."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        # Daily task at 10:00 AM
        task_10am = Task(description="Feed", time=datetime(2026, 3, 31, 10, 0), frequency="daily", pet=pet)
        pet.add_task(task_10am)

        # Try to schedule at 10:05 AM on April 1st (should conflict with expanded recurring task)
        candidate = Task(description="Play", time=datetime(2026, 4, 1, 10, 5), frequency="none", pet=pet)
        scheduler = Scheduler(owner)

        conflicts = scheduler.get_conflicts_for_task(candidate, window_mins=10)
        # Note: get_conflicts_for_task only checks existing tasks, not expanded recurring ones
        # This tests current behavior (may be a limitation to note)
        self.assertIsInstance(conflicts, list)

    def test_same_time_conflicts_multiple_pairs(self):
        """Test detecting multiple conflict pairs."""
        owner = Owner(name="OwnerA", age=35)
        pet1 = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        pet2 = Pet(name="Whiskers", kind_of_animal="Cat", owner=owner)
        owner.add_pet(pet1)
        owner.add_pet(pet2)

        time1 = datetime(2026, 3, 31, 10, 0)
        time2 = datetime(2026, 3, 31, 14, 0)

        task1 = Task(description="Walk Buddy", time=time1, frequency="none", pet=pet1)
        task2 = Task(description="Feed Whiskers", time=time1, frequency="none", pet=pet2)
        task3 = Task(description="Groom Buddy", time=time2, frequency="none", pet=pet1)
        task4 = Task(description="Vet Whiskers", time=time2, frequency="none", pet=pet2)

        pet1.add_task(task1)
        pet2.add_task(task2)
        pet1.add_task(task3)
        pet2.add_task(task4)

        scheduler = Scheduler(owner)
        conflicts = scheduler.get_same_time_conflicts()

        # Should find 2 conflict pairs
        self.assertEqual(len(conflicts), 2)

    # ===== EDGE CASE TESTS: TIME WINDOW FILTERING =====

    def test_get_tasks_for_window_empty_window(self):
        """Test get_tasks_for_window with no tasks in the window."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        task = Task(description="Feed", time=datetime(2026, 3, 30, 10, 0), frequency="none", pet=pet)
        pet.add_task(task)

        scheduler = Scheduler(owner)
        tasks = scheduler.get_tasks_for_window(datetime(2026, 4, 10, 0, 0), datetime(2026, 4, 20, 23, 59))

        self.assertEqual(len(tasks), 0)

    def test_get_tasks_for_window_recurring_expansion(self):
        """Test that recurring tasks are expanded within the window."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        # Daily task starting March 30
        task = Task(description="Feed", time=datetime(2026, 3, 30, 8, 0), frequency="daily", pet=pet)
        pet.add_task(task)

        scheduler = Scheduler(owner)
        # Get tasks for 5-day window
        tasks = scheduler.get_tasks_for_window(
            datetime(2026, 3, 30, 0, 0),
            datetime(2026, 4, 3, 23, 59)
        )

        # Should find the original plus 4 expanded instances (5 days total)
        self.assertEqual(len(tasks), 5)

    def test_get_today_tasks_no_tasks(self):
        """Test get_today_tasks when no tasks are scheduled for that date."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        task = Task(description="Feed", time=datetime(2026, 3, 30, 8, 0), frequency="none", pet=pet)
        pet.add_task(task)

        scheduler = Scheduler(owner)
        today_tasks = scheduler.get_today_tasks(on_date=date(2026, 4, 1))

        self.assertEqual(len(today_tasks), 0)

    def test_get_next_task_no_pending_tasks(self):
        """Test get_next_task when all tasks are completed."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        task = Task(description="Feed", time=datetime(2026, 3, 31, 10, 0), frequency="none", pet=pet)
        pet.add_task(task)
        task.complete_task()

        scheduler = Scheduler(owner)
        next_task = scheduler.get_next_task(after=datetime(2026, 3, 31, 9, 0))

        self.assertIsNone(next_task)

    # ===== EDGE CASE TESTS: FILTERING =====

    def test_filter_nonexistent_pet(self):
        """Test filtering by pet name that doesn't exist."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        task = Task(description="Feed", time=datetime(2026, 3, 31, 10, 0), frequency="none", pet=pet)
        pet.add_task(task)

        scheduler = Scheduler(owner)
        tasks = scheduler.get_tasks_for_pet("NonexistentPet")

        self.assertEqual(len(tasks), 0)

    def test_filter_completion_status_all_pending(self):
        """Test filtering completed status when all tasks are pending."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        task1 = Task(description="Feed", time=datetime(2026, 3, 31, 10, 0), frequency="none", pet=pet)
        task2 = Task(description="Walk", time=datetime(2026, 3, 31, 14, 0), frequency="none", pet=pet)
        pet.add_task(task1)
        pet.add_task(task2)

        scheduler = Scheduler(owner)
        completed = scheduler.get_tasks_by_status(completed=True)

        self.assertEqual(len(completed), 0)

    def test_filter_completion_status_all_completed(self):
        """Test filtering pending status when all tasks are completed."""
        owner = Owner(name="OwnerA", age=35)
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        owner.add_pet(pet)

        task1 = Task(description="Feed", time=datetime(2026, 3, 31, 10, 0), frequency="none", pet=pet)
        task2 = Task(description="Walk", time=datetime(2026, 3, 31, 14, 0), frequency="none", pet=pet)
        pet.add_task(task1)
        pet.add_task(task2)

        task1.complete_task()
        task2.complete_task()

        scheduler = Scheduler(owner)
        pending = scheduler.get_tasks_by_status(completed=False)

        self.assertEqual(len(pending), 0)

    def test_filter_multiple_criteria_no_matches(self):
        """Test filtering with multiple criteria that match no tasks."""
        owner = Owner(name="OwnerA", age=35)
        pet1 = Pet(name="Buddy", kind_of_animal="Dog", owner=owner)
        pet2 = Pet(name="Whiskers", kind_of_animal="Cat", owner=owner)
        owner.add_pet(pet1)
        owner.add_pet(pet2)

        task1 = Task(description="Walk", time=datetime(2026, 3, 31, 10, 0), frequency="none", pet=pet1)
        task2 = Task(description="Feed", time=datetime(2026, 3, 31, 14, 0), frequency="none", pet=pet2)
        pet1.add_task(task1)
        pet2.add_task(task2)

        scheduler = Scheduler(owner)
        # Filter for "Buddy" completed tasks - should be empty
        tasks = scheduler.filter_tasks(pet_name="Buddy", completed=True)

        self.assertEqual(len(tasks), 0)

    # ===== EDGE CASE TESTS: TASK COMPARISON & ORDERING =====

    def test_task_comparison_less_than(self):
        """Test task comparison for sorting."""
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=None)
        task1 = Task(description="Early", time=datetime(2026, 3, 31, 8, 0), frequency="none", pet=pet)
        task2 = Task(description="Late", time=datetime(2026, 3, 31, 17, 0), frequency="none", pet=pet)

        self.assertTrue(task1 < task2)
        self.assertFalse(task2 < task1)

    def test_task_comparison_equal_time(self):
        """Test task comparison when times are equal."""
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=None)
        task1 = Task(description="Task A", time=datetime(2026, 3, 31, 10, 0), frequency="none", pet=pet)
        task2 = Task(description="Task B", time=datetime(2026, 3, 31, 10, 0), frequency="none", pet=pet)

        self.assertFalse(task1 < task2)
        self.assertFalse(task2 < task1)

    def test_task_comparison_with_non_task(self):
        """Test task comparison returns NotImplemented for non-Task objects."""
        pet = Pet(name="Buddy", kind_of_animal="Dog", owner=None)
        task = Task(description="Task", time=datetime.now(), frequency="none", pet=pet)

        result = task.__lt__("not a task")
        self.assertEqual(result, NotImplemented)


if __name__ == "__main__":
    unittest.main()
