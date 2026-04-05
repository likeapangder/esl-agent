"""
Main CLI Interface
A rich-based command-line interface for the ESL Agent.
"""
import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.table import Table

from data_manager import DataManager
from agent_logic import ESLAgent


console = Console()


def display_welcome():
    """Display welcome banner."""
    welcome_text = """
# 🎓 Personalized ESL Agent (Local V2)

Type commands to interact with the agent:
- `/plan [StudentName]` - Generate a lesson plan
- `/chat [StudentName]` - Start a chat session
- `/log [StudentName]` - Log a new lesson summary
- `/finalize` - Save the current lesson plan (inside chat)
- `/list` - List all students
- `/quit` or `/exit` - Exit the program
"""
    console.print(Panel(Markdown(welcome_text), border_style="blue"))


def display_students(data_manager: DataManager):
    """Display list of available students."""
    students = data_manager.list_students()

    if not students:
        console.print("[yellow]No students found in the database.[/yellow]")
        return

    table = Table(title="Available Students", border_style="green")
    table.add_column("Name", style="cyan")

    for student in students:
        table.add_row(student)

    console.print(table)


def handle_chat_command(student_name: str, data_manager: DataManager, agent: ESLAgent):
    """Handle the /chat command."""
    if not student_name:
        console.print("[red]Error: Please provide a student name. Usage: /chat [StudentName][/red]")
        return

    # Check if student exists
    if not data_manager.student_exists(student_name):
        console.print(f"[red]Error: Student '{student_name}' not found in the database.[/red]")
        console.print("[yellow]Available students:[/yellow]")
        display_students(data_manager)
        return

    # Start chat session
    console.print(f"\n[cyan]Starting chat session for {student_name}...[/cyan]\n")
    agent.start_chat(student_name)

    # Initial load of profile
    with console.status("[bold green]Loading student profile..."):
        # We send an initial instruction to the agent to load the profile.
        # This will trigger the tool use.
        response = agent.chat(f"Begin session for {student_name}. Load their profile.", data_manager)
        console.print(Panel(Markdown(response), title="Agent", border_style="green"))

    # Chat loop
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()

            if not user_input:
                continue

            if user_input.lower() in ["/quit", "/exit"]:
                console.print("[yellow]Exiting chat session...[/yellow]")
                break

            if user_input.lower() == "/finalize":
                console.print("\n[cyan]Finalizing and saving lesson plan...[/cyan]")
                with console.status("[bold green]Compiling and saving..."):
                    response = agent.chat(
                        "SYSTEM COMMAND: Compile everything we just discussed into the final 4-part Markdown format, and execute the save_lesson_plan tool.",
                        data_manager
                    )
                console.print(Panel(Markdown(response), title="Agent", border_style="green"))
                continue

            with console.status("[bold green]Agent is thinking..."):
                response = agent.chat(user_input, data_manager)

            console.print(Panel(Markdown(response), title="Agent", border_style="green"))

        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting chat session...[/yellow]")
            break


def handle_plan_command(student_name: str, data_manager: DataManager, agent: ESLAgent):
    """Handle the /plan command."""
    if not student_name:
        console.print("[red]Error: Please provide a student name. Usage: /plan [StudentName][/red]")
        return

    # Check if student exists
    if not data_manager.student_exists(student_name):
        console.print(f"[red]Error: Student '{student_name}' not found in the database.[/red]")
        console.print("[yellow]Available students:[/yellow]")
        display_students(data_manager)
        return

    # Generate lesson plan
    console.print(f"\n[cyan]Generating lesson plan for {student_name}...[/cyan]\n")

    agent.start_chat(student_name)
    with console.status("[bold green]Agent is thinking..."):
        lesson_plan = agent.chat(f"Please create a personalized ESL lesson plan for {student_name}.", data_manager)

    # Display the result
    console.print(Panel(
        Markdown(lesson_plan),
        title=f"Lesson Plan for {student_name}",
        border_style="green"
    ))


def handle_log_command(student_name: str, data_manager: DataManager):
    """Handle the /log command."""
    if not student_name:
        console.print("[red]Error: Please provide a student name. Usage: /log [StudentName][/red]")
        return

    if not data_manager.student_exists(student_name):
        console.print(f"[red]Error: Student '{student_name}' not found.[/red]")
        return

    console.print(f"[cyan]Logging lesson for {student_name}.[/cyan]")
    topic = Prompt.ask("[bold]Topic Taught[/bold]")
    notes = Prompt.ask("[bold]Student Performance Notes[/bold]")

    if data_manager.add_lesson_log(student_name, topic, notes):
        console.print(f"[green]Successfully logged lesson for {student_name}.[/green]")
    else:
        console.print(f"[red]Error: Failed to log lesson for {student_name}.[/red]")



def main():
    """Main CLI loop."""
    # Check for API key
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    google_key = os.environ.get("GOOGLE_API_KEY")

    if not anthropic_key and not google_key:
        console.print("[red]Error: Neither ANTHROPIC_API_KEY nor GOOGLE_API_KEY environment variables are set.[/red]")
        console.print("[yellow]Please set one of your API keys:[/yellow]")
        console.print("[yellow]  export ANTHROPIC_API_KEY='your-key-here'[/yellow]")
        console.print("[yellow]  OR[/yellow]")
        console.print("[yellow]  export GOOGLE_API_KEY='your-key-here'[/yellow]")
        sys.exit(1)

    # Initialize components
    base_dir = Path(__file__).parent
    data_manager = DataManager(students_dir=str(base_dir / "students"))

    # Initialize agent with available key
    if anthropic_key:
        console.print("[green]Using Anthropic Claude API[/green]")
        agent = ESLAgent(api_key=anthropic_key, provider="anthropic")
    else:
        console.print("[green]Using Google Gemini API[/green]")
        agent = ESLAgent(api_key=google_key, provider="google")

    # Display welcome message
    display_welcome()

    # Main loop
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]ESL Agent[/bold blue]").strip()

            if not user_input:
                continue

            # Parse command
            if user_input.startswith("/plan "):
                student_name = user_input[6:].strip()
                handle_plan_command(student_name, data_manager, agent)

            elif user_input.startswith("/chat "):
                student_name = user_input[6:].strip()
                handle_chat_command(student_name, data_manager, agent)

            elif user_input.startswith("/log "):
                student_name = user_input[5:].strip()
                handle_log_command(student_name, data_manager)

            elif user_input == "/finalize":
                # This catches /finalize when typed in the main menu, which is not valid.
                # The user must be in a chat session to finalize.
                console.print("[red]Error: You must be in a chat session to use /finalize. Start a chat first with /chat [StudentName].[/red]")

            elif user_input == "/list":
                display_students(data_manager)

            elif user_input in ["/quit", "/exit"]:
                console.print("[yellow]Goodbye! 👋[/yellow]")
                break

            else:
                console.print(f"[red]Unknown command: {user_input}[/red]")
                console.print("[yellow]Available commands: /plan [StudentName], /chat [StudentName], /list, /quit[/yellow]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye! 👋[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
