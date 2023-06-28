# This is the automatic testing environment of the Talos team for the RoboCup 2023 competition

This is a program capable of testing an erebus controller by running many webots simulations and compilating analytics in a .csv file that can then be analyzed in the spread-sheet program of your choice.

## How it works

The program uses a modified version of the Erebus platform that automatically starts the loaded controller when the robot window is opened. The script launches one or more webots instances, and then processes the logs that erebus leaves once a run is finished in the ```erebus/game/logs/``` directory.

## How to use it

### 1. Worlds

Firstly, you must have some worlds in the ```erebus/game/worlds``` directory. Let's say your ```worlds``` directory has the following files: ``` world1.wbt world2.wbt room4.wbt ```

### 2. World Set

Now go back to the root of the repo, and go to the ```world_sets/``` directory. There, create a text file named ```my_world_set.txt```. in the file write the following:

``` txt
world1.wbt
world2.wbt
room4.wbt
```

Be careful not to include any white lines or white space after each world.

### 3. Config File

Now, in the root of the repo, you can create a config file. Create a text file with the name ```my_config.json``` that looks like this:

``` json
{
    "erebus_directory": "./erebus",
    "controller": "[path to your erebus controller]",
    "world_set": "./world_sets/my_world_set.txt",
    "batch_number":3,
    "reps":5,
    "timeout_minutes": 9.0,
    "run_name": "my_run"
}
```

The parameters mean the following:

* **erebus_directory:** path to erebus. You can use any version you like, but you will have to modify it so that it automatically starts when a new webots instance is launched.
* **controller:** path of your controller file. The program will load it automatically when starting.
* **world_set:** path of your world set txt file.
* **reps:** how many times to run the same world in parallel. This number depends on your computer. More doesn't mean faster. We recommend a maximum of 5, because above that number the logs that are written at the same time overwrite eachother and the testing environment has to run the missing tests again, wasting time.
* **batch_number:** how many times to run each batch of simulations consecutively. This depends on how accurate you want your results to be. There is no limit to this, only more time.
* **timeout_minutes:** How much real time has to pass before the script decides that an error has occured or that some log data has been lost. The current real-time limit of erebus is 9 minutes, so a 9 minute timeout is very reasonable. If you program normally goes considerably faster than real time, you might get away with less, but remember that it could cause some skew in the data if one of the runs takes more time than normal.
* **run_name:** What are you testing? A folder of this name will be created (or used if it already exists), and there all runs with that name will be saved.

Note: a total of around 15 runs (batch_number x reps) is more or less statistically significative with world-set of a few worlds, but the more the better.

### 4. Simulator Prep

Almost there! Before finally starting the simulations, open each one of the worlds you want to use, manually open the robot window and then close the simulator.

At this stage you can also load the robot json if you have one. Pause the simulation in the webots window (not in the erebus window), and press the reset button in webots. Before the simulation starts you will have the chance to load your json, and then unpause the simulation to build the robot.

### 5. Starting the tests

Close any webots instances you might have open. Go to the root of the repo and run ```python run_test.py my_config.json```. After a few seconds the webots instances will start appearing.  You can check the terminal for debug info and estimates of how much time is left in the test.

### 6. Analyzing the data

Once the tests are finished, got to the ```runs/``` directory, and locate the folder with the name specified on your config file. There you will find all runs with that name, ordered by date, time and chosen world set. You can import a file into any spread-sheet program to analyze it.

You will see that there are empty columns. You can optionally fill them if you have the data of the worlds you are testing, for easier analysis. In others you can do the spread-sheet calculations to obtain percentages and totals.

In the ```scripts/``` directory you will find some scripts that can help you obtain data from the .json files of the worlds. More data can also be found by loading the world in the erebus world editor [https://osaka.rcj.cloud/service/editor/simulation/2023] and pressing the calculator icon.

## Licence

Our code is free and open-source under the MIT license! That means you can do whatever you want with it. We encourage you to see our code, take inspiration and copy it. You can also make your own fork of this repsitory and share your innovations upon it. We are exited to share and innovate together, and in this spirit we would like to encourage you to do the same, so we can all grow together. Only one thing: if you end up copyign big parts as-is, it would be nice if you gave us some credit ;).

``` txt
         .--.             .---.
        /:.  '.         .' ..  '._.---.
       /:::-.  \.-"""-;` .-:::.     .::\
      /::'|  `\/  _ _  \'   `\:'   ::::|
  __.'    |   /  (o|o)  \     `'.   ':/
 /    .:. /   |   ___   |        '---'
|    ::::'   /:  (._.) .:\
\    .='    |:'        :::|
 `""`       \     .-.   ':/
       jgs   '---`|I|`---'
                  '-'
                  
```
