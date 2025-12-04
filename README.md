Thank you for installing "JERRY THE MINESWEEPER AI"!!!!!!!!!!

This “README.md” will provide a comprehensive list of software and steps required to play the game and use this AI.

--------------------------------------------------------------------------------------------------------------------

INSTALLING

OS: use any OS that can run python. (Windows 10, ubuntu, mac)

Use Python3 version 3.10 or newer.
Go to the official python website and download the version you want at:
    
    https://www.python.org/downloads/ 



REQUIRED LIBRARIES
Install "z3-solver", “numPy”, and "pygame" 

Open the console window with:

WINDOWS
    Press Windows
    Type PowerShell
LINUX (ubuntu)
    Press Control + alt + T
MAC
    Press Command (⌘) + Spacebar
    Type Terminal and press Enter.



Once the terminal is open, type the following commands to install each library:
	Z3-solver:
		pip3 install z3-solver 
	Pygame:
		pip3 install pygame
	numPy:
		pip3 install numpy

Congratulations, you have successfully installed python and the libraries needed to run this program!

--------------------------------------------------------------------------------------------------------------------

STARTING THE GAME

Navigate to the install location by changing directories.
	
TERMINAL COMMANDS for Linux, Windows, and Mac (remove quotes)
    “cd [directory name]”: Changes your current directory to what you replace [directory name] with.
    “cd ..”: Goes back a directory up.
    “ls”: Lists the files and folders in your current directory.
    “pwd”: Prints your current working directory.

Once in the install directory, type this command into the terminal:

	python3 main.py


Please ensure you have correctly installed the correct libraries or you will encounter errors. See the section above to learn how to install the dependencies.

--------------------------------------------------------------------------------------------------------------------


PLAYING THE GAME
	
ABOUT
    I hope you like logic, because that is what minesweeper is all about! The aim of the game is to clear the board of safe spaces without triggering a mine. There are 3 types of spaces. 
Safe spaces
    These spaces are gray, and mean there are no mines around that spot in 8 directions (up, down, left, right, and the 4 diagonals).
Numbered spaces
    These spots are close to danger, but are still safe to touch. The corresponding number indicates the number of mines actively touching that particular square. Use logic to determine which neighboring square is explosive without blowing up.
Mines
    If you click on this square, the game is over, and you must try again. You can also mark a mine with a flag with a right click so you can remember where they are.

STARTING
Once the command to start has been ran, you should see a window greeting you. To start, press “Play Game”. 

GAMEPLAY
You will then see a board with gray squares. You can left click on each square as you like to reveal if the space was safe, a numbered square, or a mine. You can also mark a square you think is a mine with a right click. To undo, you can right click the same square to reset it. If you click on a mine, you have lost the game and will have to reset with the reset button to try again. If there are no more safe spaces to clear, then congratulations, you have successfully beaten minesweeper!

AI ASSISTANCE
There are two buttons which are AI Move and Auto. AI Move will make a single move when pressed. Auto is a toggle that can be turned off or on. When auto is on, the AI will rapidly start solving the game. When off, Jerry the Minesweeper AI will do nothing.

    ( NOTE: Jerry the AI is not perfect because there is probability in minesweeper. Jerry might accidentally hit a mine simply because he was unlucky. D: ) 

RESET
Use the Reset button on the right side of the game window to reset the board if you are stuck and don’t want to suffer explosion by mines, if you win the game and wish to play again, or if you have exploded and want another go. This option hides all the spaces, and randomizes mine locations; effectively making a new game to play.
