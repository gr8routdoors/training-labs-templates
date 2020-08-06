
## Lab 2 - Bazel Hello World


### Part 1: Create a BUILD file for hello world java application 


#### 1: Create a build file

Create a BUILD file under `//src/main/java/com/flarebuild/hello`, load `rules_java` and import `java_binary()`. Name the target “hello”. Set  <code>srcs</code> and <code>main_class</code> attributes of <code>java_binary().</code>

Refer to the [documentation](https://docs.bazel.build/versions/master/be/java.html#java_binary) if needed. 

Build with<code> bazel build //src/main/java/com/flarebuild/hello:hello</code>

<details>
  <summary>Hint</summary> Build file should look like this:


```
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


```
    load("@rules_python//python:defs.bzl", "py_binary")

    py_binary(
       name = "hello",
       srcs = ["hello.py"],
    )
```
</details>
