# import random
import numpy as np
import time # diagnostics
from typing import List, Dict

"""
This file can be a nice home for your Battlesnake's logic and helper functions.

We have started this for you, and included some logic to remove your Battlesnake's 'neck'
from the list of possible moves!
"""

def get_info() -> dict:
    """
    This controls your Battlesnake appearance and author permissions.
    For customization options, see https://docs.battlesnake.com/references/personalization

    TIP: If you open your Battlesnake URL in browser you should see this data.
    """
    return {
        "apiversion": "1",
        "author": "timothycho",  # TODO: Your Battlesnake Username
        "color": "#3E338F",  # TODO: Personalize
        "head": "sand-worm",  # TODO: Personalize
        "tail": "ghost",  # TODO: Personalize
    }


def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request

    return: A String, the single move to make. One of "up", "down", "left" or "right".

    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.

    """
    # diagnostics
    # sTime = time.time() 
  
    my_snake = data["you"]      # A dictionary describing your snake's position on the board
    my_head = my_snake["head"]  # A dictionary of coordinates like {"x": 0, "y": 0}
    my_body = my_snake["body"]  # A list of coordinate dictionaries like [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}]
    my_health = my_snake["health"]
  
    food = data["board"]["food"]
    snakes = data["board"]["snakes"]
    # print(data)
    # Uncomment the lines below to see what this data looks like in your output!
    # print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    # print(f"All board data this turn: {data}")
    # print(f"My Battlesnake this turn is: {my_snake}")
    # print(f"My Battlesnakes head this turn is: {my_head}")
    # print(f"My Battlesnakes body this turn is: {my_body}")

    possible_moves = ["up", "down", "left", "right"]
    possible_moves = _avoid_my_neck(my_body, possible_moves)
    possible_moves = avoid_walls(my_body, possible_moves)
    possible_moves = avoid_snakes(my_head, snakes, possible_moves, data["you"]["length"])
    
    numMoves = len(possible_moves[0])
    # find food a bit earlier when uneven length to avoid head snipes
    if (my_health < 33 or (my_health < 38 and data["you"]["length"] % 2 == 1)) and numMoves != 0:
      move = find_food(my_head, data["board"]["food"], possible_moves[0], possible_moves[1])
    else:
      move = chase_tail(my_head, my_body, possible_moves[0], possible_moves[1])

    # diagnostics
    # eTime = time.time() 
    # lapse = eTime - sTime
    print(f"MOVE {data['turn']}: {move} picked from all valid options in {possible_moves} Health: {my_health}")
    # print(f"Choose Move Time: {round(lapse*1000,4)}ms")
  
    return move


def _avoid_my_neck(my_body: dict, possible_moves: List[str]) -> List[str]:
    """
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}]
    possible_moves: List of strings. Moves to pick from.
            e.g. ["up", "down", "left", "right"]

    return: The list of remaining possible_moves, with the 'neck' direction removed
    """
    my_head = my_body[0]  # The first body coordinate is always the head
    my_neck = my_body[1]  # The segment of body right after the head is the 'neck'

    if my_neck["x"] < my_head["x"]:  # my neck is left of my head
      possible_moves.remove("left")
    elif my_neck["x"] > my_head["x"]:  # my neck is right of my head
      possible_moves.remove("right")
    elif my_neck["y"] < my_head["y"]:  # my neck is below my head
      possible_moves.remove("down")
    elif my_neck["y"] > my_head["y"]:  # my neck is above my head
      possible_moves.remove("up")

    return possible_moves

def avoid_snakes(my_head, snakes, possible_moves, length):
  # grid = [
  #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  # ]  
  # create grid
  grid = np.zeros((11, 11),dtype=int) # switch to numpy since slightly bit faster
  
  # moves that will lead to potential head to head collisions
  panic_moves = [] 

  for snakeIndex in range(len(snakes)):
    # Adds the possible ways a snake head could move if it has more health
    if snakes[snakeIndex]["body"][0] != my_head and snakes[snakeIndex]["length"] >= length:
      if snakes[snakeIndex]["body"][0]["x"] - 1 >= 0:
        grid[snakes[snakeIndex]["body"][0]["y"]][snakes[snakeIndex]["body"][0]["x"]-1] = 2
      if snakes[snakeIndex]["body"][0]["x"] + 1 <= 10:
        grid[snakes[snakeIndex]["body"][0]["y"]][snakes[snakeIndex]["body"][0]["x"]+1] = 2
      if snakes[snakeIndex]["body"][0]["y"] - 1 >= 0:
        grid[snakes[snakeIndex]["body"][0]["y"]-1][snakes[snakeIndex]["body"][0]["x"]] = 2
      if snakes[snakeIndex]["body"][0]["y"] + 1 <= 10:
        grid[snakes[snakeIndex]["body"][0]["y"]+1][snakes[snakeIndex]["body"][0]["x"]] = 2
        
    for bodyIndex in range(len(snakes[snakeIndex]["body"])-1):
      # Adds every body part except the tail
      grid[snakes[snakeIndex]["body"][bodyIndex]["y"]][snakes[snakeIndex]["body"][bodyIndex]["x"]] = 1

  # Remove killing moves using grid
  # removed the try/excepts since out of index moves were removed earlier with avoid_walls()
  # builds panic list of potential moves with possible head to head collision in case no other safe moves
      
    if "up" in possible_moves:
      if grid[my_head["y"]+1][my_head["x"]] >= 1:
        possible_moves.remove("up")
        if grid[my_head["y"]+1][my_head["x"]] == 2:
          panic_moves.append("up") 

    if "down" in possible_moves:
      if grid[my_head["y"]-1][my_head["x"]] >= 1:
        possible_moves.remove("down")
        if grid[my_head["y"]-1][my_head["x"]] == 2:
          panic_moves.append("down")

    if "left" in possible_moves:
      if grid[my_head["y"]][my_head["x"]-1] >= 1:
        possible_moves.remove("left")
        if grid[my_head["y"]][my_head["x"]-1] == 2:
          panic_moves.append("left")

    if "right" in possible_moves:
      if grid[my_head["y"]][my_head["x"]+1] >= 1:
        possible_moves.remove("right")
        if grid[my_head["y"]][my_head["x"]+1] == 2:
          panic_moves.append("right")

    

  return [possible_moves, panic_moves]
  
  # if {"x": my_head["x"], "y": my_head["y"]} in my_body:
  #   my_body.remove({"x": my_head["x"], "y": my_head["y"]})

def find_food(my_head, food, possible_moves, panic_moves):
  closestFood = {"x": 5, "y": 5}
  closestDist = 50
  print("Find Food")
  for i in range(len(food)):
    dist = abs(my_head["x"] - food[i]["x"]) + abs(my_head["y"] - food[i]["y"])
    #print(dist, closestDist)
    if dist < closestDist:
      closestDist = dist
      closestFood = food[i]
    
  xDiff = abs(my_head["x"] - closestFood["x"])
  yDiff = abs(my_head["y"] - closestFood["y"])
  
  execute = True
  if xDiff >= yDiff:
    execute = False
    if my_head["x"] > closestFood["x"]:
      choice = "left"
    else:
      choice = "right"
    
    if choice not in possible_moves:
      execute = True

  if execute:
    if my_head["y"] > closestFood["y"]:
      choice = "down"
    else:
      choice = "up"
    
    if choice not in possible_moves:
      print("FindFood Can't Move -> Picks First Moves")
      return possible_moves[0]
  
  return choice

def chase_tail(my_head, my_body, possible_moves, panic_moves):
  my_neck = my_body[1]
  my_tail = my_body[-1]

  xDiff = abs(my_head["x"] - my_tail["x"])
  yDiff = abs(my_head["y"] - my_tail["y"])
  print("Tail Chase")
  
  # if no safe moves, use moves with potential head to head collision
  if len(possible_moves) == 0:
    possible_moves = panic_moves
  # removes option to move straight when able to turn (tries to keep turning)
  if len(possible_moves) > 2:
    if my_head["y"] > my_neck["y"] and "up" in possible_moves:
      possible_moves.remove("up")
    elif my_head["y"] < my_neck["y"] and "down" in possible_moves:
      possible_moves.remove("down")
    elif my_head["x"] > my_neck["x"] and "right" in possible_moves:
      possible_moves.remove("right")
    elif my_head["x"] < my_neck["x"] and "left" in possible_moves:
      possible_moves.remove("left")

  execute = True

  # Try to move away from edge of map
  if len(possible_moves) >= 2:
    if my_head["x"] >= 8 and "left" in possible_moves:
      choice = "left"
      execute = False
    if my_head["x"] <= 2 and "right" in possible_moves:
      choice = "right"
      execute = False
    if my_head["y"] >= 8 and "down" in possible_moves:
      choice = "down"
      execute = False
    if my_head["y"] <= 2 and "up" in possible_moves:
      choice = "up"
      execute = False

  if execute:
    if my_head["x"] == my_tail["x"] and my_head["x"] == my_neck["x"] and my_head["x"] == my_body[2]["x"]:
      if "left" in possible_moves:
        choice = "left"
        execute = False
      elif "right" in possible_moves:
        choice = "right"
        execute = False
    if my_head["y"] == my_tail["y"] and my_head["y"] == my_neck["y"] and my_head["y"] == my_body[2]["y"]:
      if "up" in possible_moves:
        choice = "up"
        execute = False
      elif "down" in possible_moves:
        choice = "down"
        execute = False
  
  if execute: 
    execute = False
    if my_head["x"] > my_tail["x"]:
      choice = "left"
    else:
      choice = "right"
    
    if choice not in possible_moves:
      execute = True

  if execute:
    if my_head["y"] > my_tail["y"]:
      choice = "down"
    else:
      choice = "up"
    
    if choice not in possible_moves:
      if len(possible_moves) > 0:
        print(possible_moves)
        print("ChaseTail Can't Move -> Picks First Moves")
        return possible_moves[0]
      else: # 
        print("None")
        choice = None
          
  return choice

def avoid_walls(my_body: dict, possible_moves: List[str]) -> List[str]:
  my_head = my_body[0] 
  if my_head["x"] in [0,10] or my_head["y"] in [0,10]: 
    # if move would go into wall, remove it
    if my_head["x"] + 1 > 10 and "right" in possible_moves:
      possible_moves.remove("right")
    if my_head["x"] - 1 < 0 and "left" in possible_moves:
      possible_moves.remove("left")
    if my_head["y"] + 1 > 10 and "up" in possible_moves:
      possible_moves.remove("up")
    if my_head["y"] - 1 < 0 and "down" in possible_moves:
      possible_moves.remove("down")
  return possible_moves

# possible things to do:
# try another hosting service maybe
# something to help avoid dead ends

# Games History:
# https://play.battlesnake.com/u/timothycho/georgemartha/ 
  
