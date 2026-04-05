# Project: Personalized ESL Agent (Local V2)

## 1. Overview
This is a local CLI-based agent designed to generate personalized ESL lesson plans.
Unlike a simple script, this agent must perform a **Diagnostic Reasoning Loop** before generating content.

## 2. Constraints & Privacy
- **Local Only:** All student data is stored in local Markdown files.
- **External Integrations:** Canva (via MCP) for presentation creation. No other external APIs.

## 3. Core Workflow (The Agentic Loop)
The generic flow for every request:
1. **User Input:** "/plan [StudentName]"
2. **Tool Call:** `get_student_profile(name)` (MUST be called first)
3. **Diagnostic Phase (CRITICAL):**
   - The Agent must output a specific "Diagnostic Block" analyzing the student's `error_patterns` and `last_lesson`.
   - Decide: Review (Conservative) vs. New Topic (Progressive).
4. **Content Generation:**
   - Mimic "Elli-style" content (discussion-heavy, functional).
   - Generate slides in Markdown table format.
5. **Output:** Display the plan to the user.

## 4. File Structure
- `main.py`: The entry point (CLI loop using `rich` or simple `input()`).
- `agent_logic.py`: Contains the LLM interaction logic (using Anthropic API).
- `data_manager.py`: Handles reading/writing local files.
- `students/`: Directory to store student profiles.
  - Schema: `{name}.json`
    - `name`: str
    - `cefr_level`: str
    - `interests`: list[str]
    - `weaknesses`: list[str] (e.g., "Past Tense", "Pronunciation of 'th'")
    - `last_lesson`: str
    - `goals`: str

## 5. System Prompt Requirements
The System Prompt must enforce the "Diagnostic Phase".
It should explicitly forbid generating lesson content until the student profile is loaded and analyzed.

## 6. Tool Definitions (Skills)
The `agent_logic.py` must implement the **Anthropic Tool Use Loop**. 
Do not use simple text generation; use the `client.messages.create(..., tools=[...])` API.

### Python CLI Tools:
1.  **`get_student_profile`**
    -   **Purpose:** Retrieves the JSON data for a specific student.
    -   **Input:** `student_name` (string)
    -   **Output:** The content of the JSON file or an error message if not found.
    -   **Function Logic:** Located in `data_manager.py`.

2.  **`save_lesson_plan`**
    -   **Purpose:** Saves the generated markdown plan to a local file.
    -   **Input:** `student_name` (string), `content` (string)
    -   **Output:** "Success: Saved to plans/{student_name}_{date}.md"
    -   **Function Logic:** Located in `data_manager.py`.

### Claude Code Skills:
3.  **`/esl-prep`** (Orchestrator)
    -   **Purpose:** Full lesson prep pipeline — gathers student info, then delegates.
    -   **Input:** `student_name`, `topic_or_materials_path`
    -   **Flow:** Read student profile + Elli PDF → `/esl-plan` → `/esl-canva`
    -   **Prompt:** `prompts/esl-prep.md`

4.  **`/esl-plan`** (Lesson Plan + QA)
    -   **Purpose:** Generates a QA-checked lesson plan with exact Canva slide content.
    -   **Input:** `student_name`, `topic_or_materials_path`
    -   **Flow:** PPT framework mapping → Draft → QA self-check → Output
    -   **Prompt:** `prompts/esl-plan.md`

5.  **`/esl-canva`** (Canva Presentation)
    -   **Purpose:** Creates a Canva presentation and files it in the student's folder.
    -   **Input:** `student_name` (slide content from conversation context)
    -   **Flow:** `generate-design` → `create-design-from-candidate` → `search-folders` / `create-folder` → `move-item-to-folder`
    -   **Naming:** `[Student] — [Date]`
    -   **Prompt:** `prompts/esl-canva.md`

### The Tool Loop Logic (In `agent_logic.py`):
1.  Send user message to Claude.
2.  Check `stop_reason`.
3.  If `stop_reason` is `tool_use`:
    -   Extract tool name and arguments.
    -   Call the corresponding Python function.
    -   **CRITICAL:** Send the tool result *back* to Claude as a new message with role `user` and content type `tool_result`.
4.  Repeat until `stop_reason` is `end_turn`.