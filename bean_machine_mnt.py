from typing import Tuple, List
from PIL import Image, ImageDraw
from random import gauss, random

class GaltonBoard:
    DEFAULT_NUM_ROWS: int = 12
    DEFAULT_NUM_BALLS: int = 100_000
    DEFAULT_BOARD_WIDTH: int = 667
    DEFAULT_BOARD_HEIGHT: int = 667
    PEG_RADIUS: int = 4
    BACKGROUND_COLOR: Tuple[int, int, int] = (102, 51, 153)
    LEFT_HALF_COLOR: Tuple[int, int, int] = (122, 122, 244)
    RIGHT_HALF_COLOR: Tuple[int, int, int] = (122, 244, 122)

    def __init__(self, num_rows: int = DEFAULT_NUM_ROWS, num_balls: int = DEFAULT_NUM_BALLS, 
                 board_width: int = DEFAULT_BOARD_WIDTH, board_height: int = DEFAULT_BOARD_HEIGHT) -> None:
        self.num_rows: int = num_rows
        self._num_balls: int = num_balls
        self.board_width: int = board_width
        self.board_height: int = board_height
        self.slot_counts: List[int] = [0] * self.board_width
        self.image: Image.Image = Image.new("RGB", (self.board_width, self.board_height), self.BACKGROUND_COLOR)
        self.draw: ImageDraw.Draw = ImageDraw.Draw(self.image)
        self.elasticity: float = 0.7
        self.peg_offset: float = self.PEG_RADIUS * 0.5
        self.initial_variance: float = 2.0

    @property
    def num_balls(self) -> int:
        return self._num_balls

    @num_balls.setter
    def num_balls(self, num_balls: int) -> None:
        self._num_balls = num_balls

    def simulate(self) -> None:
        """Simulate the dropping of balls through the Galton board."""
        slots = [0] * self.board_width
        progress_step = max(1, self.num_balls // 20)
        
        for i in range(self.num_balls):
            bin_index = self.calculate_bin_index()
            slots[bin_index] += 1
            
            if (i + 1) % progress_step == 0:
                print(f"Simulated: {i + 1}/{self.num_balls} balls.")
        
        self.smooth_slot_counts(slots)

    def smooth_slot_counts(self, slots: List[int]) -> None:
        """Smooth the slot counts using a moving average."""
        window_size = 3
        for i in range(len(self.slot_counts)):
            start = max(0, i - window_size)
            end = min(len(slots), i + window_size + 1)
            self.slot_counts[i] = sum(slots[start:end]) // (end - start)

    def generate_image(self) -> Image.Image:
        """Generate the histogram image."""
        self.draw_histogram()
        return self.image

    def save_image(self, filename: str = 'galton_board.png') -> None:
        """Save the generated histogram image to a file."""
        try:
            self.generate_image().save(filename)
        except Exception as e:
            print(f"Error saving image: {e}")
            raise

    def calculate_bin_index(self) -> int:
        """Calculate the bin index for a single ball drop."""
        position: float = self.board_width / 2 + gauss(0, self.initial_variance)
        momentum: float = 0
        
        for row in range(self.num_rows):
            peg_center = position + (row % 2) * self.peg_offset
            distance_from_center = (position - peg_center) / self.PEG_RADIUS
            
            bounce_probability = 0.5 + (0.1 * distance_from_center)
            bounce_probability = max(0.2, min(0.8, bounce_probability))
            
            direction = 1 if random() < bounce_probability else -1
            bounce_force = (1.0 - abs(distance_from_center)) * self.elasticity
            
            momentum = momentum * 0.8 + direction * bounce_force * self.PEG_RADIUS * 2
            position += momentum
            
            position = max(self.PEG_RADIUS, min(self.board_width - self.PEG_RADIUS, position))

        return int(position)

    def draw_histogram(self) -> None:
        """Draw the histogram on the image."""
        max_frequency: int = max(self.slot_counts)
        bar_width: int = max(1, self.board_width // len(self.slot_counts))

        for bin_index, frequency in enumerate(self.slot_counts):
            self.draw_bar(frequency, bin_index, max_frequency, bar_width)

    def draw_bar(self, frequency: int, bin_index: int, max_frequency: int, bar_width: int) -> None:
        """Draw a single bar on the histogram."""
        bar_height: int = self.calculate_bar_height(frequency, max_frequency)
        x0: int = bin_index * bar_width
        y0: int = self.board_height - bar_height
        x1: int = x0 + bar_width
        y1: int = self.board_height

        color: Tuple[int, int, int] = self.LEFT_HALF_COLOR if x0 < self.board_width // 2 else self.RIGHT_HALF_COLOR
        self.draw.rectangle([x0, y0, x1, y1], fill=color)

    def calculate_bar_height(self, frequency: int, max_frequency: int) -> int:
        """Calculate the height of a bar in the histogram."""
        return 0 if max_frequency == 0 else int(frequency / max_frequency * self.board_height)

def generate_galton_board() -> None:
    """Generate and save a Galton board histogram image."""
    board: GaltonBoard = GaltonBoard(
        board_width=667,
        board_height=667,
        num_rows=12,
        num_balls=100_000
    )
    board.simulate()
    board.save_image()

if __name__ == "__main__":
    generate_galton_board()