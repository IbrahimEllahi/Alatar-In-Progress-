# Alatar (In-Progress)

This is the alpha version of Alatar, a video game about the magical adventures of the world's last wizard! All of the other wizards have vanished from the planet, and Alatar must reclaim his memories in order to figure out what's going on. Slowly roam throughout this universe and unlock gadgets, spells and forgotten memories.



![alatar](https://user-images.githubusercontent.com/85767913/152055363-09cec97e-8a50-4b71-8b4a-70da916bdf90.gif)

<br>

## Version Alpha 1.0

Alatar is currently a visuals-only game. This version allows the player to free-roam throughout the test map, and experiment with particles and game physics.


<br>

## Setup

Use `pip install pygame, pytmx` for the needed packages

<br>

## Implementing the Particle System


The conveniency of this system has allowed me to use it in multiple programs. It does a great job at making the game feel immersive and detailed!

<br>

1. Alatar uses a unique particle system that allows the programmer to easily generate hundreds of particles, with a unique size, color, speed, decay, and flow of direction. This system makes the implemnation of environmental conditions such as rain, snow, meteors, etc, a lot more efficient and accessible.

<br>

2. The Particle Class I've coded is what makes this possible, it takes these ranges of sizes, colors, and speeds, randomizes them and then returns the desired amount of particles objects onto the pygame window. These objects are constantly being updated in each frame, this includes their location, camera angle and size.

<br>

3. To reduce lag these particles have a rate of decay and will slowly disappear over time, this way we can generate new particles and change their x,y values without crashing the program. The `create_particles` function is reponsible for this, when a particle decays or disappears it is called and makes sure to replace the old particle with a newly generated one.

<br>

4. If `runtime = False` these particles will continue to generate on and on for infinity until the level is over, which is exactly what I've done with the test map. Increasing the x,y range of our particles can allow us to see them at different intervals such as every 10-30 seconds. Particles will be randomly generated within these x,y ranges and slowly move onto the main screen. 

<br>

