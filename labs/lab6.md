# Lab 6 - Extending Bazel

In this lab, we'll create Bazel-native python code generation tooling. For the sake of simplicity, we'll define a list of strings and for each string, generate the following:
- a py_library with name=the string
- a python function named after the string, which returns the string as a value

#### Part 1: code-gen binary

Create file `src/main/python/codegen/main.py`.

It will accept two arguments: string and output path and will write our simple function to output path:

```python
import sys
f = open(sys.argv[2], "w")
f.write("def {str}():\n    return \"{str}\"".format(str = sys.argv[1]))
f.close()
```

Create `src/main/python/codegen/BUILD.bazel`:

```
py_binary(
    name = "main",
    srcs = ["main.py"],
    visibility = ["//visibility:public"],
)
```

Invoke it, passing some test values:

```
bazel run //src/main/python/codegen:main -- test /tmp/test.py
cat /tmp/test.py
def test():
    test
```

#### Part 2: Build Rule

Now we'll define a custom build rule which wraps this binary and can be instantiated in Bazel.

Create `rules/codegen.bzl`.

```
def _codegen_impl(ctx):
    file = ctx.actions.declare_file("%s.py" % ctx.attr.key)
    ctx.actions.run(
        outputs = [file],
        executable = ctx.executable._gen_bin,
        arguments = [ctx.attr.key, file.path],
    )
    return DefaultInfo(files = depset([file]))

codegen = rule(
    implementation = _codegen_impl,
    attrs = {
        "key": attr.string(
            mandatory = True,
        ),
        "_gen_bin": attr.label(
            default = Label("//src/main/python/codegen:main"),
            executable = True,
            cfg = "host",
        ),
    },
)
```

This defines the `codegen` build rule. It has two attributes:

- `key` - the input string
- `_gen_bin` - reference to `//src/main/python/codegen:main` target. Since this is a target attribute, the `attr.label` type should be used. 

`gen_bin` is marked as `executable = True,`, so we can access it as `ctx.executable._gen_bin` in rule in the implementation. For executables the `cfg` parameter is required, setting it to `host` guard against accidentally building host tools in the target configuration.

`_codegen_impl` is the rule implementation. It accept 1 argument - `ctx`, Bazel's custom rule execution context, containing all inputs and available to run actions.

`file = ctx.actions.declare_file("%s.py" % ctx.attr.key)` - in this line we declare the output file which our codegen tool will produce.

- By calling `ctx.actions.run` we do actual codegen tool invocation. 
- The `outputs` argument is our declared output file 
- In `executable` we place reference to our codegen binary
- And in `arguments` we pass input args for codegen binary, string key and declared file path.

This rule returns a `DefaultInfo` - an included Provider. Bazel custom rules use providers to exchange different information between each other, which be any structured data and/or generated output files.  `DefaultInfo` is the widely used and very useful to list output artifacts. 

We pass our declared file into `DefaultInfo` using `depset`, a specialized data structure that supports efficient merge operations and has a defined traversal order.

Now, create empty `rules/BUILD.bazel`, defining package `rules` so that we can `load("//rules:codegen.bzl")` from other BUILD files.

Let's try to use this custom rule. Create `tmp/BUILD.bazel`:

```
load("//rules:codegen.bzl", "codegen")

codegen(
    name = "testgen",
    key = "test",
)
```

Try to run it:

```
bazel build //tmp:testgen
INFO: Analyzed target //tmp:testgen (1 packages loaded, 1 target configured).
INFO: Found 1 target...
Target //tmp:testgen up-to-date:
bazel-bin/tmp/test.py
```

In `bazel-bin/tmp/test.py` you will see our generated function.

So, we should use it, create `tmp/testbin.py`:

```
from tmp.test import test

if __name__ == '__main__':
    print("*** %s ***" % test())
```


Now add this to `tmp/BUILD.bazel`:

```
py_library(
    name = "test",
    srcs = [":testgen"],
)

py_binary(
    name = "testbin",
    srcs = ["testbin.py"],
    deps = [":test"],
)
```

As we passed generated file with `DefaultInfo` provider to rule output, we can now use it as input for `src` attribute of `py_library`.

```
bazel run //tmp:testbin
INFO: Analyzed target //tmp:testbin (0 packages loaded, 0 targets configured).
INFO: Found 1 target...
Target //tmp:testbin up-to-date:
  bazel-bin/tmp/testbin
INFO: Elapsed time: 0.087s, Critical Path: 0.00s
INFO: 0 processes.
INFO: Build completed successfully, 1 total action
INFO: Build completed successfully, 1 total action
*** test ***
```

This verifies the `test()` function from was generated as expected and returned `"test"` string.

#### Part 3: BUILD files generation with repository_rule

We now have source file generation, but we still need to write BUILD files manually. If you recall, our initial goal was to generate code from a static input list of strings. This means we need to generate build files. 

It's not possible to generate BUILD files with custom build rules as they are executed at `analysis` phase; we need to do this in the `loading` phase. Luckily, this is possible with repository rules.

Create `rules/repo_codegen.bzl`:

```
BUILD_FILE_CHUNK = """

codegen(
    name = "{key}gen",
    key = "{key}",
)

py_library(
    name = "{key}",
    srcs = [":{key}gen"],
    visibility = ["//visibility:public"],
)

"""

def _repo_codegen_impl(repository_ctx):
    content = """load("@//rules:codegen.bzl", "codegen")"""
    for key in repository_ctx.attr.keys:
        content += BUILD_FILE_CHUNK.format(key = key)

    repository_ctx.file(
        "BUILD.bazel",
        content,
    )

repo_codegen = repository_rule(
    implementation = _repo_codegen_impl,
    attrs = {
        "keys": attr.string_list(
            mandatory = True,
        ),
    },
)
```

As you can see `repository_rule` is very similar to an ordinary custom build rule:
- It has implementation and declaration with input attributes
- The implementation  function also has a context argument. The difference is that it is loading phase context with different set of available methods, and implementation functions do not return anything.

In this rule, we are writing a `BUILD.bazel` file with generated content for each member of the input list.

`BUILD_FILE_CHUNK` is has similar declarations we wrote in `tmp/BUILD.bazel`.

The main difference is `load()` function. All `repository_rule`s live outside the main project workspace, so we can't just do `load("//rules:codegen.bzl")`, but, by prepending `@`, we can access the main workspace; so `load("@//rules:codegen.bzl")` is what we're after.

To use our `repository_rule`, add this to `WORKSPACE`:

```
load("//rules:repo_codegen.bzl", "repo_codegen")

repo_codegen(
    name = "repo_gen",
    keys = [
        "foo",
        "bar",
        "baz",
    ],
)
```

By setting `name` for our `repository_rule`, we define it's workspace alias.

We can query targets in it with:

```
bazel query @repo_gen//...
@repo_gen//:foo
@repo_gen//:foogen
@repo_gen//:baz
@repo_gen//:bazgen
@repo_gen//:bar
@repo_gen//:bargen
```

Now we'll update our `py_binary` in `tmp/BUILD.bazel` with:

```
py_binary(
    name = "testbin",
    srcs = ["testbin.py"],
    deps = [
        ":test",
        "@repo_gen//:foo",
        "@repo_gen//:bar",
        "@repo_gen//:baz",
    ],
)
```

And update `tmp/testbin.py` to:
```
from tmp.test import test
from repo_gen.foo import foo
from repo_gen.bar import bar
from repo_gen.baz import baz

print("*** %s ***" % test())
print("*** %s ***" % foo())
print("*** %s ***" % bar())
print("*** %s ***" % baz())
```

Invoke it again:

```
bazel run //tmp:testbin
INFO: Analyzed target //tmp:testbin (0 packages loaded, 0 targets configured).
INFO: Found 1 target...
Target //tmp:testbin up-to-date:
bazel-bin/tmp/testbin
INFO: Elapsed time: 0.096s, Critical Path: 0.00s
INFO: 0 processes.
INFO: Build completed successfully, 1 total action
INFO: Build completed successfully, 1 total action
*** test ***
*** foo ***
*** bar ***
*** baz ***
```

As you can see in the output, libraries, and functions were created and successfully invoked for every item in the list we provided to the instantiation of the codegen rule in the WORKSPACE.
