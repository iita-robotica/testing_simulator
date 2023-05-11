import subprocess
import time
import os
import csv
import sys
import json
from pathlib import Path
import platform

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

def getOpenScript(world):
    if platform.system() == "Linux":
        return f"""#!/bin/bash
        webots {world} --mode=fast --minimize --no-rendering
        """
    elif platform.system() == "Windows":
        return f"""webots {world} --mode=fast --minimize --no-rendering"""
    else:
        raise OSError("OS not supported. Please use either Windows or Linux")

def openWebots(world):
    script = getOpenScript(world)
    rc = subprocess.Popen(script, shell=True)

def getKillScript():
    if platform.system() == "Linux":
        return """#!/bin/bash
        pkill webots
        """
    elif platform.system() == "Windows":
        return """taskkill/im webots.exe /F"""
    
    else:
        raise OSError("OS not supported. Please use either Windows or Linux")


def killWebots():
    script = getKillScript()
    rc = subprocess.Popen(script, shell=True)

def processLogs(world: Path, fileName: Path, time_taken, log_directory: Path):
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

            writer.writerow([world.stem, finalScore, finalTime, time_taken])

def testRun(world: Path, fileName, log_directory: Path):
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

def get_output_file_name(run_name: str, world_set_dir: Path):
    actual_time = time.strftime("%d-%m-%Y_%H-%M-%S")

    return run_name + "_(" + world_set_dir.stem + ")_" + actual_time

def make_output_file(config):
    try:
        os.mkdir(Path("./runs") / config["run_name"])
    except FileExistsError:
        print("Directory already exists")

    name = get_output_file_name(config["run_name"], Path(config["world_set"])) + ".csv"

    output_file =Path("./runs", config["run_name"], name)

    with open(output_file, "w") as output:
        writer = csv.writer(output)
        writer.writerow(["World", "Score", "Simulation Time", "Real Time"])
    
    return output_file

def test_runs(config):
    erebus_directory = Path(config["erebus_directory"])

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
    








