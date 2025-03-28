from DOTs_and_BOXes.gameStart import DNBstartgame
from DOTs_and_BOXes.gameMenu import main as menu_main
from DOTs_and_BOXes.game import start_game
from DOTs_and_BOXes.game_over import main as game_over_main

def DnBmain():
    state = "Start" 
    exp = 0
    scores = {"Player": 0, "Computer": 0}
    winner = "Computer" 
    while True:
        if state == "Start":
            # print(f"Starting the game...state{state}")
            state = DNBstartgame()
        elif state == "gameMenu":
            # print(f"Opening game menu...state{state}")
            players, board_size, difficulty, theme, state = menu_main()  
            print(f"flow theme{theme}")
        elif state == "game":
            # print(f"Starting gameplay...state{state}")
            winner, scores["Player"], scores["Computer"], state = start_game(players, board_size, difficulty, theme)  
            
        elif state == "game_over":
            # print(f"Game over...state{state} exp{exp}")
            exp, state = game_over_main(winner, scores["Player"], scores["Computer"]) 
        elif state == "main_menu":
            # print("Returning to main program...state{state}")
            break  
        else:
            print(f"Unknown state: {state}")
            break
    # print("Returning to main program...")
    return exp, state 

if __name__ == "__main__":
    DnBmain()
