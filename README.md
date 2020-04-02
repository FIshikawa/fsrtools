# fsrtools

"fsrtools" is management tools made by F.Ishikawa

## Console tools
The package has some console tools.

-  "fsrview" is a visualizer of experimetal results.

-  "fsrsimulate" is a simulator which is like wrapper.

## Installation
It is recommended to use virtualenv and install this package into the environment.

```bash
$ python3 -m venv your_directory
$ source your_directory/bin/activate
$ pip install -r requirements.txt
$ pip install -e fsrtools
$ source your_directory/bin/activate
```  

## Tutorial 
In three steps, you can execute your programs with this manager.

### First step : register your program in fsrsimulate.
First of all, you register your program in this manager.
This manager build excutation codes reffering to its registered programs list.
One of the console tools, "fsrsimulate", has "set_commands" mode.
If you perform the mode, you can see the registration console as the follows.
```bash
$ fsrsimulate --set_commnads

[Interactive Shell Mode]
[ATTENTION]
 [All configuration should be set by "fsrsimulate"]
 [You can see help by "fsrsimilate.help()"]
[Start IPython]
Python 3.7.3 (default, Dec 13 2019, 19:58:14) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]:  
```  
You can resistor your program though the interactive console by IPython.
Here, one example is showed by using a simple python code, "hello_world.py", in the tutorial directory.
This code accepts an argument on the console like, 
```bash
python hell_world.py 2
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
As you can see, the input form is a directory class of python.
The key, "hello_world", is the name of the command.
The list, `['python','./hello_world.py','N_loop']`, is a list corresponding to executed code on console.
The `N_loop` is a parameter that is the number of iterations.
Final sentence, `fsrsimulate.save()`, save the registered commands.
If you forget this, you cannot use the command.

### Second step : Set json file of parameter.
Next, you create a json file that includes input parameter.
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

### Final step : execute programs via json and manager.
After that, you execute the program by fsrsimulate as follows.
```bash
$ fsrsimulate -j parameter.json -lf log.dat --cout
```
You can ignore `--cout` option if you would not like to see the all process.
The option allow standard output the log data.
Same outputs are int the `log.dat`.

#### Note 
A directory, `results`, is made in the current directory.
It has a few of directories whose name are corresponds to the date.
However, you cannot see any files in the directories.
The reason is that the executed program, `hello_world.py`, does not create any files for result
but only perform standard output.

### Advanced : manage programs that create output files. 
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
    "experiment_1":{
      "experiment_params":{
        "command_name":"create_data"
        },
      "simulate_params":{
        "N_x":[8,10],
        "N_y":"N_x * 2"
        }
    }
  }
}
```
In this case, the result files are output in the `results_data` directory.


