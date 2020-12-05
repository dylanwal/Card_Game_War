
import War_Class
import requests
import multiprocessing
from statistics import mean, stdev

session = None


def set_global_session():
    global session
    if not session:
        session = requests.Session()


def run_single_game(run):
    game = War_Class.GameWar(num_players=2, num_decks=2, shuffle=True, jokers=True, show=False)
    # print(f"{run}      Winner is: {str(game.winner)} in {game.num_turns} of turns. (Wars: {game.num_wars})")
    return game.num_turns


def run_multiple_games(runs):
    with multiprocessing.Pool() as pool:
        turns = pool.map(run_single_game, runs)

    print(f"num of infinite games: {turns.count(1000000)}   ,{turns.count(1000000)/5000*100} %")
    turns[:] = [x for x in turns if x != 1000000]
    print(f"mean: {mean(turns)}, stdev: {stdev(turns)}, min: {min(turns)}, max: {max(turns)}")



if __name__ == '__main__':
    runs = [i for i in range(500)]
    run_multiple_games(runs)

    print("Program Done")

"""Results:
(After playing 10,000 games)
Players:2, decks:1, shuffle:False, joker:False   ||||   mean turns: 477+-330 (min:42,max:3050), infinite games: 4.7% 
Players:2, decks:1, shuffle:True, joker:False   ||||   mean turns: 377+-238 (min:40,max:2244), infinite games: 0.0001%
Players:2, decks:1, shuffle:True, joker:True   ||||   mean turns: 2117+-3407 (min:47,max:29608), infinite games: 0%
Players:2, decks:1, shuffle:False, joker:True   ||||   mean turns: 2227+-3627 (min:47,max:40176), infinite games: 4.4%
Players:3, decks:1, shuffle:True, joker:False   ||||   mean turns: 369+-260 (min:36,max:3307), infinite games: 0%
Players:5, decks:1, shuffle:True, joker:False   ||||   mean turns: 353+-257 (min:16,max:1756), infinite games: 0%
Players:2, decks:2, shuffle:True, joker:False   ||||   mean turns: 743+-349 (min:142,max:3617), infinite games: 0% 
Players:2, decks:2, shuffle:False, joker:False   ||||   mean turns: 882+-430 (min:138,max:3852), infinite games: 0.12% 
Players:2, decks:2, shuffle:True, joker:True   ||||   mean turns: 22072+-60268 (min:221,max:570506), infinite games: 0% 
"""
