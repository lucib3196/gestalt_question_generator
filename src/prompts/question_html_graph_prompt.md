You are generating a `question.html` file for an engineering problem.

Your goal is to convert a raw problem statement into a structured HTML question using templated variables and input components.

---

## INPUT
You will be given:
1. A problem statement (plain text)
2. (Optional) example `question.html` files

---

## OUTPUT
Return ONLY valid HTML (no explanations, no markdown, no comments).

---

## REQUIREMENTS

### 1. Structure
Use the following structure:

- <pl-question-panel> → contains the full problem statement
- Use clean paragraph formatting with <p>
- Place input fields AFTER the problem statement

---

### 2. Parameterization (VERY IMPORTANT)

Replace ALL numeric values with template variables:

- Numbers → {{params.variable_name}}
- Units → {{params.unitsVariable}}

Examples:
- 300 K → ${{params.T1}}\ {{params.unitsTemperature}}$
- 2.5 bar → ${{params.Pressure1S}}\ {{params.unitsPressure}}$

Use clear, consistent variable names:
- T1, T2, T3 (temperatures)
- Pressure1S, Pressure2S (pressures)
- pr (pressure ratio)
- etc.

---

### 3. Inputs

For any quantity the user must solve for:

Use:
<pl-number-input 
    answers-name="variable_name" 
    comparison="sigfig" 
    digits="3" 
    label="clear label with units (in {{params.units...}})">
</pl-number-input>

Rules:
- answers-name MUST match {{correct_answers.variable_name}}
- Labels must include units using params
- Keep labels concise and lowercase

---

### 4. LaTeX Formatting Rules (STRICT)

- Use $ ... $ for inline math
- Use $$ ... $$ for display (block) math
- Do NOT use \( \) or \[ \]

Examples:

Inline:
the pressure is $P = {{params.Pressure1S}}\ \text{{{{params.unitsPressure}}}}$

Display:
$$
W = \int_{{V_1}}^{{V_2}} P \, dV
$$

Additional rules:
- Always wrap variables and values in LaTeX math mode
- Use \text for units inside math
- Use inline math for values and variables in sentences
- Use display math only for important equations or derivations
- Keep formatting clean and minimal

---

### 5. Style Rules

- Keep wording natural but slightly cleaned (do NOT heavily rewrite)
- Maintain engineering-style clarity
- Avoid unnecessary tags (no <div> unless needed)
- Ensure clean spacing and indentation
- Keep everything concise and readable

---

### 6. Consistency

- Follow provided examples EXACTLY if given
- Preserve the meaning of the original problem
- Ensure consistent variable naming throughout

---

### 7. Output Validation (STRICT)

- Every numeric value MUST be replaced with {{params.*}}
- Every required answer MUST have a corresponding input field
- answers-name MUST align with {{correct_answers.*}}
- Output must be valid, renderable HTML

---

## EXAMPLE TRANSFORMATION

Input:
"air enters the compressor at 2.5 bar and 300 K. pressure ratio is 4. max temperature is 1200 K."

Output:
<pl-question-panel>
  <p>
    air enters the compressor at ${{params.Pressure1S}}\ \text{{{{params.unitsPressure}}}}$ and ${{params.T1}}\ \text{{{{params.unitsTemperature}}}}$.
  </p>
  <p>
    the pressure ratio is ${{params.pr}}$ and the maximum temperature is ${{params.T3}}\ \text{{{{params.unitsTemperature}}}}$.
  </p>
</pl-question-panel>

<p>determine the work output and heat input.</p>

<pl-number-input 
    answers-name="Work" 
    comparison="sigfig" 
    digits="3" 
    label="work output (in {{params.unitsSpecificEnthalpy}})">
</pl-number-input>

<pl-number-input 
    answers-name="Qin" 
    comparison="sigfig" 
    digits="3" 
    label="heat input (in {{params.unitsSpecificEnthalpy}})">
</pl-number-input>