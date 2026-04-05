---
name: esl-canva
description: Creates a Canva presentation from lesson plan slide content and files it in the student's folder
context: fork
agent: general-purpose
---
You create Canva presentations from finalized ESL lesson plans using Canva MCP tools.

You should strictly follow the instructions in the file `prompts/esl-canva.md` to execute this task.

Arguments:
$1: The student's name

Use the slide content from the current conversation (output of /esl-plan) to generate the Canva presentation.
Please execute the workflow defined in `prompts/esl-canva.md` using the provided arguments.
