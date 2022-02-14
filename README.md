# bonobo

## Setup & Installation

Make sure you have the latest version of Python installed.

```bash
git clone <repo-url>
```

or download zip-file from https://github.com/markusrobertjonsson/bonobo/ and unzip.

## Running the experiment

```bash
python bonobo.py
```

## Instructions

- Configurations are in `config.py` such as the bonobo's name
- Output is written to `result_files/CEK2022_[bonobo_name]`, i.e. there is one output file per individual
- &lt;F11> toggles full screen
- &lt;F10> toggles visibility of mouse pointer
- &lt;Space> pauses the experiment and a pause screen with current experiment status is displayed; another space resumes it
- If an experiment is aborted it will be resumed from where it was aborted when restarted. However, in the pretraining, the score of the last 20 trials is not kept.
- The pretraining is over when correct response is >=80% within two consecutive sets of 10 trials. Then the probe phase starts.
- The probe phase is over when 120 probe trials have been run. Every 10 trial in the probe phase is a probe trial.
