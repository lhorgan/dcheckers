# A Lovely Readme for Checkers

To run a graphical :cage match" between two networks, use the following command:

	python graphics.py cage_match 40000 random 2

Specify any network iteration you please (provided it exists), or use random.  In the above command, the network from iteration 40000 will face off against a random agent using depth-2 search.

To play a game against the computer yourself, use:

	python graphics.py game green 40000

The first argument, green, specifies the HUMAN PLAYER.  So, if you run the above command, the computer will play as RED using network 40000.  In human-computer matches, the computer plays with depth-3 search.

To train the network from scratch using the methods outlined in the paper, simply run:

    python train.py

Note that this will progressively overwrite the sample networks provided (in the networks folder), and will generate A LOT of data.  It will also take about a day to run, but it will keep you abreast of its progress.

To run the experiments outlined in the paper, use:

	python trials.py random

to play the networks against a random baseline and

	python trials.py self

to play the networks against themselves.  Both of these commands will take many minutes to run, but they print frequent status updates.

### A Few Practical Notes
Everything here is written from scratch!  For anything NOT involving graphics, it is much faster to use pypy Simply replace each python command with pypy.

	pypy trials.py random

To make this work, you will (of course) need to have pypy installed WITH its special implementation of numpy.  Instructions for installing pypy with numpy are conveniently included on its website (http://pypy.org/download.html).  You do not NEED pypy, it just makes things faster!

Graphics, unfortunately, are not compatible with pypy.  To run graphics, you will need to have the pygame library installed.  To install pygame, just run:

    pip install pygame
