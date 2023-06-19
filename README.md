# bonobo

## Setup & Installation

Make sure you have Python version 3.6 or newer installed.

```bash
git clone https://github.com/markusrobertjonsson/bonobo.git
```

or download zip-file from https://github.com/markusrobertjonsson/bonobo/ and unzip.

## Running the experiments in the manuscript "A test of memory for stimulus sequences in great apes"

For Kanzi:
```bash
python kanzi.py
```

For Teco:
```bash
python teco.py
```

For the sequence discrimination experiments for bonobos:
```bash
python bonobo_seqdis.py
```

For the experiments on human subjects:
```bash
python human.py
```


## Instructions

- Output from kanzi.py is written to `result_files/CEK2022_kanzi.csv`
- Output from teco.py is written to `result_files/CEK2022_teco.csv`
- Output from bonobo_seqdis.py is written to `result_files/bonobo_name_SeqDis_[date].csv`
- Output from human.py is written to `result_files/subjectn_expm[date and time].csv`
- &lt;F11> toggles full screen
- &lt;F10> toggles visibility of mouse pointer. The mouse may need to be moved before the effect of the visibility change is seen.
- &lt;Space> pauses the experiment and a pause screen with current experiment status is displayed; another space resumes it
- The pause screen contains information about how many trials are left (in pretraining part) and how many probe trials are left (in the probe phase) 
- If an experiment is aborted (by closing the window) it will be resumed from where it was aborted when restarted. However, in the pretraining, the score of the last 20 trials is not kept.
- The pretraining is over when correct response is >=80% within two consecutive sets of 10 trials. Then the probe phase starts.
- The probe phase is over when 120 probe trials have been run. Every 10 trial in the probe phase is a probe trial.
