# ESL Canva Presentation Creator (esl-canva)

## Trigger
User commands `/esl-canva <student_name> <path_to_lesson_plan>`
Example: `/esl-canva Ariel plans/Ariel_Dreams.md`
Or called automatically by `/esl-prep` after the lesson plan is finalized.

## Role
You create a Canva presentation from a finalized ESL lesson plan and organize it into the student's folder.

## Inputs
- **Student name:** Used for the design name and folder lookup.
- **Lesson Plan Path:** A file path to the Markdown file containing the finalized lesson plan (e.g., `plans/Ariel_Dreams.md`).

## Workflow

### 0. Read the Lesson Plan
Use the `Read` tool to open the file specified in the second argument. Extract the exact text from the `## 🖼️ Canva PPT Slide Content` section (Slides 1–5).

### 1. Generate the presentation
**CRITICAL REQUIREMENTS FOR CANVA PRESENTATION:**
1. **Design Style:** Request a clean, educational aesthetic. Use a white background. **Typography Constraints:** Headings MUST be "Century Gothic" font, size 72, and bold. Body text MUST be "Century Gothic" font, size 32. All text should be black. Incorporate two-column tables for vocabulary. Prioritize large headers and bulleted sentence patterns with clear placeholders for student input.
2. **Pass Exact Content:** Use the `generate-design` Canva MCP tool to create a presentation design (`design_type: 'presentation'`). Provide a detailed prompt describing the full slide deck — **CRITICAL: You MUST include the EXACT text for ALL slides (Slides 1–5) extracted from the markdown file in your prompt to Canva**. Do not just ask for a "presentation about [Topic]". You must supply the actual English lesson content, vocabulary, and questions so they appear on the slides.

### 2. Create from candidate
If `generate-design` returns a candidate, use `create-design-from-candidate` to finalize it into an actual Canva design. Save the `design_id`.

### 3. Find or create the student's folder
Use `search-folders` to look for a folder named after the student (e.g., "Ariel"). If it doesn't exist, use `create-folder` to create one (with `parent_folder_id: 'root'`). Save the `folder_id`.

### 4. Move the design into the folder
Use `move-item-to-folder` to move the newly created presentation (using `design_id`) into the student's folder (using `folder_id`).

### 5. Report back
Share the design URL and confirm it's been placed in the student's folder.

## Naming Convention
Name the presentation: `[Student Name] — [Date]`
Example: `Ariel — 2026-04-11`

## Output Format
Confirm completion with:
> ✅ **Canva:** Presentation "[Student Name] — [Date]" created and moved to the "[Student Name]" folder.
> 🔗 [Link to design]
