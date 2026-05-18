You are generating a Python file that computes parameters and correct answers for an engineering problem.

Your goal is to convert a given question into a structured `generate()` function that:
- Randomizes inputs
- Computes all required intermediate variables
- Computes final answers
- Returns a properly formatted `data` dictionary

---

## INPUT
You will be given:
1. A question (HTML format)
2. (Optional) example Python files

---

## OUTPUT
Return ONLY valid Python code (no explanations, no markdown, no comments unless necessary).

---

## REQUIREMENTS

### 1. File Structure

Your output must follow this structure:

- Import required libraries (e.g., `random`, `math`)
- Define a `generate()` function
- Define units and unit systems (if applicable)
- Generate random parameters
- Perform calculations step-by-step
- Store results in a `data` dictionary
- Return `data`

---

### 2. Core Function

- All logic must be inside `generate()`
- Keep the flow structured and sequential
- Do not skip steps

---

### 3. Parameters (`params`)

All given values and useful intermediate variables must go inside:

```python
"params": {
    ...
}
```

Include:
- Randomized inputs
- Intermediate values (if helpful for solution rendering)
- Units (e.g., `units_dist`, `units_time`, etc.)

---

### 4. Answers (`correct_answers`)

All final computed results must go inside:

```python
"correct_answers": {
    ...
}
```

- Use clear variable names
- Match names expected by the question HTML

---

### 5. Randomization

- Use `random.randint()` or similar methods
- Ensure values are valid and realistic
- Avoid edge cases that break the problem

---

### 6. Units Handling

If units are present:
- Define a `units` dictionary
- Support multiple systems (e.g., `si`, `uscs`)
- Select one randomly
- Assign unit variables

---

### 7. Calculations

- Break calculations into clear steps
- Store intermediate variables
- Use correct engineering relationships
- Keep logic readable

---

### 8. Formatting & Style

- Use clean indentation
- Use descriptive variable names
- Avoid unnecessary complexity
- Keep code minimal and structured

---

### 9. Output Object

Your function must return:

```python
data = {
    "params": { ... },
    "correct_answers": { ... },
    "nDigits": 2,
    "sigfigs": 2
}
```

---

### 10. Consistency

- Follow provided examples if given
- Ensure variable naming aligns with the question
- Ensure outputs match expected answers

---

## EXAMPLE STRUCTURE (HIGH LEVEL)

```python
import random
import math

def generate():

    # -----------------------------
    # 1. Select unit system
    # -----------------------------
    unit_systems = ['si', 'uscs']
    unit_sel = random.randint(0, 1)

    units = {
        "si": {
            "dist": "m",
            "time": "s"
        },
        "uscs": {
            "dist": "ft",
            "time": "s"
        }
    }

    units_dist = units[unit_systems[unit_sel]]["dist"]
    units_time = units[unit_systems[unit_sel]]["time"]

    # -----------------------------
    # 2. Generate random parameters
    # -----------------------------
    speed = random.randint(10, 100)
    time = random.randint(1, 10)

    # -----------------------------
    # 3. Perform calculations
    # -----------------------------
    distance = speed * time

    # -----------------------------
    # 4. Format output
    # -----------------------------
    data = {
        "params": {
            "speed": speed,
            "time": time,
            "unitsDist": units_dist,
            "unitsTime": units_time
        },
        "correct_answers": {
            "distance": distance
        },
        "nDigits": 2,
        "sigfigs": 2
    }

    return data
```

---

## GOAL

Produce clean, structured, and reusable Python code that integrates directly with the question and solution system.