> **_NOTE:_**  This version (1.0.1) is a patch to version 1.0. Version 1.0 is referenced in 
>
> Lind, J., Vinken, V., Jonsson, M., Ghirlanda, S., & Enquist, M. (2023). A test of memory for stimulus sequences in great apes. _Plos one, 18_(9), e0290546.
>
> available at https://doi.org/10.1371/journal.pone.0290546.
>
> This patch version includes the matching-to-sample experiments in that manuscript, in `bonobo_mts.py`. Also, for consistency, the files `kanzi.py` and `teco.py` have been renamed to `bonobo_trace_kanzi.py` and `bonobo_trace_teco.py`, respectively.

# Setup & Installation

Make sure you have Python version 3.6 or newer installed.

```bash
git clone --depth 1 --branch v1.0.1 git@github.com:markusrobertjonsson/bonobo.git
```

or download the zip-file from https://github.com/markusrobertjonsson/bonobo/archive/refs/tags/v1.0.1.zip and unzip.


# Starting the matching-to-sample (MTS) experiments
For the simultaneous MTS experiment:
```bash
python bonobo_mts.py MTS
```

For the zero-delay MTS experiment:
```bash
python bonobo_mts.py ZDMTS
```

For the delayed MTS experiment:
```bash
python bonobo_mts.py MTS
```

# Starting the sequence discrimination experiment
For bonobos:
```bash
python bonobo_seqdis.py
```

For human subjects:
```bash
python human.py
```

# Starting the trace model tests (with probe trials)
Note that this experiment starts with a pretraining phase consisting of a delayed matching-to-sample experiment with 0.2 s delay.

For the trace model experiment for Kanzi:
```bash
python bonobo_trace_kanzi.py
```

For the trace model experiment for Teco:
```bash
python bonobo_trace_teco.py
```

# Other information

## Function keys
- **&lt;F11>** toggles full screen
- **&lt;F10>** toggles visibility of mouse pointer. The mouse may need to be moved before the effect of the visibility change is seen.
- **&lt;Space>** pauses the experiment and a pause screen with current experiment status is displayed; another space resumes it

## Output files
The output from the below commands are written to the below output files in the subdirectory `result_files`:
- `bonobo_mts.py <exp>`: `subject_tag_<exp>_[date].csv`
- `bonobo_trace_kanzi.py`: `CEK2022_kanzi.csv`
- `bonobo_trace_teco.py`: `CEK2022_teco.csv`
- `bonobo_seqdis.py`: `bonobo_name_SeqDis_[date].csv`
- `human.py`: `subject[n]_exp[m][date and time].csv`

## Notes for the trace tests
- The pause screen contains information about how many trials are left (in pretraining part) and how many probe trials are left (in the probe phase) 
- If an experiment is aborted (by closing the window) it will be resumed from where it was aborted when restarted. However, in the pretraining, the score of the last 20 trials is not kept.
- The pretraining is over when correct response is >=80% within two consecutive sets of 10 trials. Then the probe phase starts.
- The probe phase is over when 120 probe trials have been run. Every 10 trial in the probe phase is a probe trial.
