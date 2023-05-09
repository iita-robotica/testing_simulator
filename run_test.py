import subprocess
import time
import os
import csv
import sys
import json
import pathlib

import datetime
import math
from PIL import ImageGrab


"""
parametros:

1. Archivo de mundos
"""


def loadController(erebus_directory, controller):
    erebusControllerPath = erebus_directory / "game/controllers/robot0Controller/robot0Controller.py"

    with open(controller, "r") as contToLoad:
        with open(erebusControllerPath, "w") as contToWrite:
            contToWrite.write(contToLoad.read())
    
    print(f"Loaded {controller}")

def openWebots(world):
    script = f"""#!/bin/bash
    webots {world} --mode=fast --minimize --no-rendering
    """
    rc = subprocess.Popen(script, shell=True)

def killWebots():
    script = """#!/bin/bash
    pkill webots
    """
    rc = subprocess.Popen(script, shell=True)

def processLogs(world, fileName, time_taken, log_directory):
    lastLog = sorted(os.listdir(log_directory))[-1]

    if "gameLog" in lastLog:
        with open(log_directory / lastLog, "r") as log:
            lines = log.readlines()
        
        finalLine = lines[-1]
        finalTime = (int(finalLine[0:2]) * 60) + int(finalLine[3:5])
        print("Final time:", finalTime, "seconds")

        for line in lines:
            if "ROBOT_0_SCORE: " in line:
                line = line.replace("ROBOT_0_SCORE: ", "")
                line = line.replace("\n", "")
                finalScore = float(line)
                print("Final score:", finalScore)
        
        with open(fileName, "a") as file:
            writer = csv.writer(file)

            writer.writerow([str(world).split("/")[-1], finalScore, finalTime, time_taken])



# Added functions:

def get_mission_time(log_file):
    with open(log_file, "r") as f:
        last_line = f.readlines()[-1]
    time_str = last_line.split()[0]
    mission_time = datetime.datetime.strptime(time_str, "%M:%S")
    return mission_time


def get_area_traveled(log_file):
    with open(log_file, "r") as f:
        lines = f.readlines()
    positions = []
    for line in lines:
        if "ROBOT_0_POSITION" in line:
            x, y, z = map(float, line.split()[-3:])
            positions.append((x, y))
    area_traveled = 0
    for i in range(1, len(positions)):
        dx = positions[i][0] - positions[i-1][0]
        dy = positions[i][1] - positions[i-1][1]
        distance = math.sqrt(dx*dx + dy*dy)
        area_traveled += distance
    return area_traveled


def get_detected_victims(log_file):
    with open(log_file, "r") as f:
        lines = f.readlines()
    detected_victims = 0
    for line in lines:
        if "DETECTED_VICTIM" in line:
            detected_victims += 1
    return detected_victims


def get_swamps(grid):
    num_swamps = 0
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == "S":
                num_swamps += 1
    return num_swamps


def take_grids_screenshot():
    # Get the position and size of the Webots window
    window_pos_x = 100
    window_pos_y = 100
    window_width = 800
    window_height = 600
    window_region = (window_pos_x, window_pos_y, window_pos_x + window_width, window_pos_y + window_height)

    # Take a screenshot of the whole Webots window
    screenshot = ImageGrab.grab(bbox=window_region)

    # Crop the image to the region of the grids
    grids_region = (10, 50, 610, 550)
    grids_screenshot = screenshot.crop(grids_region)

    # Save the image to a file
    grids_screenshot.save("grids_screenshot.png")



def testRun(world, fileName, log_directory):
    initialLogNumber = len(os.listdir(log_directory))
    newLogNumber = len(os.listdir(log_directory))

    print("Opening webots with world:", world)
    start_time = time.time()

    openWebots(world)
    while initialLogNumber == newLogNumber:
        newLogNumber = len(os.listdir(log_directory))

    print("Finished run")
    time_taken = time.time() - start_time
    print("Time taken:", time_taken, "seconds")

    time.sleep(1)

    print("Closing webots...")
    killWebots()
    

    print("Processing data...")
    processLogs(world, fileName, time_taken, log_directory)

def get_output_file_name(run_name, world_set_dir):
    actual_time = time.strftime("%d-%m-%Y_%H-%M-%S")

    formatted_world_set_name = world_set_dir.split("/")[-1]
    formatted_world_set_name = formatted_world_set_name.replace(".txt", "")

    return run_name + "_(" + formatted_world_set_name + ")_" + actual_time

def make_output_file(config):
    try:
        os.mkdir(pathlib.Path("./runs") / config["run_name"])
    except FileExistsError:
        print("Directory already exists")

    name = get_output_file_name(config["run_name"], config["world_set"]) + ".csv"

    output_file = pathlib.Path("./runs", config["run_name"], name)

    with open(output_file, "w") as output:
        writer = csv.writer(output)
        writer.writerow(["World", "Score", "Simulation Time", "Real Time"])
    
    return output_file

def test_runs(config):
    erebus_directory = pathlib.Path(config["erebus_directory"])

    log_directory = erebus_directory / "game/logs/"

    output_file = make_output_file(config)

    loadController(erebus_directory, config["controller"])

    with open(config["world_set"], "r") as worlds:
        lines = worlds.readlines()

        actualRuns = 0
        totalRuns = len(lines) * int(config["reps"])

        for world in lines:
            world = world.replace("\n", "")
            world = erebus_directory / ("game/worlds/" + world)
            for _ in range(int(config["reps"])):
                testRun(world, output_file, log_directory)
                actualRuns += 1
                time.sleep(1)
                print("Tested", actualRuns, "/", totalRuns, "simulations")


if __name__ == "__main__":
    with open(sys.argv[1], "r") as config_file:
        config = json.load(config_file)
    
    test_runs(config)
    








