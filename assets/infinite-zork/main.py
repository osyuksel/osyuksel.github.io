from pyscript import document
from pyscript.web import page, when

from infinite_zork.engine.game import initialize, game_loop, GameInput
import mistune

markdown = mistune.create_markdown()

state = initialize("content/full_map.json")
loop = game_loop(state)
next(loop)  # Prime the generator

# Get page elements
game_text_div = page["#game-text"][0]
command_input = page["#command-input"][0]
room_title = page["#room-title"][0]
score_display = page["#score-display"][0]
moves_display = page["#moves-display"][0]
inventory_count = page["#inventory-count"][0]
minimap_div = page["#minimap"][0]


def update_ui(minimap_html=""):
    """Update all UI elements with current game state"""
    current_room = state.rooms[state.player.current_room_id]
    room_title.textContent = f"[{current_room.title}]"
    score_display.textContent = f"Score: {state.player.score}"
    moves_display.textContent = (
        f"Moves: {state.player.num_moves}"  # Add moves tracking if needed
    )
    inventory_count.textContent = f"Items: {len(state.player.inventory)}"

    # Update minimap with ASCII art
    if minimap_html:
        minimap_div.innerHTML = minimap_html
        # Optional: tweak styles on the container if needed
        minimap_div.style.margin = "0"
        minimap_div.style.padding = "0"
    else:
        minimap_div.innerHTML = ""


def add_game_text(text, css_class=""):
    """Add text to the game output area"""
    p = document.createElement("p")
    p.innerHTML = markdown(text)
    if css_class:
        p.className = css_class
    game_text_div.appendChild(p)

    # Auto-scroll to bottom
    game_text_div.parentElement.scrollTop = game_text_div.parentElement.scrollHeight


def process_command(command):
    """Process user command and return response"""
    global state, loop
    game_input = GameInput(text=command)
    output, state = loop.send(game_input)
    next(loop)  # Advance to next yield point
    return output


@when("keypress", "#command-input")
def handle_keypress(event):
    """Handle enter key press on command input"""
    if event.key == "Enter":
        command = command_input.value

        if command.strip():
            # Display the command
            add_game_text(f"\\> {command}", "prompt")

            # Process the command
            output = process_command(command)
            add_game_text(output.text, "response")

            # Update UI with minimap
            update_ui(output.minimap)

        # Clear input
        command_input.value = ""


# Initialize the game
def init_game():
    """Initialize the game on page load"""
    # Get initial state with minimap by processing a "look" command
    output = process_command("look")
    add_game_text(output.text, "response")
    update_ui(output.minimap)


# Start the game
init_game()
