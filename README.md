# AutoVMAF Excel Accelerator

Generate an Excel-file, using results from AutoVMAF-API. Complete with graphs and auto-suggested ladders.

## How?

1. Populate `jobnames.txt` with your job names.

2. Edit the provided shell script `get-results.sh` to reflect your `HOST` and `PORT` settings.

3. Run the shell script to download results for all defined jobs.

```
bash get-results.sh
```

4. Install the required python packages. You might want to use a [virtual environment] (https://docs.python.org/3/tutorial/venv.html) for this.

```
pip install -r requirements.txt
```

5. Run the python script

```
python autovmaf_generate_excel.py
```
