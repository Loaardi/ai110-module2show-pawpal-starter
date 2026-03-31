import unittest
from datetime import datetime
from pawpal_system import Task, Pet


class TestPawPal(unittest.TestCase):

    def test_task_completion(self):
        """Verify that calling complete_task() changes the task's completion status."""
        # Create a pet (owner can be None for this test)
        pet = Pet(name="TestPet", kind_of_animal="Dog", owner=None)
        
        # Create a task
        task = Task(
            description="Test Task",
            time=datetime.now(),
            frequency="daily",
            pet=pet
        )
        
        # Initially, task should not be completed
        self.assertFalse(task.completion_status)
        
        # Mark the task as complete
        task.complete_task()
        
        # Now, task should be completed
        self.assertTrue(task.completion_status)

    def test_task_addition(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        # Create a pet
        pet = Pet(name="TestPet", kind_of_animal="Dog", owner=None)
        
        # Get initial task count
        initial_count = len(pet.tasks)
        
        # Create a task
        task = Task(
            description="Test Task",
            time=datetime.now(),
            frequency="daily",
            pet=pet
        )
        
        # Add the task to the pet
        pet.add_task(task)
        
        # Verify the task count increased by 1
        self.assertEqual(len(pet.tasks), initial_count + 1)


if __name__ == "__main__":
    unittest.main()
