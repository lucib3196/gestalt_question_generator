You are generating a JavaScript file that computes parameters and correct answers for an engineering problem.

Your goal is to convert a given question into a structured `generate()` function that:
- Randomizes inputs
- Computes all required intermediate variables
- Computes final answers
- Returns a properly formatted `data` object

---

## INPUT
You will be given:
1. A question (HTML format)
2. (Optional) example JavaScript files

---

## OUTPUT
Return ONLY valid JavaScript code (no explanations, no markdown, no comments unless necessary).

---

## REQUIREMENTS

### 1. File Structure

Your output must follow this structure:

- Import required libraries (e.g., `mathjs`)
- Define a `generate()` function
- Define units and unit systems (if applicable)
- Generate random parameters
- Perform calculations step-by-step
- Store results in a `data` object
- Return `data`
- Export the function

---

### 2. Core Function

- All logic must be inside `generate()`
- Keep the flow structured and sequential
- Do not skip steps

---

### 3. Parameters (`params`)

All given values and useful intermediate variables must go inside:

```js
params: {
  ...
}
```

Include:
- Randomized inputs
- Intermediate values (if helpful for solution rendering)
- Units (e.g., `unitsDist`, `unitsTime`, etc.)

---

### 4. Answers (`correct_answers`)

All final computed results must go inside:

```js
correct_answers: {
  ...
}
```

- Use clear variable names
- Match names expected by the question HTML

---

### 5. Randomization

- Use `math.randomInt()` or similar
- Ensure values are valid and realistic
- Avoid edge cases that break the problem

---

### 6. Units Handling

If units are present:
- Define a `units` object
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

```js
data = {
  params: { ... },
  correct_answers: { ... },
  nDigits: 2,
  sigfigs: 2
}
```

---

### 10. Consistency

- Follow provided examples if given
- Ensure variable naming aligns with the question
- Ensure outputs match expected answers

---

## EXAMPLE STRUCTURE (HIGH LEVEL)

```javascript
const math = require('mathjs');

const generate = () => {

  // -----------------------------
  // 1. Select unit system
  // -----------------------------
  const unitSystems = ['si', 'uscs'];
  const unitSel = math.randomInt(0, 2);

  const units = {
    si: {
      dist: "m",
      time: "s"
    },
    uscs: {
      dist: "ft",
      time: "s"
    }
  };

  const unitsDist = units[unitSystems[unitSel]].dist;
  const unitsTime = units[unitSystems[unitSel]].time;

  // -----------------------------
  // 2. Generate random parameters
  // -----------------------------
  const speed = math.randomInt(10, 100);
  const time = math.randomInt(1, 10);

  // -----------------------------
  // 3. Perform calculations
  // -----------------------------
  const distance = speed * time;

  // -----------------------------
  // 4. Format output
  // -----------------------------
  const data = {
    params: {
      speed: speed,
      time: time,
      unitsDist: unitsDist,
      unitsTime: unitsTime
    },

    correct_answers: {
      distance: distance
    },

    nDigits: 2,
    sigfigs: 2
  };

  return data;
};

module.exports = {
  generate
};
```

---

## GOAL

Produce clean, structured, and reusable JavaScript code that integrates directly with the question and solution system.