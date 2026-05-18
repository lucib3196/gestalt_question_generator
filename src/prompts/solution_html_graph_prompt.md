You are generating a `solution.html` file for an engineering problem.

Your goal is to convert a raw problem statement into a structured, step-by-step solution using templated variables and clear reasoning.

---

## INPUT
You will be given:
1. A problem statement (plain text)
2. (Optional) example `solution.html` files

---

## OUTPUT
Return ONLY valid HTML (no explanations, no markdown, no comments).

---

## REQUIREMENTS

### 1. Structure

- Use multiple <pl-hint> blocks to represent each step of the solution
- Each <pl-hint> should contain:
  - A clear step title (optional but preferred)
  - A short explanation
  - Equations if needed

Suggested flow:
1. Given / Known values  
2. Relevant equations  
3. Substitution  
4. Simplification  
5. Final answer  

---

### 2. Parameterization (VERY IMPORTANT)

Replace ALL numeric values with template variables:

- Numbers → \{\{params.variable_name\}\}
- Final answers → \{\{correct_answers.variable_name\}\}
- Units → \{\{params.unitsVariable\}\}

Examples:
- T = {{params.T1}} {{params.unitsTemperature}}
- Final answer: W = {{correct_answers.Work}} {{params.unitsSpecificEnthalpy}}

Use consistent variable names:
- T1, T2, T3  
- Pressure1S, Pressure2S  
- pr  

---

### 3. Step-by-Step Logic

Each <pl-hint> should:
- Contain ONE logical step  
- Be concise and focused  
- Progress naturally toward the solution  
- Avoid large jumps in reasoning  

---

### 4. LaTeX Formatting Rules (STRICT)

- Keep LaTeX formatting minimal.
- ONLY use LaTeX for static mathematical values, symbols, or equations.
- Do NOT wrap dynamic template variables (e.g., `{{params.value}}` or `{{correct_answers.value}}`) in LaTeX formatting, as it causes rendering issues.
- Use $ ... $ for inline math  
- Use $$ ... $$ for display math  
- Do NOT use \( \) or \[ \]  

Examples:

Correct (minimal LaTeX, no LaTeX for params):
P = {{params.Pressure1S}} {{params.unitsPressure}}
the static constant is $k = 1.4$

Display (for static equations only):
$$
W = \int_{V_1}^{V_2} P \, dV
$$

Additional rules:
- Never wrap variables like {{params.*}} or {{correct_answers.*}} in LaTeX math mode  
- Use display math for key static equations and derivations  
- Keep formatting clean and minimal  

---

### 5. Final Answer

- The final <pl-hint> MUST include the final answer  
- Use \{\{correct_answers.variable_name\}\} for answers  
- Include units  

Example:
$$
W = \{\{correct_answers.Work\}\} \\ \text{\{\{params.unitsSpecificEnthalpy\}\}}
$$

---

### 6. Style Rules

- Keep explanations clear and concise  
- Maintain engineering-style reasoning  
- Avoid unnecessary HTML tags  
- Use clean spacing and indentation  
- Do NOT restate the full problem unless necessary  

---

### 7. Consistency

- Follow provided examples EXACTLY if given  
- Preserve the meaning of the original problem  
- Ensure variable naming is consistent across all steps  

---

### 8. Output Validation (STRICT)

- Every numeric value MUST be replaced with \{\{params.*\}\}  
- Every final result MUST use \{\{correct_answers.*\}\}  
- Each step MUST be inside a <pl-hint>  
- Output must be valid, renderable HTML  

---

## EXAMPLE STRUCTURE

<pl-hint>
  <p><strong>step 1: identify known values</strong></p>
  <p>
    the initial temperature is {{params.T1}} {{params.unitsTemperature}} and the pressure is {{params.Pressure1S}} {{params.unitsPressure}}.
  </p>
</pl-hint>

<pl-hint>
  <p><strong>step 2: apply the relevant equation</strong></p>
  $$
  W = m c_p (T_3 - T_1)
  $$
</pl-hint>

<pl-hint>
  <p><strong>step 3: substitute values</strong></p>
  <p>
  W = ({{params.cp}})( {{params.T3}} - {{params.T1}} )
  </p>
</pl-hint>

<pl-hint>
  <p><strong>step 4: final answer</strong></p>
  <p>
  W = {{correct_answers.Work}} {{params.unitsSpecificEnthalpy}}
  </p>
</pl-hint>