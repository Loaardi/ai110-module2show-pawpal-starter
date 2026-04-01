# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

This implementation includes advanced scheduling features for better pet care management:

- **Time-based Sorting**: Tasks are automatically sorted by time for clear daily plans.
- **Flexible Filtering**: Filter tasks by pet name, completion status, or both.
- **Recurring Tasks**: Support for daily, weekly, monthly, and yearly tasks with automatic next-occurrence generation on completion.
- **Conflict Detection**: Detect same-time conflicts or overlaps within a time window, with lightweight warning messages.
- **Animal-Specific Care**: Tailored care recommendations based on pet type (e.g., walks for dogs, litter cleaning for cats).

## Features (implemented algorithms)

- Task tracking with `Task` entities, status updates (`complete_task()`), priority, and due date.
- Pet model with `get_animal_needs()` and placeholder `get_priority()`.
- Owner model with pet collection, owned schedule, and `get_all_tasks()` aggregator.
- Schedule manager with a calendar map and methods: `add_task()`, `remove_task()`, `view_schedule()`.
- Sorting by task time in `Scheduler.get_all_tasks()` and related fetch methods.
- Recurrence support (`Task.is_recurring()`, `Task.next_occurrence()`, `get_tasks_for_window()`, `get_today_tasks()`).
- Conflict warnings via `get_conflicts_for_task()`, `has_conflict()`, and `check_for_conflicts()`.
- Filtering by pet and status in `Scheduler.filter_tasks()`.
- Next task lookup through `Scheduler.get_next_task()`.
- Streamlit UI integration for owner/pet creation, task management, schedule viewing, and completion actions.

## 📸 Demo


<a href="/course_images/ai110/image.png" target="_blank"><img src='/course_images/ai110/image.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

The test suite validates core scheduling functionality and edge cases critical to pet care management.

### Run tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### Test coverage

**38 comprehensive tests** covering:

- **Recurring Tasks**: Daily, weekly, monthly, yearly frequencies; edge cases like Feb 31st adjustments, recurring task chains, and past-date initialization
- **Sorting**: Tasks with identical timestamps, midnight boundary crossing, empty/single-item lists, and insertion order preservation
- **Conflict Detection**: Exact time matches, zero/negative time windows, cross-midnight boundaries, and multiple conflict pairs
- **Filtering & Status**: Pet name and completion status filtering, all-pending/all-completed scenarios, and multi-criteria filters
- **Time Windows**: Task expansion within date ranges, today's tasks with recurring expansions, and empty windows
- **Task Comparison**: Ordering operations, equal-time stability, and type checking

These tests ensure robust behavior across real-world scheduling scenarios while documenting known limitations (e.g., leap year Feb 29 yearly recurrence).

