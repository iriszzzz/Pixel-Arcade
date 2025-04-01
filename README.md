# Pixel-Arcade
The goal of this project is to create a simple interactive gaming platform built with Python. The platform allows players to register and log in with a secure account system, view personal player information, and play three built-in mini-games. The project focuses on applying Python libraries and concepts to build a functioning application with a strong emphasis on game design and user interactivity.
> The repository records the final project in [Python Data Science](https://timetable.nycu.edu.tw/?r=main/crsoutline&Acy=113&Sem=1&CrsNo=537402&lang=zh-tw) course at NYCU.

## Overview

This project implements a game platform in Python using the Pygame library. The platform allows users to register, log in, and play multiple games. These games include:

- **Snake Game** (Gourmet Train)
- **Bridge Game**
- **Dots and Boxes**
- **Dark Chess**

The platform includes features for user registration, login, password management, and a leveling system based on experience points earned in the games. Users can track their high scores and level up as they accumulate experience points.

## Features

- **User Authentication:**
  - Users can register and log in to the platform.
  - Passwords are hashed for security.
  - Users can change their password.

- **Main Menu:**
  - Once logged in, users are greeted with a main menu offering options to play various games.
  - The main menu also provides options to log out and change the password.

- **Game Integration:**
  - Users can play the following games:
    - **Gourmet Train (Snake Game):** A classic Snake game where users can accumulate points and track their highest score.
    - **Bridge Game:** A card game allowing users to play and earn experience.
    - **Dots and Boxes:** A puzzle game where users can compete for points.
    - **Dark Chess:** A variation of chess where the pieces are hidden until they are revealed.

- **Experience and Leveling System:**
  - As users play games, they accumulate experience points.
  - Once they reach a certain experience threshold, they level up, unlocking new challenges and rewards.
  - The experience and level are displayed in the main menu.

- **Persistent Data:**
  - User data, including passwords, scores, and experience, are saved to a JSON file to persist across sessions.

## Requirements

- Python 3.x
- Pygame library

You can install Pygame via pip:

```bash
pip install pygame
```

## Running the Platform

To start the platform, navigate to the directory containing the project files and run:

```bash
python game_platform.py
```

This will launch the game platform in a Pygame window.

## Game Description

### Snake Game (Gourmet Train)

In this classic Snake game, you control a snake that grows longer as it eats food. The objective is to eat as much food as possible without hitting the walls or your own tail. Your highest score is saved, and you can continue from a saved game if one exists.

### Bridge Game

The Bridge Game is a card game where users can play with a virtual deck of cards. Players earn experience points based on their performance.

### Dots and Boxes

Dots and Boxes is a puzzle game where players take turns connecting dots to form boxes. The player who completes the most boxes wins. Experience points are awarded based on performance.

### Dark Chess

In Dark Chess, the pieces are hidden from both players until they move. The game is a challenging variant of traditional chess that requires memory and strategy. Players earn experience points based on their progress and performance.

## Data Persistence

- User data, including passwords, experience, scores, and game progress, are saved in a `users.json` file.
- The platform automatically updates the file when changes are made, such as during login, registration, or gameplay.

## Video Demo

For a visual demonstration of the application, check out our video: [Video Link](https://www.youtube.com/watch?v=itxYqdAk32c&ab_channel=%E8%94%A1%E5%AE%9B%E7%A7%A6).
<br>

👨‍🏫 Advisor: CHIEN-LIANG LIU

###### tags: `Python` `pygame` `SnakeGame` `BridgeGame` `DotsAndBoxes` `DarkChess`

> 🔍 Watch MORE ➜ [My GitHub](https://github.com/username)
