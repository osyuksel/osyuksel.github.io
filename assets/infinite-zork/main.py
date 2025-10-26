from pyscript import document
from pyscript.web import page, when

from infinite_zork.engine.game import initialize, game_loop, GameInput

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
minimap = page["#minimap"][0]


def update_ui():
    """Update all UI elements with current game state"""
    current_room = state.rooms[state.player.current_room_id]
    room_title.textContent = f"[{current_room.title}]"
    score_display.textContent = f"Score: {state.player.score}"
    moves_display.textContent = "Moves: 0"  # Add moves tracking if needed
    inventory_count.textContent = f"Items: {len(state.player.inventory)}"

    # Update minimap with visited rooms (if you want to track visited rooms, add that to GameState)
    minimap.innerHTML = ""
    # For now, just show current room
    room_element = document.createElement("div")
    room_element.textContent = f"• {current_room.title}"
    room_element.style.color = "#ffff00"
    room_element.style.fontWeight = "bold"
    minimap.appendChild(room_element)


def add_game_text(text, css_class=""):
    """Add text to the game output area"""
    p = document.createElement("p")
    p.textContent = text
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
    return output.text


@when("keypress", "#command-input")
def handle_keypress(event):
    """Handle enter key press on command input"""
    if event.key == "Enter":
        command = command_input.value

        if command.strip():
            # Display the command
            add_game_text(f"> {command}", "prompt")

            # Process the command
            response = process_command(command)
            add_game_text(response, "response")

            # Update UI
            update_ui()

        # Clear input
        command_input.value = ""


# Initialize the game
def init_game():
    """Initialize the game on page load"""
    update_ui()
    add_game_text(
        "You awaken in a dark room. Type 'look' to examine your surroundings, or 'help' for commands.",
        "response",
    )


# Start the game
init_game()
