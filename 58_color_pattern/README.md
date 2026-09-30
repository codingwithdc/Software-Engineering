# Memory Color Pattern Repair Lab

This project is a pattern recall memory game (Simon-style) using **Pygame**. It introduces students to finite state machines (`WATCH`, `PLAYER_TURN`, `GAME_OVER`), time-based sequence playback, index-matching input validation, and grid-based visual button feedback within an object-oriented codebase.
---

## What's Provided

A working Memory Color Pattern game with:

- A 2x2 grid of four colored buttons (Red, Blue, Green, Yellow) with dim and illuminated lighting states
- Automated timed playback that flashes the sequence step-by-step for the player to watch
- Click detection registering player inputs and checking order against the target sequence
- Score tracking, visual turn indicators, and a Game Over overlay with restart functionality

It has **one deliberate bug** and **three optional features** left as tasks to implement. You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional and more interesting.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**
---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python main.py
```

**Controls:** Left-click colored pads to repeat the sequence. Press R to restart after Game Over.


## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Fix the sequence duplication bug

Each round is supposed to append only one new random color to the existing sequence. In game_engine.start_next_round(), the sequence update line performs self.sequence += self.sequence + [new_color] instead of appending new_color to self.sequence. This causes the pattern length to grow exponentially and duplicates previous entries. Correct the sequence addition logic so only one single color index is added each round.

### Task 2: Implement dynamic playback acceleration

Currently, the sequence flashes at a static 450ms flash duration and 200ms pause duration across all rounds. In game_engine.start_next_round(), adjust self.flash_duration and self.pause_duration to decrease gradually as self.score increases (down to a minimum speed threshold like 180ms flash and 80ms pause), making playback faster and more challenging in later rounds.

### Task 3: Implement sound effects or audio frequencies

The game currently relies entirely on silent visual flashes. Use pygame.mixer or synthesize simple square/sine audio tones mapped to each color ID (e.g., Red: 261Hz, Blue: 329Hz, Green: 392Hz, Yellow: 523Hz). Play the respective tone whenever a button flashes during WATCH mode and when the player clicks it during PLAYER_TURN.

### Task 4: Implement a round countdown timer

During PLAYER_TURN, the player can currently wait indefinitely before making their move. Add a per-round or per-step countdown timer bar displayed in the HUD. If the timer reaches 0 before the player completes the required sequence, transition the game state to GAME_OVER.

---

## Expected Behavior

- At the beginning of each round, the game displays the accumulated sequence step-by-step with illuminated button states.   
- Each round strictly appends one new step rather than duplicating previous patterns.  
- Left-clicking a pad illuminates it briefly and registers the player's guess.
- Entering any incorrect button immediately triggers the Game Over screen.
- Pressing R on the Game Over screen clears the sequence, score, and state back to round 1.
---

## Folder Structure

```
memory_color_pattern/
├── game/
│   ├── color_button.py
│   └── game_engine.py
├── main.py
└── README.md
```

## Submission Checklist

Submission is only the following three things:

- [] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [] The Chat/LLM used page link, with the complete chat history
