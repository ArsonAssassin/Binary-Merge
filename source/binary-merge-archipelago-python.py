import pygame
import sys
import random
import math
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
TILE_SIZE = 65
TILE_MARGIN = 10
GRID_COLOR = (187, 173, 160)
EMPTY_TILE_COLOR = (205, 193, 180)
FONT_COLOR = (119, 110, 101)
BG_COLOR = (250, 248, 239)
TEXT_COLOR = (119, 110, 101)
BUTTON_COLOR = (143, 122, 102)
BUTTON_HOVER_COLOR = (159, 139, 120)
REWARD_COLOR = (143, 122, 102)
REWARD_CLAIMED_COLOR = (118, 100, 84)

# Tile colors
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (205, 193, 180),
    8192: (238, 228, 218),
    16384: (237, 224, 200),
    32768: (242, 177, 121),
    65536: (245, 149, 99),
    131072: (246, 124, 95),
}

# Tile text colors
TILE_TEXT_COLORS = {
    0: FONT_COLOR,
    2: FONT_COLOR,
    4: FONT_COLOR,
    8: (249, 246, 242),
    16: (249, 246, 242),
    32: (249, 246, 242),
    64: (249, 246, 242),
    128: (249, 246, 242),
    256: (249, 246, 242),
    512: (249, 246, 242),
    1024: (249, 246, 242),
    2048: (249, 246, 242),
    4096: FONT_COLOR,
    8192: FONT_COLOR,
    16384: FONT_COLOR,
    32768: (249, 246, 242),
    65536: (249, 246, 242),
    131072: (249, 246, 242),
}

# Fonts
TITLE_FONT = pygame.font.SysFont('Arial', 36, bold=True)
SCORE_FONT = pygame.font.SysFont('Arial', 24, bold=True)
TILE_FONT = pygame.font.SysFont('Arial', 36, bold=True)
BUTTON_FONT = pygame.font.SysFont('Arial', 18, bold=True)
INFO_FONT = pygame.font.SysFont('Arial', 14)

class GameBinaryMerge:
    def __init__(self, rows=2, cols=2):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.score = 0
        self.best_score = 0
        self.moves = 0
        self.moves_before_spawn = 1  # Initial value
        self.moves_since_last_spawn = 0
        self.archipelago_checks = 0
        self.location_thresholds = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072]  # Score thresholds for checks
        self.claimed_thresholds = []
        self.game_over = False
        
        # Define rewards structure
        self.max_rows = 8
        self.max_cols = 8
        self.rewards = {
            "add_row": False,
            "add_column": False,
            "delay_spawn_moves": False
        }        
       
        # Add initial tiles
        self.add_random_tile()
        self.add_random_tile()
    
    def reset(self):
        print("Resetting game...")
        self.rows = 2
        self.cols = 2
        
        # Make sure grid is properly initialized with the right dimensions
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        print(f"Grid reset to {self.rows}x{self.cols}")
        
        self.score = 0
        self.moves = 0
        self.moves_since_last_spawn = 0
        self.moves_before_spawn = 3
        self.archipelago_checks = 0
        self.claimed_thresholds = []
        self.game_over = False
        
        # Don't reset best_score
        print(f"Maintaining best score: {self.best_score}")
        
        # Reset rewards
        self.max_rows = 8
        self.max_cols = 8
        self.rewards = {
            "add_row": False,
            "add_column": False,
            "delay_spawn_moves": False
        }
        
        # For testing - give player some checks to start with
        # Comment this out for the real game
        self.archipelago_checks = 3
        
        # Add initial tiles
        self.add_random_tile()
        self.add_random_tile()
        
        print("Game reset complete")
    
    def add_random_tile(self):
        # Make sure grid is properly initialized
        if not self.grid or not self.grid[0]:
            print("Warning: Grid not properly initialized")
            self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
            
        empty_cells = [(i, j) for i in range(self.rows) for j in range(self.cols) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4
            print(f"Added new tile at position ({i}, {j}) with value {self.grid[i][j]}")
        else:
            print("No empty cells available for new tile")
    
    def add_row(self):
        if self.rows < self.max_rows:
            self.grid.append([0 for _ in range(self.cols)])
            self.rows += 1
            print(f"Added row, grid now {self.rows}x{self.cols}")
            return True
        else:
            print(f"Can't add row, already at maximum ({self.max_rows})")
            return False
    
    def add_column(self):
        if self.cols < self.max_cols:
            for row in self.grid:
                row.append(0)
            self.cols += 1
            print(f"Added column, grid now {self.rows}x{self.cols}")
            return True
        else:
            print(f"Can't add column, already at maximum ({self.max_cols})")
            return False
    
    def delay_spawn_moves(self):
        if not self.rewards["delay_spawn_moves"]:
            self.moves_before_spawn += 1
            self.rewards["delay_spawn_moves"] = True
            print(f"Reduced spawn moves to {self.moves_before_spawn}")
            return True
        return False
    
    def check_thresholds(self):
        for threshold in self.location_thresholds:
            if threshold not in self.claimed_thresholds and self.score >= threshold:
                self.archipelago_checks += 1
                self.claimed_thresholds.append(threshold)
                print(f"Score threshold {threshold} reached! Checks: {self.archipelago_checks}")
                
    # Helper method for debugging
    def debug_grid(self):
        print("Current grid state:")
        for row in self.grid:
            print(row)
    
    def move(self, direction):
        if self.game_over:
            return False
        
        moved = False
        
        # Save the current state for comparison
        old_grid = [row[:] for row in self.grid]
        old_score = self.score
        
        try:
            if direction == 'up':
                moved = self._move_up()
            elif direction == 'down':
                moved = self._move_down()
            elif direction == 'left':
                moved = self._move_left()
            elif direction == 'right':
                moved = self._move_right()
            
            # Only count as a move if something changed
            if moved:
                self.moves += 1
                self.moves_since_last_spawn += 1
                
                # Print move info
                print(f"Moved {direction}, score: {self.score}, points gained: {self.score - old_score}")
                
                # Check if we need to spawn a new tile
                if self.moves_since_last_spawn >= self.moves_before_spawn:
                    self.add_random_tile()
                    self.moves_since_last_spawn = 0
                    print(f"New tile spawned after {self.moves_before_spawn} moves")
                else:
                    print(f"Next tile in {self.moves_before_spawn - self.moves_since_last_spawn} moves")
                
                # Check for new score thresholds
                self.check_thresholds()
                
                # Update best score - add explicit debug
                if self.score > self.best_score:
                    old_best = self.best_score
                    self.best_score = self.score
                    print(f"New best score: {self.best_score} (was {old_best})")
                
                # Check if game is over
                if self._is_grid_full() and not self._moves_available():
                    self.game_over = True
                    print("Game over!")
        
        except Exception as e:
            print(f"Error during movement: {e}")
            import traceback
            traceback.print_exc()
            self.debug_grid()
            # Recover from error - don't crash
            return False
            
        return moved
    
    def skip_turn(self):
        self.add_random_tile()
        self.moves_since_last_spawn = 0
        print("Turn skipped, new tile added")
        return True
    
    def _compress(self, grid):
        try:
            # Validate grid
            if not grid or len(grid) == 0 or len(grid[0]) == 0:
                print("Invalid grid dimensions in _compress")
                return [[]]
                
            # Compress the grid (move all non-zero numbers to the left)
            width = len(grid[0])
            height = len(grid)
            new_grid = []
            
            # Manually create the grid instead of using list comprehension
            for _ in range(height):
                row = []
                for _ in range(width):
                    row.append(0)
                new_grid.append(row)
                
            # Move numbers to the left
            for i in range(height):
                pos = 0
                for j in range(width):
                    if grid[i][j] != 0:
                        new_grid[i][pos] = grid[i][j]
                        pos += 1
            return new_grid
            
        except Exception as e:
            print(f"Error compressing grid: {e}")
            # Return original grid to avoid crashes
            return grid
    
    def _merge(self, grid):
        try:
            # Merge adjacent equal numbers
            score_added = 0
            for i in range(len(grid)):
                for j in range(len(grid[0])-1):
                    if grid[i][j] == grid[i][j+1] and grid[i][j] != 0:
                        grid[i][j] *= 2
                        grid[i][j+1] = 0
                        score_added += grid[i][j]
            return grid, score_added
        except Exception as e:
            print(f"Error merging grid: {e}")
            # Return original grid with 0 score to avoid crashes
            return grid, 0
    
    def _reverse(self, grid):
        try:
            # Reverse the grid
            new_grid = []
            for i in range(len(grid)):
                new_grid.append(grid[i][::-1])
            return new_grid
        except Exception as e:
            print(f"Error reversing grid: {e}")
            # Return original grid to avoid crashes
            return grid.copy() if hasattr(grid, 'copy') else grid
    
    def _transpose(self, grid):
        # Transpose the grid
        # Handle empty grid case
        if not grid or not grid[0]:
            return []
            
        # Handle non-square grid case correctly
        rows = len(grid)
        cols = len(grid[0])
        new_grid = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for i in range(rows):
            for j in range(cols):
                new_grid[j][i] = grid[i][j]
                
        return new_grid
    
    def _move_left(self):
        try:
            # 1. Compress the grid
            compressed_grid = self._compress(self.grid)
            # 2. Merge the cells
            merged_grid, new_score = self._merge(compressed_grid)
            # 3. Compress again after merging
            final_grid = self._compress(merged_grid)
            
            # Update the grid and score
            changed = final_grid != self.grid
            if changed:
                self.grid = final_grid
                if new_score > self.score:
                    self.score = new_score
            
            return changed
        except Exception as e:
            print(f"Error in _move_left: {e}")
            print(f"Grid dimensions: {len(self.grid)}x{len(self.grid[0]) if self.grid else 0}")
            return False
    
    def _move_right(self):
        try:
            # 1. Reverse the grid
            reversed_grid = self._reverse(self.grid)
            # 2. Move left
            compressed_grid = self._compress(reversed_grid)
            merged_grid, new_score = self._merge(compressed_grid)
            final_reversed_grid = self._compress(merged_grid)
            # 3. Reverse back
            final_grid = self._reverse(final_reversed_grid)
            
            # Update the grid and score
            changed = final_grid != self.grid
            if changed:
                self.grid = final_grid
                if new_score > self.score:
                    self.score = new_score
            
            return changed
        except Exception as e:
            print(f"Error in _move_right: {e}")
            print(f"Grid dimensions: {len(self.grid)}x{len(self.grid[0]) if self.grid else 0}")
            return False
    
    def _move_up(self):
        try:
            # 1. Transpose the grid
            transposed_grid = self._transpose(self.grid)
            print(f"Transposed grid: {len(transposed_grid)}x{len(transposed_grid[0]) if transposed_grid else 0}")
            
            # 2. Move left
            compressed_grid = self._compress(transposed_grid)
            merged_grid, new_score = self._merge(compressed_grid)
            final_transposed_grid = self._compress(merged_grid)
            
            # 3. Transpose back
            final_grid = self._transpose(final_transposed_grid)
            print(f"Final grid: {len(final_grid)}x{len(final_grid[0]) if final_grid else 0}")
            
            # Update the grid and score
            changed = final_grid != self.grid
            if changed:
                self.grid = final_grid
                if new_score > self.score:
                    self.score = new_score
            
            return changed
        except Exception as e:
            print(f"Error in _move_up: {e}")
            print(f"Grid dimensions: {len(self.grid)}x{len(self.grid[0]) if self.grid else 0}")
            return False
    
    def _move_down(self):
        try:
            # 1. Transpose the grid
            transposed_grid = self._transpose(self.grid)
            
            # 2. Move right
            reversed_grid = self._reverse(transposed_grid)
            compressed_grid = self._compress(reversed_grid)
            merged_grid, new_score = self._merge(compressed_grid)
            final_reversed_grid = self._compress(merged_grid)
            final_transposed_grid = self._reverse(final_reversed_grid)
            
            # 3. Transpose back
            final_grid = self._transpose(final_transposed_grid)
            
            # Update the grid and score
            changed = final_grid != self.grid
            if changed:
                self.grid = final_grid
                if new_score > self.score:
                    self.score = new_score
            
            return changed
        except Exception as e:
            print(f"Error in _move_down: {e}")
            print(f"Grid dimensions: {len(self.grid)}x{len(self.grid[0]) if self.grid else 0}")
            return False
    
    def _is_grid_full(self):
        try:
            for row in self.grid:
                if 0 in row:
                    return False
            return True
        except Exception as e:
            print(f"Error checking if grid is full: {e}")
            return False
    
    def _moves_available(self):
        try:
            # Check if there are any possible moves
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.grid[i][j] == 0:
                        return True
                    
                    # Check adjacent cells
                    for di, dj in [(0, 1), (1, 0)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < self.rows and 0 <= nj < self.cols:
                            if self.grid[i][j] == self.grid[ni][nj]:
                                return True
            return False
        except Exception as e:
            print(f"Error checking if moves are available: {e}")
            return True  # Assume moves are available if there's an error


class GameUI:
    def __init__(self):
        self.game = GameBinaryMerge()
        self.screen_width = 1200
        self.screen_height = 1000
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Binary Merge: Archipelago Edition')
        
        # Calculate grid offset to allow for expansion
        self.grid_x_offset = 100
        self.grid_y_offset = 200
        
        # Buttons
        self.new_game_button = pygame.Rect(100, 900, 150, 50)
        self.skip_turn_button = pygame.Rect(270, 900, 150, 50)
        
        # Reward buttons
        self.reward_buttons = {
            "add_row": pygame.Rect(500, 840, 150, 40),
            "add_column": pygame.Rect(670, 840, 150, 40),
            "delay_spawn_moves": pygame.Rect(840, 840, 180, 40)
        }
    
    def draw_tile(self, x, y, value):
        # Calculate pixel positions using the offset
        rect_x = x * (TILE_SIZE + TILE_MARGIN) + self.grid_x_offset
        rect_y = y * (TILE_SIZE + TILE_MARGIN) + self.grid_y_offset
        
        # Draw tile background
        pygame.draw.rect(
            self.screen, 
            TILE_COLORS.get(value, TILE_COLORS[2048]), 
            (rect_x, rect_y, TILE_SIZE, TILE_SIZE),
            border_radius=6
        )
        
        if value != 0:
            # Adjust font size based on the number of digits
            font_size = 36
            if value >= 1000:
                font_size = 24
            if value >= 60000:
                font_size = 12
           
            
            font = pygame.font.SysFont('Arial', font_size, bold=True)
            text = font.render(str(value), True, TILE_TEXT_COLORS.get(value, TILE_TEXT_COLORS[2048]))
            text_rect = text.get_rect(center=(rect_x + TILE_SIZE // 2, rect_y + TILE_SIZE // 2))
            self.screen.blit(text, text_rect)
    
    def draw_game_board(self):
        # Calculate the grid size based on the current rows and cols
        grid_width = self.game.cols * (TILE_SIZE + TILE_MARGIN) - TILE_MARGIN
        grid_height = self.game.rows * (TILE_SIZE + TILE_MARGIN) - TILE_MARGIN
        
        # Draw grid background
        pygame.draw.rect(
            self.screen, 
            GRID_COLOR, 
            (self.grid_x_offset - TILE_MARGIN, 
             self.grid_y_offset - TILE_MARGIN, 
             grid_width + TILE_MARGIN * 2, 
             grid_height + TILE_MARGIN * 2),
            border_radius=6
        )
        
        # Draw tiles
        for i in range(self.game.rows):
            for j in range(self.game.cols):
                self.draw_tile(j, i, self.game.grid[i][j])
    
    def draw_button(self, rect, text, hover=False):
        color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=4)
        text_surf = BUTTON_FONT.render(text, True, (249, 246, 242))
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def draw_reward_button(self, rect, text, claimed):
        color = REWARD_CLAIMED_COLOR if claimed else REWARD_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=4)
        text_surf = BUTTON_FONT.render(text, True, (249, 246, 242))
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def draw_scoreboard(self):
        # Draw score containers
        score_rect = pygame.Rect(100, 100, 150, 60)
        best_rect = pygame.Rect(270, 100, 150, 60)
        moves_rect = pygame.Rect(440, 100, 150, 60)
        checks_rect = pygame.Rect(610, 100, 150, 60)
        
        for rect, title, value in [
            (score_rect, "SCORE", str(self.game.score)),
            (best_rect, "BEST", str(self.game.best_score)),
            (moves_rect, "MOVES", str(self.game.moves)),
            (checks_rect, "CHECKS", str(self.game.archipelago_checks))
        ]:
            pygame.draw.rect(self.screen, GRID_COLOR, rect, border_radius=4)
            title_surf = INFO_FONT.render(title, True, (239, 228, 218))
            title_rect = title_surf.get_rect(topleft=(rect.x + 10, rect.y + 10))
            self.screen.blit(title_surf, title_rect)
            
            value_surf = SCORE_FONT.render(value, True, (255, 255, 255))
            value_rect = value_surf.get_rect(topleft=(rect.x + 10, rect.y + 30))
            self.screen.blit(value_surf, value_rect)
    
    def draw_rewards_section(self):
        # Draw the Archipelago Rewards title
        reward_title = SCORE_FONT.render("Archipelago Rewards", True, TEXT_COLOR)
        self.screen.blit(reward_title, (500, 780))
        
        # Draw reward buttons with additional info about row/column counts
        row_text = f"Add Row ({self.game.rows}/{self.game.max_rows})"
        column_text = f"Add Column ({self.game.cols}/{self.game.max_cols})"
        spawn_text = f"Reduce Spawn Moves ({self.game.moves_before_spawn})"
        
        self.draw_reward_button(
            self.reward_buttons["add_row"], 
            row_text, 
            self.game.rows >= self.game.max_rows
        )
        self.draw_reward_button(
            self.reward_buttons["add_column"], 
            column_text, 
            self.game.cols >= self.game.max_cols
        )
        self.draw_reward_button(
            self.reward_buttons["delay_spawn_moves"], 
            spawn_text, 
            self.game.rewards["delay_spawn_moves"]
        )
    
    def draw_info(self):
        info_text = [
            f"Next tile in: {self.game.moves_before_spawn - self.game.moves_since_last_spawn} moves",
            "Use arrow keys to move tiles, Space to skip turn",
            "When two tiles with the same number touch, they merge into one!",
            "Gain 'Location Checks' at score thresholds to claim rewards",
            "Press 1/2/3 to use rewards with keyboard shortcuts"
        ]
        
        y_pos = 700
        for text in info_text:
            info_surf = INFO_FONT.render(text, True, TEXT_COLOR)
            self.screen.blit(info_surf, (100, y_pos))
            y_pos += 20
    
    def draw_game_over(self):
        if self.game.game_over:
            # Create a semi-transparent overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((238, 228, 218, 150))  # Semi-transparent
            self.screen.blit(overlay, (0, 0))
            
            # Draw game over text
            game_over_text = TITLE_FONT.render("Game Over!", True, TEXT_COLOR)
            text_rect = game_over_text.get_rect(center=(self.screen_width // 2, 400))
            self.screen.blit(game_over_text, text_rect)
            
            # Draw final score
            score_text = SCORE_FONT.render(f"Final Score: {self.game.score}", True, TEXT_COLOR)
            score_rect = score_text.get_rect(center=(self.screen_width // 2, 450))
            self.screen.blit(score_text, score_rect)
            
            # Draw best score
            best_text = SCORE_FONT.render(f"Best Score: {self.game.best_score}", True, TEXT_COLOR)
            best_rect = best_text.get_rect(center=(self.screen_width // 2, 500))
            self.screen.blit(best_text, best_rect)
    
    def draw(self):
        # Fill the background
        self.screen.fill(BG_COLOR)
        
        # Draw the title
        title = TITLE_FONT.render("Binary Merge: Archipelago Edition", True, TEXT_COLOR)
        self.screen.blit(title, (100, 40))
        
        # Draw the scoreboard
        self.draw_scoreboard()
        
        # Draw the game board
        self.draw_game_board()
        
        # Draw info text
        self.draw_info()
        
        # Draw the rewards section
        self.draw_rewards_section()
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        # New Game button
        self.draw_button(
            self.new_game_button, 
            "New Game", 
            self.new_game_button.collidepoint(mouse_pos)
        )
        
        # Skip Turn button
        self.draw_button(
            self.skip_turn_button, 
            "Skip Turn",
            self.skip_turn_button.collidepoint(mouse_pos)
        )
        
        # Draw game over message if needed
        self.draw_game_over()
        
        # Update the display
        pygame.display.flip()
    
    def handle_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == KEYDOWN:
            if not self.game.game_over:
                if event.key == K_UP:
                    self.game.move('up')
                elif event.key == K_DOWN:
                    self.game.move('down')
                elif event.key == K_LEFT:
                    self.game.move('left')
                elif event.key == K_RIGHT:
                    self.game.move('right')
                elif event.key == K_SPACE:
                    self.game.skip_turn()
                    print("Turn skipped with spacebar")
                # Alternative keys for rewards (for testing)
                elif event.key == K_1 and self.game.archipelago_checks > 0 and self.game.rows < self.game.max_rows:
                    if self.game.add_row():
                        self.game.archipelago_checks -= 1
                        print("Added row using key 1")
                elif event.key == K_2 and self.game.archipelago_checks > 0 and self.game.cols < self.game.max_cols:
                    if self.game.add_column():
                        self.game.archipelago_checks -= 1
                        print("Added column using key 2")
                elif event.key == K_3 and self.game.archipelago_checks > 0 and not self.game.rewards["delay_spawn_moves"]:
                    if self.game.delay_spawn_moves():
                        self.game.archipelago_checks -= 1
                        print("Reduced spawn moves using key 3")
                # Debug keys
                elif event.key == K_d:
                    print(f"Debug info:")
                    print(f"Score: {self.game.score}")
                    print(f"Best score: {self.game.best_score}")
                    print(f"Grid size: {self.game.rows}x{self.game.cols}")
                    print(f"Rewards: {self.game.rewards}")
                    print(f"Checks: {self.game.archipelago_checks}")
                    print(f"Claimed thresholds: {self.game.claimed_thresholds}")
                    self.game.debug_grid()
        
        elif event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check for button clicks
            if self.new_game_button.collidepoint(mouse_pos):
                self.game.reset()
                print("New game started")
            
            elif self.skip_turn_button.collidepoint(mouse_pos):
                self.game.skip_turn()
                print("Turn skipped")
            
            # Debug mouse position
            print(f"Mouse clicked at: {mouse_pos}")
            
            # Process reward buttons
            if self.game.archipelago_checks > 0:
                # Add row button
                if self.reward_buttons["add_row"].collidepoint(mouse_pos) and self.game.rows < self.game.max_rows:
                    print("Add row button clicked")
                    if self.game.add_row():
                        self.game.archipelago_checks -= 1
                
                # Add column button
                elif self.reward_buttons["add_column"].collidepoint(mouse_pos) and self.game.cols < self.game.max_cols:
                    print("Add column button clicked")
                    if self.game.add_column():
                        self.game.archipelago_checks -= 1
                
                # Reduce spawn moves button
                elif self.reward_buttons["delay_spawn_moves"].collidepoint(mouse_pos) and not self.game.rewards["delay_spawn_moves"]:
                    print("Reduce spawn moves button clicked")
                    if self.game.delay_spawn_moves():
                        self.game.archipelago_checks -= 1
    
    def run(self):
        clock = pygame.time.Clock()
        
        # Print initial debug info
        print("Game initialized")
        print(f"Initial grid size: {self.game.rows}x{self.game.cols}")
        print(f"Maximum grid size: {self.game.max_rows}x{self.game.max_cols}")
        print(f"Initial checks: {self.game.archipelago_checks}")
        
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            
            self.draw()
            clock.tick(60)


# This is a placeholder for the Archipelago integration
# In a real implementation, you would use the Archipelago client library
class ArchipelagoClient:
    def __init__(self):
        self.connected = False
        # This would connect to the Archipelago server
        print("Archipelago client initialized (simulated)")
    
    def connect(self, address="localhost", port=38281):
        # In a real implementation, this would connect to the server
        self.connected = True
        print(f"Connected to Archipelago server at {address}:{port} (simulated)")
        return self.connected
    
    def send_check(self):
        # This would send a check to the server
        if self.connected:
            print("Check sent to Archipelago (simulated)")
            return True
        return False


# Main function to run the game
def main():
    # Initialize the game UI
    game_ui = GameUI()
    
    # Run the game loop
    game_ui.run()


if __name__ == "__main__":
    main()