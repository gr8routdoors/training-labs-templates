# Lab 5 — Genrules and Macros

## Functionality — Problem Statement

### In a not-so-far-fetched future....

Let's imagine, for a moment, that we are a team of Data Scientists Extraordinaire at a corporation **C.S.Veil Inc.**, and our business model is all about cleaning polluted CSV files from dirty data.

After our CTO had heard of Bazel, she became convinced that C.S.Veil Inc _must_ release an open source a rule that uses our proprietary CSV parser to clean the data.

> You see, C.S.Veil Inc's sinister plan is to take over the world, of course. The plan is — once the proprietary parser is adopted by the majority of Fortune 500 Companies, C.S.Veil Inc. would sneak in an urgent security patch that would, once and for all, elimitate all tab-delimited files by auto-converting any TAB-delimited file found into a CSV file, forcing a New World Order, whereas The Commas (not to be confused with the "Commies") Rule the World, one tab at a time.
>
> **NOTE: Please note — no tabs were harmed in the making of this lab.**

Our first quest is to _create a custom Bazel Rule that transform CSV files, and to provide a user-friendly macro as an interface_. We want to make the task of cleaning CSV files as easy as possible for everyone out there, who may still be debating the merits of tabs over commas. Pointlessly unthinkable.

Once we create our rule — we should make sure to provide some automated tests with it, so that other developers who contribute to our rules in the future can be certain they didn't break any legacy CSVs.

## Part 1 – `genrule`

First, let’s clean-up CSV data by removing blank lines and duplicate lines.

This could be done with a `bash`  one-liner, like this one:

```bash
cat source.csv | awk '!a[$0]++' | awk 'NF' > resulting.csv
```

> Details on how the above one-liner works using AWK are outside the scope of this excercize. Please see the [GNU Awk Guide](https://www.gnu.org/software/gawk/manual/gawk.html) for more details.

Let’s wrap it in a `genrule`.

1. Create a BUILD file under `//src/main/python/json_conversion`.

2. Here we will create a `filegroup` which will serve as a source target. It could be an output from another action, but for simplicity we will use an existing file: `src/main/python/json_conversion/test/data.csv`.

```bazel
filegroup(
    name = "csv_data",
    srcs = ["test/data.csv"],
)    
```

3. Next, lets define a new `genrule`, and name it `csv_sanitized`. We will use `:csv_data` label as it’s `srcs` attribute.

4. Please provide an output filename in the `outs` attribute (for example, `uniq_data.csv`).


NOTE: Don’t forget to escape `$` symbols: `awk '!a[$0]++'` → `awk '!a[$$0]++'`

Refer to the [documentation](https://docs.bazel.build/versions/master/be/general.html#genrule) if needed.

Build with the following command, and verify the result:

```bash
bazel build //src/main/python/json_conversion:csv_sanitized
cat bazel-bin/src/main/python/json_conversion/uniq_data.csv
```

<details>
  <summary>Hint</summary> Build file should look like this:
  
```bazel
filegroup(
    name = "csv_data",
    srcs = ["test/data.csv"],
)

genrule(
    name = "csv_sanitized",
    srcs = [":csv_data"],
    outs = ["uniq_data.csv"],
    cmd = "cat $< | awk '!a[$$0]++' | awk 'NF' > $@",
)

```

</details>

## Part 2 – `sh_test`

Next, we will add a test to compare action output with the expected "reference" data.

Conveniently, we have an existing file with a reference data already committed to the repo here: `src/main/python/json_conversion/test/expected.csv`

And a bash script `src/main/python/json_conversion/test/compare.sh` (which invokes `cmp` — UNIX compare utility).

In this lab, please write a `sh_test` rule, and name it `remove_duplicates_test`. Please use the provided `BASH` script as it’s `srcs`.

To pass arguments to the script, use the previously created target output and wrap it in `$location` helper: `$(location :csv_sanitized)`.

Second argument is our reference file: `$(location test/expected.csv)`.

References:
  * [`sh_test` Rule Documentation](https://docs.bazel.build/versions/master/be/shell.html#sh_test)
  * [Make Variables Manual](https://docs.bazel.build/versions/master/be/make-variables.html)

Once finished, go ahead and run the test with:

```bash
bazel test //src/main/python/json_conversion:remove_duplicates_test
```

and make sure it shows as `PASSED`.

<details>
  <summary>Hint</summary> Test target should look like this:

```bazel
sh_test(
    name = "remove_duplicates_test",
    size = "small",
    srcs = ["test/compare.sh"],
    args = [
        "$(location :csv_sanitized)",
        "$(location test/expected.csv)",
    ],
    data = [
        "test/expected.csv",
        ":csv_sanitized",
    ],
)
```

</details>

## Part 3 – Macros

Writing long lists of arguments for target definitions could be time-consuming. `sh_test` already looks heavy in our `BUILD` file. Imagine if we will need 10 of them?

Thankfully we have a solution: macro. Treat it like "wrapper" for rules definitions, for which Bazel will replace each macro call to related macro contents on the loading phase.

1. Create `defs.bzl` file under `//src/main/python/json_conversion`.

2. Define two macros: `remove_duplicates(name, src, out = "")` and `compare_files_test(name, actual, expected)` and wrap our genrule and sh_test in them.

> Tip: you could substitute genrule output filename from macro name argument.

Refer to the [documentation](https://docs.bazel.build/versions/master/skylark/macros.html) if needed.

3. In the `BUILD` file load your macros: `load(":defs.bzl", "compare_files_test", "remove_duplicates")`

4. And replace `genrule` and `sh_test` with macro usage: 

```bazel
remove_duplicates(
    name = "csv_sanitized_with_macro",
    src = ":csv_data",
)

compare_files_test(
    name = "remove_duplicates_macro_test",
    actual = ":csv_sanitized_with_macro",
    expected = "test/expected.csv",
)
```

5. Build and test:

```bash
bazel build //src/main/python/json_conversion:csv_sanitized_with_macro
bazel test //src/main/python/json_conversion:remove_duplicates_macro_test
```

<details>
  <summary>Hint</summary> Macros definitions should look like this:
  
```bazel
def remove_duplicates(name, src, out = "", **kwargs):
    """
    Remove duplicate lines and blank lines from the provided file.
    """
    if out == "":
        out = name + ".csv"
    native.genrule(
        name = name,
        srcs = [src],
        outs = [out],
        cmd = "cat $< | awk '!a[$$0]++' | awk 'NF' > $@",
        **kwargs
    )

def compare_files_test(name, actual, expected):
    """
    Compare contents and fail is differ.
    """
    native.sh_test(
        name = name,
        size = "small",
        srcs = ["test/compare.sh"],
        args = [
            "$(location %s)" % actual,
            "$(location %s)" % expected,
        ],
        data = [
            actual,
            expected,
        ],
    )

```
</details>

## Part 4 – `genrule` with `py_binary` target

Lets assume we would like to transform data, but bash scripts are no longer sufficient for our particular task.

For instance, perhaps we'd like to convert CSV to JSON (and vice versa) with an existing Python script: `src/main/python/json_conversion/main.py` (which just uses `pandas`,`read_json` and `read_csv`).

The script accepts two arguments: an input and output files. Depending on the extension of the input file it will transform csv input to json output or vice versa.

1. Please define a `py_binary` in the `BUILD` file, and name it `csv_converter`.

2. Next, load the `requirement()` function from the `@pip` package and set `requirement("pandas")` under the deps of your `py_binary`:

```bazel
load("@pip//:requirements.bzl", "requirement")
```

Refer to the [documentation](https://docs.bazel.build/versions/master/be/python.html#py_binary) if needed.

3. Create new `genrule`, name it `convert_csv` and use `:csv_converter` label as it’s tools argument.

 * Don’t forget to use $location helper in the cmd: `$(location :csv_converter)`.

4. As an input, use output from your macro label: `:csv_sanitized_with_macro`

5. Build with: `bazel build //src/main/python/json_conversion:convert_csv`

<details>
  <summary>Hint</summary> py_binary and new genrule should look like this:
  
```bazel
## Python converter
py_binary(
    name = "csv_converter",
    srcs = ["main.py"],
    main = "main.py",
    deps = [
        requirement("pandas"),
    ],
)

# Get sanitized CSV and convert it to JSON
genrule(
    name = "convert_csv",
    srcs = [":csv_sanitized_with_macro"],
    outs = ["converted-data.json"],
    cmd = "$(location :csv_converter) $< $@",
    tools = [":csv_converter"],
)
```

</details> 

You may have noticed `test/expected.json` file before. That’s right, it is a reference data to use in test.

Create test based on your macro `compare_files_test`.
 
Provide `:convert_csv` output as it’s `actual` argument and `test/expected.json` file as `expected` argument.

```bazel
compare_files_test(
    name = "csvjson_convertion_test",
    actual = ":convert_csv",
    expected = "test/expected.json",
)
```

Run it with Bazel (`bazel test //src/main/python/json_conversion:csvjson_convertion_test`).

Now wrap newly-created genrule with macro. Add `convert_csv_or_json` to `defs.bzl`, which will use two rules now: `native.py_binary` and `native.genrule`.

Don’t forget to add load statement at the top of `defs.bzl`: `load("@pip//:requirements.bzl", "requirement")`

Derive name for `py_binary` from macro name argument with some suffix to avoid label name conflicts.

<details>
  <summary>Hint</summary> new macro could look like this:
  
```bazel
def convert_csv_or_json(name, input, output):
    """Convert CSV to JSON and vice versa (depending on the input)
    """

    native.py_binary(
        name = name + "_converter",
        srcs = ["main.py"],
        main = "main.py",
        deps = [
            requirement("pandas"),
        ],
    )

    native.genrule(
        name = name,
        srcs = [input],
        outs = [output],
        cmd = "$(location :" + name + "_converter) $< $@",
        tools = [":" + name + "_converter"],
    )
```

</details>

Replace `:convert_csv` label in your `BUILD` file with newly-created macro. 

For the extra fun, use that macro again to convert resulting json from `:convert_csv` back to csv.
And create additional `compare_files_test` to check it’s output against original `test/expected.csv` file.

Be extra careful with labels (remember script chooses conversion direction based on input file extension)

```bazel
# Get sanitized CSV and convert it to JSON
convert_csv_or_json(
    name = "convert_csv",
    input = ":csv_sanitized_with_macro",
    output = "converted-data.json",
)

# Compare resulting JSON with reference
compare_files_test(
    name = "csvjson_convertion_test",
    actual = ":convert_csv",
    expected = "test/expected.json",
)

# Convert that JSON back to CSV
convert_csv_or_json(
    name = "convert_json",
    input = ":convert_csv",
    output = "converted-data-back.csv",
)

# Compare resulting CSV with reference
compare_files_test(
    name = "jsoncsv_convertion_test",
    actual = ":convert_json",
    expected = "test/expected.csv",
)
```

Run all tests and make sure they passed:

```bash
bazel test //src/main/python/json_conversion:all --test_output=errors
```
