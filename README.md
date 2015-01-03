# automark

**Automatic code marking**

These scripts will work through a folder of folders containing zipped Java projects and test them using various metrics. The current checks are the following:

1. Code compilation.
1. Code execution.
1. Data output validation (based on random inputs).
1. Indentation correctness.
1. Variable name quality.
1. Code comment quality.

## Usage

The minimum requirements to run the `batchmark.py` script are a task number a path to the folder containing the folders of students' work. The script will then assume default values for everything else.

```
python batchmark.py <task number> <path to students' work>
```

For example:

```
python batchmark.py 1 ./DLJ
```

There are other parameters for controlling where to find inputs and store outputs. Full usage details can be obtained using `python batchmark.py -h` at the command line to get the following.

```
usage: batchmark.py [-h] [-i INITIALS] [-b BUILD] [-t TEMPLATE] [-d DETAILS]
                    [-s SUMMARY]
                    TASK WORK

Batch marker for 4001COMP Java programming.

positional arguments:
  TASK                  Task number (e.g. 1)
  WORK                  Folder containing students' folders (e.g. ./DLJ)

optional arguments:
  -h, --help            show this help message and exit
  -i INITIALS, --initials INITIALS
                        Marker's initials (default Master)
  -b BUILD, --builddir BUILD
                        Folder to output build files to (default ./build)
  -t TEMPLATE, --template TEMPLATE
                        Word feedback sheeet template (default
                        ./feedback_username.docx)
  -d DETAILS, --details DETAILS
                        Excel student details list (default ./4001COMP Marking
                        2014-15.xlsx)
  -s SUMMARY, --summary SUMMARY
                        Summary of marks as a CSV file (default ./summary.csv)

```
