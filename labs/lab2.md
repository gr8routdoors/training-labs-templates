
## Lab 2.1 - Bazel Hello World


### Part 1: Create a BUILD file for hello world java application 


#### 1: Create a build file

Create a BUILD file under `//src/main/java/com/flarebuild/hello`, load `rules_java` and import `java_binary()`. Name the target “hello”. Set  <code>srcs</code> and <code>main_class</code> attributes of <code>java_binary().</code>

Refer to the [documentation](https://docs.bazel.build/versions/master/be/java.html#java_binary) if needed. 

Build with<code> bazel build //src/main/java/com/flarebuild/hello:hello</code>

<details>
  <summary>Hint</summary> Build file should look like this:


```bazel
load("@rules_java//java:defs.bzl", "java_binary")

java_binary(
    name = "hello",
    srcs = ["Hello.java"],
    main_class = "com.flarebuild.hello.Hello",
)
```
</details>

### Part 2: Create a BUILD file for hello world python application


#### 1: Create a build file 

Create a `BUILD` file under `src/main/python/hello`, load `rules_python` from `py_binary()`. Name the target “hello”. Set `srcs` attribute.

Build with<code> bazel build //src/main/python/hello:hello</code>

<details>
  <summary>Hint</summary> your `BUILD` file should look like this:


```bazel
load("@rules_python//python:defs.bzl", "py_binary")

py_binary(
    name = "hello",
    srcs = ["hello.py"],
)
```
</details>

## Lab 2.2 - PySpark

This lab looks at a usage of PySpark similar to that utilized by Riot when creating packages for submission to dataproc. 


#### 1: Creating BUILD files

Create a `BUILD` file under each of:

*   <code>//src/main/python/etls</code> 
*   <code>//src/main/python/etls/lor</code>
*   <code>//src/main/python/etls/utils</code>


#### 2: Building utils python library

Load rules_python to <code>//src/main/python/etls/utils/BUILD</code> and import py_library. Define package visibility as public. Set the name attribute of<code> py_library</code> to “utils”. Define srcs:<code> __init__.py </code>and <code>utils.py</code>.

Build with<code> bazel build //src/main/python/etls/utils:utils</code>  

<details>
  <summary>Hint</summary> BUILD file in<code> //src/main/python/etls/utils</code> should look like this:


```bazel
load("@rules_python//python:defs.bzl", "py_library")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "utils",
    srcs = [
        "__init__.py",
        "utils.py",
    ],
)
```

</details>

#### 2: Build lor

Load rules_python to<code> //src/main/python/etls/lor/BUILD.bazel</code> and import py_binary. Set the name attribute of<code> py_binary</code> to <code>"simple_bigquery</code>”. Add srcs, set visibility of the target to be public, add  utils to deps. 

Build with: <code>bazel build //src/main/python/etls/lor:simple_bigquery</code>

Navigate to<code> bazel-bin/src/main/python/etls/lor/simple_bigquery</code> and check whether simple_bigquery contains utils

<details>
  <summary>Hint</summary> BUILD file in<code> //src/main/python/etls/lor</code> should look like this:


```bazel
load("@rules_python//python:defs.bzl", "py_binary")

py_binary(
    name = "simple_bigquery",
    srcs = ["simple_bigquery.py"],
    visibility = ["//visibility:public"],
    deps = [
        "//src/main/python/etls/utils",
    ],
)
```

</details>

#### 3: Zip everything up

Create<code> py_zip.bzl</code> under<code> //src/main/python/etls</code>. And add the following Starlark genrule code:


```python
def py_zip(name, srcs, out_override = None):
    out = "%s.zip" % (out_override if out_override else name)
    native.genrule(
        name = name,
        srcs = srcs,
        tools = ["@bazel_tools//tools/zip:zipper"],
        outs = [out],
        cmd = "$(location @bazel_tools//tools/zip:zipper) c $@ $(SRCS)",
    )
```


Load this function In BUILD file under //src/main/python/etls:

```bazel
load(":py_zip.bzl", "py_zip")
```


Create a<code> py_zip</code> target with<code> name</code> attribute “simple_bigquery_zip” and sources <code>//src/main/python/etls/lor:simple_bigquery</code> and<code> //src/main/python/etls/utils</code>. This utility will be used to create a zip file which retains the correct folder structure for import paths. 

Build with: <code>bazel build //src/main/python/etls:simple_bigquery.zip</code>

Check the content of bazel-bin/src/main/python/etls/simple_bigquery_zip.zip

<details>
  <summary>Hint</summary> BUILD file in<code> //src/main/python/etls</code> should look like this:


```bazel
load(":py_zip.bzl", "py_zip")

py_zip(
    name = "simple_bigquery_zip",
    srcs = [
        "//src/main/python/etls/lor:simple_bigquery",
        "//src/main/python/etls/utils",
    ],
)
```
</details>
