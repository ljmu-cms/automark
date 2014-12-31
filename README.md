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

Call the `batchmark.py` script with the task number and the name of the folder containing the submissions:

```
python batchmark.py <task number> <marker initials>
```

For example:

```
python batchmark.py 1 DLJ
```
