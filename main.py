import typer
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

def main(query: str):
    console = Console()
    console.print(f"[bold blue]🔍 Searching for command to:[/bold blue] {query}...")

    # 1. Ask Copilot (using stderr to catch errors if needed)
    result = subprocess.run(
        ["gh", "copilot", "suggest", "-t", "shell", query],
        capture_output=True,
        text=True
    )

    # 2. Smart Filter: Dig through the "Deprecated" noise
    output_lines = result.stdout.strip().split('\n')
    suggestion = ""

    for line in output_lines:
        clean_line = line.strip()
        # Skip useless lines
        if not clean_line: continue
        if "deprecated" in clean_line.lower(): continue
        if "visit" in clean_line.lower(): continue
        if "https://" in clean_line: continue
        if "no commands" in clean_line.lower(): continue
        
        # The first valid line left is our command
        suggestion = clean_line
        break

    # If we found nothing, check if it failed completely
    if not suggestion:
        console.print("[bold red]❌ Could not find a command.[/bold red]")
        # Print the error so we can see it
        console.print(f"[dim]Debug output: {result.stdout}[/dim]")
        if result.stderr:
            console.print(f"[dim]Error: {result.stderr}[/dim]")
        return

    # 3. Safety Check
    if "rm " in suggestion or "delete" in query.lower():
         console.print("[bold red]⚠️  WARNING: This command deletes files![/bold red]")

    # 4. Show and Ask
    console.print(Panel(f"[bold green]{suggestion}[/bold green]", title="Copilot Suggestion"))
    
    if Confirm.ask("Do you want to run this command?"):
        subprocess.run(suggestion, shell=True)

if __name__ == "__main__":
    typer.run(main)
