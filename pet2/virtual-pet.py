import sys
import os
import glob
import random
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer, QSize, QPoint
from PyQt5.QtGui import QMovie, QPixmap, QTransform

class VirtualPet(QLabel):
    def __init__(self, idle_gifs, walking_gifs, reaction_gifs, frame_size=QSize(200, 200)):
        super().__init__()
        self.idle_gifs = idle_gifs
        self.walking_gifs = walking_gifs
        self.reaction_gifs = reaction_gifs
        self.frame_size = frame_size
        self.facing = 'right' #default direction

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.frame_size)
        # Idle gif start first
        self.movie = QMovie(random.choice(self.idle_gifs))
        self.movie.frameChanged.connect(self.update_frame)
        self.movie.start()

        # timer
        self.change_timer = QTimer(self)
        self.change_timer.timeout.connect(self.change_gif)
        self.change_timer.start(random.randint(5000, 10000))

        # random walk
        self.walk_trigger_timer = QTimer(self)
        self.walk_trigger_timer.timeout.connect(self.maybe_start_walking)
        self.walk_trigger_timer.start(10000)  # Check every 10 seconds.

        # change animations
        self.walk_timer = QTimer(self)
        self.walk_timer.timeout.connect(self.update_walk)
        self.is_walking = False
        self.walk_steps = 0
        self.total_walk_steps = 0
        self.walk_delta = QPoint(0, 0)
        self.target_pos = QPoint(0, 0)

        # drag and click
        self.offset = None
        self.press_pos = None

    def update_frame(self):
        """Called on each frame change. Scales the frame with nearest-neighbor scaling
        to keep pixel art sharp and flips it if needed."""
        pix = self.movie.currentPixmap()
        if pix.isNull():
            return
        scaled = pix.scaled(self.frame_size, Qt.KeepAspectRatio, Qt.FastTransformation)
        if self.facing == 'left':
            transform = QTransform().scale(-1, 1)
            scaled = scaled.transformed(transform)
        self.setPixmap(scaled)

    def change_gif(self):
        """Randomly changes the idle GIF or starts walking with a given probability."""
        if not self.is_walking:
            if self.walking_gifs and random.random() < 0.3:
                self.start_walking()
            else:
                gif_path = random.choice(self.idle_gifs)
                self.movie.stop()
                self.movie = QMovie(gif_path)
                self.movie.frameChanged.connect(self.update_frame)
                self.movie.start()
            self.change_timer.start(random.randint(5000, 10000))

    def maybe_start_walking(self):
        """Randomly trigger walking if not already walking."""
        if not self.is_walking and self.walking_gifs and random.random() < 0.5:
            self.start_walking()

    def start_walking(self):
        """Starts the walking animation and movement sequence.
        Also sets the facing direction based on the target."""
        self.is_walking = True
        if self.walking_gifs:
            gif_path = random.choice(self.walking_gifs)
            self.movie.stop()
            self.movie = QMovie(gif_path)
            self.movie.frameChanged.connect(self.update_frame)
            self.movie.start()

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        current_pos = self.pos()
        target_x = random.randint(screen_geometry.left(), screen_geometry.right() - self.width())
        target_y = random.randint(screen_geometry.top(), screen_geometry.bottom() - self.height())
        self.target_pos = QPoint(target_x, target_y)

        if self.target_pos.x() < current_pos.x():
            self.facing = 'left'
        else:
            self.facing = 'right'

        self.total_walk_steps = 40
        self.walk_steps = 0
        dx = self.target_pos.x() - current_pos.x()
        dy = self.target_pos.y() - current_pos.y()
        self.walk_delta = QPoint(dx // self.total_walk_steps, dy // self.total_walk_steps)
        self.walk_timer.start(50)

    def update_walk(self):
        """Updates the pet's position during walking."""
        if self.walk_steps < self.total_walk_steps:
            self.move(self.pos() + self.walk_delta)
            self.walk_steps += 1
        else:
            self.walk_timer.stop()
            self.is_walking = False
            if self.idle_gifs:
                gif_path = random.choice(self.idle_gifs)
                self.movie.stop()
                self.movie = QMovie(gif_path)
                self.movie.frameChanged.connect(self.update_frame)
                self.movie.start()

    def trigger_reaction(self):
        """Plays a reaction animation when the pet is clicked, then reverts to idle after a fixed duration."""
        if not self.reaction_gifs:
            return
        self.movie.stop()
        gif_path = random.choice(self.reaction_gifs)
        self.movie = QMovie(gif_path)
        self.movie.frameChanged.connect(self.update_frame)
        self.movie.start()
        QTimer.singleShot(2000, self.restore_idle)

    def restore_idle(self):
        """Restores the idle animation after a reaction."""
        if not self.is_walking and self.idle_gifs:
            gif_path = random.choice(self.idle_gifs)
            self.movie.stop()
            self.movie = QMovie(gif_path)
            self.movie.frameChanged.connect(self.update_frame)
            self.movie.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            self.press_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None:
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        if self.offset is not None:
            # Determine if this was a click (minimal movement).
            if (event.pos() - self.press_pos).manhattanLength() < 10:
                self.trigger_reaction()
        self.offset = None
        self.press_pos = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    idle_gifs = glob.glob(os.path.join(script_dir, 'idle_*.gif'))
    walking_gifs = glob.glob(os.path.join(script_dir, 'walk_*.gif'))
    reaction_gifs = glob.glob(os.path.join(script_dir, 'reaction_*.gif'))
    if not walking_gifs:
        walking_gifs = idle_gifs
    if not reaction_gifs:
        reaction_gifs = idle_gifs

    pet = VirtualPet(idle_gifs, walking_gifs, reaction_gifs, frame_size=QSize(200, 200))
    pet.show()
    sys.exit(app.exec_())