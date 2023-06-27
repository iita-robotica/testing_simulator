import subprocess
import time
import os
import csv
import sys
import json
from pathlib import Path
import platform
import random

"""
parametros:

1. Archivo de mundos
"""

port = 1234

def loadController(erebus_directory, controller):
    erebusControllerPath = erebus_directory / "game/controllers/robot0Controller/robot0Controller.py"

    with open(controller, "r") as contToLoad:
        with open(erebusControllerPath, "w") as contToWrite:
            contToWrite.write(contToLoad.read())
    
    print(f"Loaded {controller}")

def getOpenScript(world):
    global port
    port += 1
    if platform.system() == "Linux":
        return f"""#!/bin/bash
        webots {world} --mode=fast --minimize --no-rendering --port={port}
        """
    elif platform.system() == "Windows":
        return f"""webots {world} --mode=fast --minimize --no-rendering --port={port}"""
    else:
        raise OSError("OS not supported. Please use either Windows or Linux")

def openWebots(world):
    print("Opening webots with world:", world)
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

def processLog(world: Path, input_file_name: Path, output_file_name: Path, time_taken, log_directory: Path):
    if "gameLog" not in input_file_name:
        return
    
    with open(log_directory / input_file_name, "r") as log:
        lines = log.readlines()
    
    # Score
    for line in lines:
        if "ROBOT_0_SCORE: " in line:
            line = line.replace("ROBOT_0_SCORE: ", "")
            line = line.replace("\n", "")
            finalScore = float(line)
            


    # Hazards
    hazards_detected = 0
    hazards_correctly_identified = 0
    victims_detected = 0
    victims_correctly_identified = 0
    checkpoints_found = 0
    fixture_type_missidentification = 0
    completion_percentage = 0
    finalTime = 8*60
    lack_of_progress_n = 0

    for line in lines:
        if "Successful Exit" in line:
            finalTime = (int(line[0:2]) * 60) + int(line[3:5])

        if "Successful Hazard Identification" in line:
            hazards_detected += 1
        elif "Successful Hazard Type Correct Bonus" in line:
            hazards_correctly_identified += 1

        elif "Successful Victim Identification" in line:
            victims_detected += 1
        
        elif "Successful Victim Type Correct Bonus" in line:
            victims_correctly_identified += 1

        elif "Found checkpoint" in line:
            checkpoints_found += 1

        elif "Map Correctness" in line:
            completion_percentage = line[-7:-2].replace(" ", "")
            completion_percentage = float(completion_percentage) / 100

        elif "Misidentification" in line:
            fixture_type_missidentification += 1

        elif "Lack of Progress" in line:
            lack_of_progress_n += 1

    print("Final time:", finalTime, "seconds")
    print("Final score:", finalScore)

    with open(output_file_name, "a") as file:
        writer = csv.writer(file)

        writer.writerow([world.stem,
                         "",
                         finalScore,
                         "",
                         finalTime,
                         time_taken, 
                         completion_percentage,
                         hazards_detected, 
                         hazards_correctly_identified,
                         victims_detected,
                         victims_correctly_identified,
                         "",
                         "",
                         fixture_type_missidentification,
                         checkpoints_found,
                         lack_of_progress_n,])
        

def processLogs(world: Path, file_name: Path, time_taken, log_directory: Path, number_of_logs: int):
    log_list = sorted(os.listdir(log_directory))
    for log in log_list[-number_of_logs:]:
        processLog(world, log, file_name, time_taken, log_directory)
    

def testRunsUntilDone(world: Path, fileName, log_directory: Path, reps: int, timeout):
    initialLogNumber = len(os.listdir(log_directory))
    newLogNumber = len(os.listdir(log_directory))

    
    start_time = time.time()

    for _ in range(reps):
        time.sleep(random.randint(1, 8))
        openWebots(world)
    
    while True:
        newLogNumber = len(os.listdir(log_directory))

        new_logs_count = newLogNumber - initialLogNumber

        if time.time() - start_time > timeout:
            killWebots()
            testRunsUntilDone(world, fileName, log_directory, reps - new_logs_count, timeout + 60)

        if new_logs_count >= reps:
            break

    print("Finished run")
    time_taken = time.time() - start_time
    print("Time taken:", time_taken, "seconds")

    time.sleep(1)

    print("Closing webots...")
    killWebots()
    if reps == 0:
        return 0
    else:
        return time_taken / reps

def testRun(world: Path, fileName, log_directory: Path, reps: int, timeout):
    
    time_taken = testRunsUntilDone(world, fileName, log_directory, reps, timeout)

    print("Processing data...")
    processLogs(world, fileName, time_taken, log_directory, reps)

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
        writer.writerow(["World",
                         "Max Score",
                         "Score",
                         "Score Percentage",
                         "Simulation Time", 
                         "Real Time",
                         "final map correctness",
                         "hazards_detected", 
                         "hazards_correctly_identified",
                         "victims_detected",
                         "victims_correctly_identified",
                         "max_fixture_total",
                         "fixture_total",
                         "fixture_type_missidentification",
                         "checkpoints found",
                         "lack_of_progress_count"])
    
    return output_file

def test_runs(config):
    
    erebus_directory = Path(config["erebus_directory"])
    reps = int(config["reps"])
    batch_number = int(config["batch_number"])

    log_directory = erebus_directory / "game/logs/"

    output_file = make_output_file(config)

    loadController(erebus_directory, config["controller"])

    with open(config["world_set"], "r") as worlds:
        lines = worlds.readlines()

        actualRuns = 0
        totalRuns = len(lines) * int(config["reps"]) * batch_number

        init_time = time.time()

        for world in lines:
            
            print("#########################################################")
            world = world.replace("\n", "")
            world = erebus_directory / ("game/worlds/" + world)
            
            for _ in range(batch_number):
                testRun(world, output_file, log_directory, reps, timeout=60*4)
                actualRuns += reps
                time.sleep(1)
                print("Tested", actualRuns, "/", totalRuns, "simulations")

                time_so_far = time.time() - init_time
                print("Total time so far:", time_so_far / 60, "minutes")
                print("Estimated time left:", time_so_far / actualRuns * (totalRuns - actualRuns) / 60, "minutes")


if __name__ == "__main__":
    with open(sys.argv[1], "r") as config_file:
        config = json.load(config_file)
    
    test_runs(config)
    








