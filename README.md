# Personalized ESL Agent

A local CLI-based agent for generating personalized ESL lesson plans with diagnostic reasoning.

## Setup

1. Install dependencies:
```bash
pip install anthropic rich
```

2. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

3. Run the agent:
```bash
python main.py
```

## Usage

### Python CLI
- `/plan [StudentName]` - Generate a personalized lesson plan
- `/list` - List all available students
- `/quit` or `/exit` - Exit the program

### Claude Code Skills

- **Full flow:** `/esl-prep Hsuan '/path/to/elli.pdf'`
  Reads the student profile, generates a QA-checked lesson plan, and creates a Canva presentation filed in the student's folder.

- **Plan only:** `/esl-plan Hsuan "smartwatches"`
  Generates the lesson plan with exact Canva slide content — no Canva design created.

- **Canva only:** `/esl-canva Hsuan` (after a plan is already in the conversation)
  Creates a Canva presentation from the slide content and files it in the student's folder.

## Project Structure

```
esl-agent/
├── architecture.md               # Project specification
├── README.md                     # This file
├── main.py                       # CLI interface
├── agent_logic.py                # LLM interaction logic
├── data_manager.py               # File I/O handling
├── students/                     # Student profile storage (Markdown)
├── prompts/
│   ├── esl-prep.md               # Orchestrator prompt
│   ├── esl-plan.md               # Lesson plan generation + QA prompt
│   └── esl-canva.md              # Canva presentation creation prompt
└── .claude/skills/
    ├── esl-prep/SKILL.md         # Orchestrator skill
    ├── esl-plan/SKILL.md         # Plan generation skill
    └── esl-canva/SKILL.md        # Canva creation skill
```

## Student Profile Schema

Each student profile (`students/{name}.json`) contains:
- `name`: Student's name
- `cefr_level`: CEFR proficiency level (A1, A2, B1, B2, C1, C2)
- `interests`: List of topics the student is interested in
- `weaknesses`: List of specific grammar/pronunciation challenges
- `last_lesson`: Summary of the most recent lesson
- `goals`: Student's learning objectives
