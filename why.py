import tkinter as tk
from enum import Enum
import pynput.keyboard
import pyautogui
import threading
import time
import random

SPEED = 0.9
LEN = 1
DIE = True
FADE = 5

screenWidth, screenHeight = pyautogui.size()
cellSize = screenHeight//10

print(f'Screen width: {screenWidth}, Screen height: {screenHeight}')

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class BodyPart:
    def __init__(self, root, x, y) -> None:
        self.x = x
        self.y = y

        self.root = tk.Toplevel(root)
        self.root.overrideredirect(True)
        self.root.geometry(f'{cellSize}x{cellSize}+{x}+{y}')

        self.bg = 255

        self.root.configure(bg='yellow')

    def age(self):
        if self.bg == 'yellow':
            self.root.configure(bg='#0000FF')
        else:
            self.bg -= FADE
            self.root.configure(bg=f'#0000{hex(self.bg)[2:].upper()}')

    def die(self):
        self.root.destroy()

class Snake:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.overrideredirect(True)

        self.appleX = random.randint(0, screenWidth//cellSize)*cellSize
        self.appleY = random.randint(0, screenHeight//cellSize)*cellSize

        print(f'Apple x: {self.appleX}, Apple y: {self.appleY}')

        self.root.geometry(f'{cellSize}x{cellSize}+{self.appleX}+{self.appleY}')

        self.root.configure(bg='red')

        self.body = []
        self.listener = pynput.keyboard.Listener()

        self.listener.on_press = self.onPress

        self.listener.start()

        self.len = LEN
        self.speed = SPEED

        self.x = cellSize
        self.y = cellSize

        self.lastX = 0
        self.lastY = 0

        self.dir = Direction.RIGHT
        self.lastDir = Direction.RIGHT

        self.live = True

    def onPress(self, key):
        # This is terrible, but i dont care
        try:
            if key.char == "w" and self.lastDir != Direction.DOWN:
                self.dir = Direction.UP

            elif key.char == "s" and self.lastDir != Direction.UP:
                self.dir = Direction.DOWN
            
            elif key.char == "a" and self.lastDir != Direction.RIGHT:
                self.dir = Direction.LEFT
            
            elif key.char == "d" and self.lastDir != Direction.LEFT:
                self.dir = Direction.RIGHT

        except:
            if key == pynput.keyboard.Key.up and self.lastDir != Direction.DOWN:
                self.dir = Direction.UP

            elif key == pynput.keyboard.Key.down and self.lastDir != Direction.UP:
                self.dir = Direction.DOWN

            elif key == pynput.keyboard.Key.left and self.lastDir != Direction.RIGHT:
                self.dir = Direction.LEFT

            elif key == pynput.keyboard.Key.right and self.lastDir != Direction.LEFT:
                self.dir = Direction.RIGHT

            elif key == pynput.keyboard.Key.esc:
                self.live = False
                for part in self.body:
                    part.die()
                self.root.destroy()
                exit(0)
            

    def setRootPos(self):
        while self.live:
            time.sleep(0.01)
            if self.x == self.lastX and self.y == self.lastY:
                continue

            self.lastX = self.x
            self.lastY = self.y

            try:
                self.body[self.len].die()
                self.body.pop()
            except:
                pass
            
            try:
                for i, bodyPart in enumerate(self.body):
                    if i < 500/FADE:
                        bodyPart.age()
            except:
                pass

            self.body.insert(0, BodyPart(self.root, self.x, self.y))


    def move(self):
        while self.live:
            if self.dir == Direction.UP:
                self.y -= cellSize

            elif self.dir == Direction.DOWN:
                self.y += cellSize

            elif self.dir == Direction.LEFT:
                self.x -= cellSize

            elif self.dir == Direction.RIGHT:
                self.x += cellSize

            self.lastDir = self.dir

            if DIE:
                for part in self.body[1:]:
                    if self.x == part.x and self.y == part.y:
                        self.live = False

                        self.root.geometry(f'{100}x{100}+{screenWidth//2-50}+{screenHeight//2-50}')
                        self.root.configure(bg='black')
                        self.root.attributes('-alpha', 0.8)
                        self.root.attributes('-topmost', True)

                        text = tk.Label(self.root, text=f'You died :(\nScore:\n{self.len}', font=('Helvetica', 20), bg='black', fg='white')
                        text.pack()

                        break

            if self.x < 0:
                self.x = round(screenWidth//cellSize)*cellSize

            if self.x > screenWidth:
                self.x = 0
            
            if self.y < 0:
                self.y = round(screenHeight//cellSize-1)*cellSize

            if self.y+cellSize > screenHeight:
                self.y = 0

            time.sleep(1-self.speed)

    def checkApple(self):
        while self.live:
            if self.x == self.appleX and self.y == self.appleY:
                self.len += 1

                while True:
                    self.appleX = random.randint(0, screenWidth//cellSize)*cellSize
                    self.appleY = random.randint(0, screenHeight//cellSize)*cellSize

                    appleInSnake = False
                    for part in self.body:
                        if self.appleX == part.x and self.appleY == part.y:
                            appleInSnake = True
                            break

                    if appleInSnake or self.appleY+cellSize > screenHeight or self.appleX+cellSize > screenWidth:
                        print('Apple in snake or out of bounds')
                        continue

                    break
                
                print(f'Apple x: {self.appleX}, Apple y: {self.appleY}')

                self.root.geometry(f'{cellSize}x{cellSize}+{self.appleX}+{self.appleY}')

            time.sleep(0.01)

    def run(self):
        setPosThread = threading.Thread(target=self.setRootPos)
        setPosThread.start()

        moveThread = threading.Thread(target=self.move)
        moveThread.start()

        appleThread = threading.Thread(target=self.checkApple)
        appleThread.start()

        self.root.mainloop()
            

if __name__ == '__main__':
    snake = Snake()
    snake.run()
