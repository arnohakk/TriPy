# TriPy

## A toolbox for creating joint attention paradigms with a virtual agent

When using this code (or parts of it), please cite the following paper:

XXX

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" href="http://purl.org/dc/dcmitype/Text" property="dct:title" rel="dct:type">TriPy</span> by <a xmlns:cc="http://creativecommons.org/ns#" href="https://github.com/arnohakk/TriPy" property="cc:attributionName" rel="cc:attributionURL">Arne Hartz and Martin Schulte-Rüther</a> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.

Main contributors: [Arne Hartz](https://github.com/arnohakk),  [Björn Guth](https://github.com/scattenlaeufer), and [Martin Schulte-Rüther](https://github.com/msrlab)

## Dependencies

* [PyGaze](http://www.pygaze.org/)
* [pyglet](https://pypi.python.org/pypi/pyglet)
* [pyHook](https://pypi.python.org/pypi/pyHook)
* [msgpack](https://pypi.python.org/pypi/msgpack-python)

Currently, only out-of-the-box support for Tobii SKD is given. As this toolbox is based on PyGaze adaption should cost minimal effort.

## Running a experiment
- Start a console in folder containing `run_experiment.py`
- Run `python run_experiment.py` to start the default paradigm
- Run `python run_experiment.py --exp_tpye <name>` to start paradigm defined in file `studies/<name>`

## Compiler flags for usage for testing/development
- `-c` /  `--auto_create`: Creates automatically an agent
- `-a`/`--draw_aois`: Draw boxes around used AOIs
- `-f`: Skips the entire calibration and uses the most recent           calibrations instead
- `-i`/`--skip_instr`: Skips the instruction screen at the beginning of the paradigm
- `-k`/`--skip_key_input`: No key input needed to continue during all instruction screens
- `-o`/`--options`: Set a special VARIABLE to a given VALUE
- `-t`: Enters pre-set test data (Name, sex, age)  of test subject automatically
- `-r`: Reloads previously used proband
- `-d`, `--delete`: Deletes test proband log files (1337_H4x0r) before starting the paradigm. Should be used in combination with `-t` when same block as before is wanted
- `--exp_type`: Select an experiment type: basic or ja_nirs, their corresponding config file will be imported
- `--gaze_cursor`: Show gaze cursor ??
- `--agent`: Define the agent, which will be used
- `--code`: Sets the subject code used for saving the data ??
- `--runs`: Number of runs, the defined agent will do
- `--gui`: Only run the setup window
- `--screenshots`: Capture screenshots
- `--aoi_border_size`: Thickness of the AOI box border
- `--stopwatch`: Run a stopwatch during the experiment, printing the current time every SEC
- `--force_quit`: Force experiment to quit at the end
- `--gamify`: Give points and keep score
- `--block`: Set block to run

## Important files

- `agents.py`: Code for agent behavior
- `run_experiment.py`: Starting experiment, screen presentation
- `studies/basic.py`: Example paradigm
- `experiment_parameters.py`: All experimental options can also be defined here and these default values will be overwritten by definitions in `studies/<study_name>.py` when running `python run_experiment.py --exp_type <study_name>`
