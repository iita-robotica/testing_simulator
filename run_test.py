import subprocess
import time
import os
import csv
import sys
import json
import pathlib

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
    








