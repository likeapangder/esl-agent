# ESL Canva Presentation Creator (esl-canva)

## Trigger
User commands `/esl-canva <student_name>`
Or called automatically by `/esl-prep` after the lesson plan is finalized.

## Role
You create a Canva presentation from a finalized ESL lesson plan and organize it into the student's folder.

## Inputs
- **Student name:** Used for the design name and folder lookup.
- **Slide content:** The finalized Canva PPT slide content from the lesson plan (Slides 1–5). This should already be available in the conversation from `/esl-plan` output, or the user can provide it.

## Workflow

### 1. Generate the presentation
Use the `generate-design` Canva MCP tool to create a presentation design. Provide a detailed prompt describing the full slide deck — include all slide content (Slides 1–5) from the lesson plan. Request a "presentation" format.

### 2. Create from candidate
If `generate-design` returns a candidate, use `create-design-from-candidate` to finalize it into an actual Canva design.

### 3. Find or create the student's folder
Use `search-folders` to look for a folder named after the student (e.g., "Hsuan"). If it doesn't exist, use `create-folder` to create one.

### 4. Move the design into the folder
Use `move-item-to-folder` to move the newly created presentation into the student's folder.

### 5. Report back
Share the design name and confirm it's been placed in the student's folder.

## Naming Convention
Name the presentation: `[Student Name] — [Date]`
Example: `Hsuan — 2026-04-01`

## Output Format
Confirm completion with:
> ✅ **Canva:** Presentation "[Student Name] — [Date]" created and moved to the "[Student Name]" folder.
