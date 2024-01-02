import os.path
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
import json
import numpy as np
import re


# METHOD DEFINITION
# (You can directly import the method to use it)

def draw_policy_map(problem_path, policy=None, save_to_file=True):
    """
    Draws the specified problem and the learned policy for visualization. 

    Policy is expected to follow the following format:
    - A dictionary where each key (x, y) contains an action

    Actions are expected to be given in the format <"up", "right", "down", "left>
    (as strings)

    If save_to_file is True, a PNG file with the problem name will be stored in the
    current directory
    """

    # STEP 1 - PLOT THE PROBLEM

    # Read the problem path and store it as a dictionary
    with open(problem_path, "r") as file:
        problem_dict = json.load(file)

    # Extract the information from the JSON
    nrows, ncols = problem_dict["city"]["rows"], problem_dict["city"]["columns"]
    blocked = problem_dict["city"]["blocked"]
    departure = problem_dict["departure"]
    dangers = problem_dict["dangers"]
    trapped = problem_dict["trapped"]
    fatal_dangers = problem_dict["fatal_dangers"]

    # Create the x/y tick labels and their positions
    xticks_labels = np.arange(0, ncols, 1)
    xticks = xticks_labels + 0.5

    yticks_labels = np.arange(0, nrows, 1)
    yticks = yticks_labels + 0.5

    # Draw the matrix with the following colors:
    # 0 - Free - White
    # 1 - Blocked - Black
    # 2 - Dangers - Red
    # 3 - Departure - Green
    # 4 - Trapped - Blue
    # 5 - Fatal danger - Orange
    problem_matrix = np.zeros((nrows, ncols), int)

    # *blocked "separates" all elements of the list and feeds them one by one to zip
    # This extracts all [[x1, y1], [x2, y2]...] values into two lists: (x1, x2...) and (y1, y2...)
    if blocked:
        x_blocked, y_blocked = zip(*blocked)
        problem_matrix[x_blocked, y_blocked] = 1

    if dangers:
        x_dangers, y_dangers = zip(*dangers)
        problem_matrix[x_dangers, y_dangers] = 2

    # Departure can directly be uncoupled
    x_departure, y_departure = departure
    problem_matrix[x_departure, y_departure] = 3

    # Trapped and fatal dangers have an additional reward - we can store it separately
    x_trapped, y_trapped, reward_trapped = zip(*trapped)
    problem_matrix[x_trapped, y_trapped] = 4

    if fatal_dangers:
        x_fatal_dangers, y_fatal_dangers, reward_fatal_dangers = zip(*fatal_dangers)
        problem_matrix[x_fatal_dangers, y_fatal_dangers] = 5

    # Create the original figure
    plt.figure(figsize=(nrows, ncols))
    ax = plt.gca()

    # Create a color map for the city and plot it
    cmap = ListedColormap(["white", "black", "red", "green", "blue", "orange"])
    plt.pcolor(problem_matrix, cmap=cmap, edgecolors="k", vmin=0, vmax=5)

    # Invert the Y axis and set up the ticks properly
    ax.invert_yaxis()

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks_labels)

    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks_labels)

    # Display the x-axis ticks at the top
    ax.tick_params(axis = "x",
                   which = "both",
                   bottom = False,
                   labelbottom = False,
                   top = True,
                   labeltop = True)

    # STEP 2 - Draw the rewards
    # Trapped rewards
    for x, y, reward in zip(x_trapped, y_trapped, reward_trapped):
        plt.text(x=y + 0.5, y=x + 0.5, s=f"+{reward}", 
                 c="white", size=12, 
                 horizontalalignment="center",
                 verticalalignment="center")

    # Fatal dangers penalties
    if fatal_dangers:
        for x, y, reward in zip(x_fatal_dangers, y_fatal_dangers, reward_fatal_dangers):
            plt.text(x=y + 0.5, y=x + 0.5, s=str(reward), 
                     size=12, 
                     horizontalalignment="center",
                     verticalalignment="center")

    # STEP 3 - Draw the policy
    # Only drawn if a policy is specified
    if policy:
        # Define the values to increment for drawing the arrows
        increments = {"UP": (0.5, 0.75, 0.5, 0.25),
                    "RIGHT": (0.25, 0.5, 0.75, 0.5), 
                    "DOWN": (0.5, 0.25, 0.5, 0.75), 
                    "LEFT": (0.75, 0.5, 0.25, 0.5)}

        # Loop through all the policies
        # Note - policy is a Python dictionary
        # You need to pre-process it before using the method
        for (x, y), action in policy.items():

            # Extract the information
            action = str.upper(action)
            a, b, c, d = increments[action]
            xytext= (y + a, x + b)
            xy = (y + c, x + d)
            plt.annotate("", xy= xy, xytext=xytext, arrowprops={"arrowstyle": "->"})

    # Show the image and, if necessary, store it
    fig = plt.gcf()

    plt.show(block=False)
    if save_to_file:
        # Extract the file name
        file_name = os.path.splitext(os.path.basename(problem_path))[0]
        # Sanity check - if the file name is empty, give it a default name
        if not file_name:
            file_name = "image"
        
        # Save the image
        fig.savefig(file_name + ".png", bbox_inches = "tight")



# ACCESS POINT
if __name__ == "__main__":
    
    # MODIFY THESE VALUES TO LAUNCH THE CODE ##############################################
    # Path to the problem JSON
    problem_path = r"instances\lesson5-rl.json"

    # Path to the policy JSON
    policy_path = r"example_policies\lesson5-rl_policy.json"

    # Whether the image should only be shown on screen or also saved to a file
    save_image = True
    #######################################################################################

    # DO NOT MODIFY THIS CODE - ONLY COMMENT IT IF YOU'RE NOT USING A JSON FILE ###########
    # Transform the policy JSON into a Python dict
    policy_json_dict = json.load(open(policy_path, "r"))
    policy_dict = {(int(re.search(r"\((?P<x>\d+),\s*(?P<y>\d+)\)", key).group("x")),
                    int(re.search(r"\((?P<x>\d+),\s*(?P<y>\d+)\)", key).group("y"))): value 
                    for key, value in policy_json_dict.items()}
    ########################################################################################
    print(policy_dict)

    # Code launch
    # If no policy is specified, only the map with the rewards is drawn
    draw_policy_map(problem_path, policy=policy_dict, save_to_file=save_image)