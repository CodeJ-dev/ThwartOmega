# ThwartOmega

Set up:

TwarthOmega.py must be in the same folder where all png files realted to TwarthOmega.py are. This can be done by adding TwarthOmega.py into the pictures folder.

User's must also have a discord bot set up and insert the discord bot token into where it says "insert discord bot token". 

User's must also have a discord server with white, black, grey, and gameroom channels set and insert each channel id into where it says "insert (type of channel) id here".

User's must also have a discord server with white, black, and grey roles set and insert each channel id into where it says "insert (type of role) id here".

Rules For Thwart Omega:

Your objective is simple: score more than your opponent, by making many groups of stones of your color. The catch? Your score is the product of your group sizes, which makes it tricky to optimize.

You will play on a 7x7 board. Initially, it begins empty; one of you will play as white and the other as black.

The game is divided into rounds. In each round, each of you must place 1 white stone and 1 black stone on the board, such that they are placed on different empty squares. This is how you build groups of stones.

However, moves are simultaneous, and thus it's possible that you play stones onto the same square. In such case, if a square has two stones of different colors, it's burned and belongs to neither player; otherwise, all the stones remain there, whether it's one or two of a color.

The game ends when there are fewer empty squares than the square of the number of players playing remaining at the end of a round; all remaining empty squares are burned. Then it's time to count up the scores.

A group of stones consists of a maximal contiguous set of squares occupied by the same color of stones. This means, squares that share a side (diagonal touching doesn't count) and both contain the same color belong in the same group; each group is taken to be as large as possible. Your score is simply the product of all group sizes of your color. Group sizes count the number of stones in it; in particular, squares containing two of the same stone count double.

The player with the highest score wins.
