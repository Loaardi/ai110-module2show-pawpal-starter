# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
Each owner manages one schedule and can have multiple pets. Each pet requires multiple tasks, and the schedule contains all tasks. This structure enables the app to assign, track, and prioritize pet care activities for each owner's pets.

- What classes did you include, and what responsibilities did you assign to each?
class Task:
   Represents a pet care task with priority and due date.
   Mark this task as complete.
   Return the priority level of this task.

class Pet:
    Represents a pet with its attributes and care information.
    Return the type of animal this pet is.
    Return the care needs for this animal.
    Return the priority level for this pet's care.

class Schedule:
    Manages a calendar of tasks for pet care.
    Initialize the schedule with an empty calendar.
    Add a task to the schedule.
    Remove a task from the schedule.
    Display the current schedule.

class Owner:
    Represents a pet owner with basic information.
    Initialize an owner with name and age.
    Return the owner's name.
    Return the owner's age.    

**b. Design changes**

- Did your design change during implementation?
Yes

- If yes, describe at least one change and why you made it.
add completed for task class.
---
add the pet, see schedule, see why it is important thee order.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
