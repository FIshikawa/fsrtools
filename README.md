![](https://github.com/FIshikawa/fsrtools/workflows/Python%20package/badge.svg)

# fsrtools

"Friendly Simulating and Recording tools (fsrtools)" is a package managing numerical simulations.

## Features

- Console tools

    The package has two console tools.

    -  "fsrview" is a visualizer of experimetal results.

    -  "fsrsimulate" is a simulator which is like wrapper.

## Requirements
This package requires python3.x (x > 5) and some packages.
See setup.cfg and github actions.

## Installation
It is recommended to use virtualenv and install this package in the environment.

```bash
$ python3 -m venv your_directory
$ source your_directory/bin/activate
$ pip install -e fsrtools
$ source your_directory/bin/activate
```  

## Tutorial 
### fsrsimulate
"fsrsimulate" is the console tool which enable you to execute your programs with simple parameter files.
In three steps, you can execute your programs with this command.

##### Note 
All programs you want to execute should be able to obtain the parameters via the argument.

#### First step : register your program in fsrsimulate.
First of all, you register your programs in this manager.
This manager builds excutation codes reffering to the list included in the package directory.
"fsrsimulate" has "set_commands" mode which provides an interactive shell to register the programs.
If you open the mode, you can see the registration console as the follows.
```bash
$ fsrsimulate --set_commnads

[Command Manager : Interactive Shell Mode]
[ATTENTION]
 [All configuration should be set via "fsrsimulate"]
 [You can see help by "help(fsrsimilate)"]
[Start IPython]
[Registered commands]
 print as " [number] : name ".
Python 3.7.3 (default, Dec 13 2019, 19:58:14) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]:  
```  
You can resistor your program though the interactive console by IPython.
Here, one example is shown with using a simple python code, "hello_world.py", in the tutorial directory.
This code accepts an argument on the console like, 
```bash
$ python hell_world.py 2
Hello World!
Hello World!
```
In this situation, you register the simple code with the registration console.
```bash
In [2]:  fsrsimulate.add_command({'hello_world' : ['python','hello_world.py','N_loop']})
add command "hello_world"
{'hello_world': ['python', 'hello_world.py', 'N_loop']}

In [3]: fsrsimulate.save()                                                      
save now defined commands
```
As you can see, the input form is a dictionary class of python.
The key, "hello_world", is the name of the command.
The list, `['python','hello_world.py','N_loop']`, is a list corresponding to the code executed on your console.
The `N_loop` is a parameter that is the number of iterations.
Final sentence, `fsrsimulate.save()`, saves the registered command.
If you forget this, you cannot use the command because the console tool does not know it.
After registration and reopen the mode, you see the follows.
```bash
$ fsrsimulate --set_commnads

[Command Manager : Interactive Shell Mode]
[ATTENTION]
 [All configuration should be set via "fsrsimulate"]
 [You can see help by "help(fsrsimilate)"]
[Start IPython]
[Registered commands]
 print as " [number] : name ".
  [0] : hello_world 
Python 3.7.3 (default, Dec 13 2019, 19:58:14) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]:  
```
By using `fsrsimulate.view_command(command_id)`, you see the executable code of the command like,
```bash
In [1]: fsrsimulate.view_command(command_id=0)                                                                                                                           
command name : hello_world
  ['python', 'hello_world.py', 'N_loop']

In [2]: fsrsimulate.view_command(command_id='hello_world')                                                                                                               
command name : hello_world
  ['python', 'hello_world.py', 'N_loop']
```
You can also remove the registered command with `fsrsimulate.remove_command(commmand_name=you_want_to_remove)`.

#### Second step : Set json file of parameter.
Next, you create a json file including the input parameters.
An example is in the tutorial directory, whose name is `parameter_hello_world.json`.
```bash
{
  "experiment_dir":"results/",
  "experiments":{
    "experiment_1":{
      "experiment_params":{
        "command_name":"hello_world"
        },
      "simulate_params":{
        "N_loop":4
        }
    },
    "experiment_2":{
      "experiment_params":{
        "command_name":"hello_world"
        },
      "simulate_params":{
        "N_loop":"Ns * 4",
        "Ns":[1,2]
        }
    }
  }
}
```

#### Final step : execute programs via manager with json file.
After that, you execute the program via `fsrsimulate` as follows.
```bash
$ fsrsimulate -j parameter.json -lf log.dat --cout
```
You can ignore `--cout` option if you would not like to see the all process explicitly.
The option allows standard output of the log.
Same outputs are written in the `log.dat`.
You can also check the progress of simulations executed in backgraound via the following command at a glance.
```bash
$ fsrsimulate -j parameter.json -lf log.dat &
$ fsrsimulate --log log.dat
```

##### Note 
A directory, `results`, is made in the current directory.
It has a few of directories whose name are corresponds to the date.
However, you cannot see any files in the directories.
The reason is that the executed program, `hello_world.py`, does not create any files for result
but only perform standard output.

#### Advanced : manage programs that create output files. 
In usual cases, it is necessary to make a lot of result files.
An example, `create_data.py`, is in the tutorial directory.
You register the program as the follwoing.

```bash 
In [2]: fsrsimulate.add_command({'create_data' : ['python','create_data.py','result_directory','N_x','N_y']})
```
The `result_directory` parameter is the directory including result files finally.

The parameter file is like,

```bash
{ 
  "experiment_dir":"results_data/",
  "experiments":{
    "experiment_1":{
      "experiment_params":{
        "command_name":"create_data"
      },
      "simulate_params":{
        "N_x":[1024,1280,1536],
        "N_y":"N_x * 2"
      }
    }
  }
}
```
In this case, the result files are output in the `results_data` directory.
If you perform the program with background executation, you can check the progress with `--log` mode like,
```bash
[input log file : log.dat]
[parameter file : parameter_create_data.json]
[result directory : your_exected_directory/results_data/2020-04-28-11-28-13]
[server name : your_host]
[number of experiments : 1]
  [experiment_1] : [start 2020/04/28 11:34:49] : [past 0:00:45.241581] : [ongoing  number-3 (3/3)]
    [command_name : create_data] [change params : N_x,]
      [number-1] : [start 2020/04/28 11:34:49] : [end 2020/04/28 11:35:06] : [duration 0:00:17.123402] 
      [number-2] : [start 2020/04/28 11:35:06] : [end 2020/04/28 11:35:33] : [duration 0:00:27.282645] 
      [number-3] : [start 2020/04/28 11:35:33] : [past 0:00:01.246004] 
```
