# Lab 3 - Advanced Python & Java


## Lab 3.1 -  Java & 3rd-party Dependencies

<code>Rules_jvm_external</code> is already configured in this workspace; however, various applications and tests in the project will need their 3rd-party dependencies added to the Maven configuration so that <code>rules_jvm_external</code> can download them. This lab will acquaint you with that workflow in addition to the creation of BUILD files defining binary and test targets.


### Part 1: Add a Maven dependency


#### 1: Add a Maven dependency on commons-math3

Given the following Maven dependency definition, add <code>commons-math3</code> to the project.


```xml
<dependency>
   <groupId>org.apache.commons</groupId>
   <artifactId>commons-math3</artifactId>
   <version>3.1</version>
</dependency>
```

<details>
  <summary>Hint</summary> Add  <code>"org.apache.commons:commons-math3:3.1" </code>to the artifacts list of <code>maven_install</code> in the <code>WORKSPACE</code>: 


```bazel
maven_install(
   name = "maven",
   artifacts = [
       "org.apache.commons:commons-math3:3.1",
   ],
   maven_install_json = "//:maven_install.json",
   repositories = [
       "https://jcenter.bintray.com/",
       "https://maven.google.com",
       "https://repo1.maven.org/maven2",
   ],
)
```
</details>

Dependencies downloaded by <code>rules_jvm_external</code> can be accessed by at <code>@maven//:{coordinate}</code>, replacing all periods and colons with underscores and omitting the version. So commons-math3 is available at <code>@maven//:org_apache_commons_commons_math3</code>


#### 2: Pin the dependency



1. Run <code>bazel run @unpinned_maven//:pin</code>
2. Run <code>cat maven_install.json</code> and insure the entry has been added


#### 3: Bump the dependency version up

Increase the version of commons-math to 3.2.

<details>
  <summary>Hint</summary> Change  <code>"org.apache.commons:commons-math3:3.1" </code>to <code>"org.apache.commons:commons-math3:3.2" in </code>the artifacts list of <code>maven_install</code> in the <code>WORKSPACE</code>: 


```bazel
maven_install(
   name = "maven",
   artifacts = [
       "org.apache.commons:commons-math3:3.2",
   ],
   maven_install_json = "//:maven_install.json",
   repositories = [
       "https://jcenter.bintray.com/",
       "https://maven.google.com",
       "https://repo1.maven.org/maven2",
   ],
)
```
</details>


#### Part 2: Create BUILD file for ComplexGenerator

There is a Java library at <code>src/main/java/com/flarebuild/complex/generator/ComplexGenerator.java</code>. Create a BUILD file for it such that it can be built with:


```bash
bazel build //src/main/java/com/flarebuild/complex/generator:ComplexGenerator
```

Note that this library depends on <code>commons-math3. </code>

<details>
  <summary>Hint</summary> create file <code>src/main/java/com/flarebuild/complex/generator/BUILD</code> with contents:


```bazel
load("@rules_java//java:defs.bzl", "java_library")

package(default_visibility = ["//visibility:public"])

java_library(
    name = "ComplexGenerator",
    srcs = ["ComplexGenerator.java"],
    deps = [
        "@maven//:org_apache_commons_commons_math3",
    ],
)
```
</details>


## Lab 3.2 - Java Tests & Dependencies


### Part 1: Add a Maven dependency


#### 1: Add a Maven dependency on JUnit

Given the following Maven dependency definition, add <code>junit</code> to the project. Note that the test scope maps to testonly=True in the Bazel world, and that to use this property, we’ll want to use the [maven.artifact](https://github.com/bazelbuild/rules_jvm_external/blob/master/docs/api.md#mavenartifact) variant of artifact definition.


```xml
<dependency>
   <groupId>junit</groupId>
   <artifactId>junit</artifactId>
   <version>4.8.1</version>
   <scope>test</scope>
</dependency>
```


<details>
  <summary>Hint</summary> Update <code>maven_install</code> in the <code>WORKSPACE</code> to the following:


```bazel
maven_install(
   name = "maven",
   artifacts = [
       maven.artifact(
           "junit",
           "junit",
           "4.8.1",
           testonly = True,
       ),
       "org.apache.commons:commons-math3:3.2",
   ],
   maven_install_json = "//:maven_install.json",
   repositories = [
       "https://jcenter.bintray.com/",
       "https://maven.google.com",
       "https://repo1.maven.org/maven2",
   ],
)
```
</details>


#### 2: Pin the new dependency

Run <code>bazel run @unpinned_maven//:pin</code>


#### Part 2: Create a BUILD file for the ComplexGenerator tests 

There is a Java test at <code>src/test/java/com/flarebuild/complex/ComplexGeneratorTest.java</code>. Create a BUILD file for it such that it can be run with: 


```bash
bazel test //src/test/java/com/flarebuild/complex:ComplexGeneratorTest
```


<details>
  <summary>Hint</summary> Create file <code>src/test/java/com/flarebuild/complex/BUILD </code>with contents:


```bazel
load("@rules_java//java:defs.bzl", "java_library", "java_test")

java_test(
   name = "ComplexGeneratorTest",
   size = "small",
   srcs = ["ComplexGeneratorTest.java"],
   test_class = "com.flarebuild.complex.ComplexGeneratorTest",
   deps = [
       "//src/main/java/com/flarebuild/complex/generator:ComplexGenerator",
       "@maven//:junit_junit",
   ],
)
```
</details>

Invoke with  <code>bazel test //src/test/java/com/flarebuild/complex:ComplexGeneratorTest</code>



## Lab 3.3 - Python 3rd-party Dependencies

[rules_python_external](https://github.com/dillon-giacoppo/rules_python_external/blob/master/example/BUILD#L31) is configured for the workspace, and in this lab you’ll learn how to interact with 3rd-party Python dependencies in addition to creating BUILD files for python applications and tests. There is an image classification program in this repository at <code>src/main/python/classifier/main.py</code>; we are going to build, run and test it.


### Part 1: Add Pip dependencies


#### Add a Pip dependency on tensorflow, matplotlib, Pillow, and numpy

<details>
  <summary>Hint</summary> in requirements.txt add the following: 


```pip
    numpy==1.19.1
    tensorflow==2.3.0
    matplotlib==3.1.2
    Pillow==7.2.0
```

</details>

### Part 2: Create a BUILD file for the classifier

There is a Python program at <code>src/main/python/classifier/main.py</code>. Create a BUILD file for it such that it can be built with: 


```bash
bazel build //src/main/python/classifier:main
```


<details>
  <summary>Hint</summary> Create file <code>src/main/python/classifier/BUILD </code>with contents:


```bazel
load("@pip//:requirements.bzl", "requirement")
py_binary(
    name = "main",
    srcs = ["main.py"],
    data = glob(["model/"]),
    deps = [
        requirement("tensorflow"),
        requirement("matplotlib"),
    ],
)
```
</details>

Run with  <code>bazel run //src/main/python/classifier:main -- --test_image=0</code>


### Part 3: Create a BUILD file for prediction tests

There is a Python test at <code>src/test/python/classifier/prediction_test.py</code>. Write a BUILD file for it such that it can be invoked with <code>bazel test //src/test/python/classifier:prediction_test</code>. Be sure to add the images to the data attribute of the test rule!

<details>
  <summary>Hint</summary> Create file <code>src/test/python/classifier/BUILD </code>with contents:


```bazel
load("@pip//:requirements.bzl", "requirement")

py_test(
    name = "prediction_test",
    size = "small",
    srcs = ["prediction_test.py"],
    data = [":images"],
    deps = [
        requirement("Pillow"),
        requirement("numpy"),
        "//src/main/python/classifier:main",
    ],
)

filegroup(
    name = "images",
    srcs = [
        "images/pullover.png",
        "images/trousers.png",
    ],
)
```
</details>


## Lab 3.4 - Protobuf with Java & Python

There is a protobuf file in this repository at <code>src/main/proto/message_object.proto</code> which will be used by Java and Python programs at <code>src/main/java/com/flarebuild/message/Main.java</code> and <code>src/main/python/message/message.py</code> respectively. In this exercise, we’ll create BUILD files for the proto library which will be consumed by both Java and Python applications.


### Part 1: Build the .proto files


#### 1: Create a BUILD file for message_object 

Create a BUILD file under <code>//src/main/proto </code>and make the packages it defines publicly accessible. Define a proto_library, and then a java_proto_library and python_proto_library targets which use it as a dep.

<details>
  <summary>Hint</summary> create file src/main/proto/BUILD: 


```bazel
load("@rules_java//java:defs.bzl", "java_proto_library")
load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_proto_grpc//python:defs.bzl", "python_proto_library")

package(default_visibility = ["//visibility:public"])

proto_library(
   name = "message_object_proto",
   srcs = [":message_object.proto"],
)

java_proto_library(
   name = "message_object_proto_java",
   deps = [":message_object_proto"],
)

python_proto_library(
   name = "message_object_proto_python",
   deps = [":message_object_proto"],
)
```

</details>

#### 2: Build the proto library targets

* <code>bazel build //src/main/proto:message_object_proto</code>
* <code>bazel build //src/main/proto:message_object_proto_java</code>
* <code>bazel build //src/main/proto:message_object_proto_python</code>


### Part 2: Create a BUILD file for the Java binary 

Create a java binary target using java proto library as dependency

Create a BUILD file such that the java program can be built with <code>bazel build //src/main/java/com/flarebuild/message:main </code>and be sure to include <code>//src/main/proto:message_object_proto_java</code> as a dependency.

<details>
  <summary>Hint</summary> Create file <code>src/main/java/com/flarebuild/message/BUILD </code>with contents: 


```bazel
load("@rules_java//java:defs.bzl", "java_binary")

java_binary(
    name = "main",
    srcs = ["Main.java"],
    main_class = "com.flarebuild.message.Main",
    deps = [
        "//src/main/proto:message_object_proto_java",
    ],
)
```
</details>


### Part 3: Create a BUILD file for the Python binary 

Create a BUILD file such that the python program can be built with <code>bazel build //src/main/python/message:message </code>and be sure to include <code>//src/main/proto:message_object_proto_python</code> as a dependency.

<details>
  <summary>Hint</summary> the file <code>//src/main/python/message/BUILD </code>should contain:


```bazel
load("@rules_python//python:defs.bzl", "py_binary")

py_binary(
    name = "message",
    srcs = ["message.py"],
    deps = [
        "//src/main/proto:message_object_proto_python",
    ],
)
```
</details>

### Part 4: Tighten up visibility


1. Remove <code>package(default_visibility = ["//visibility:public"]) </code>from src/main/proto/BUILD.

2. Make targets message_object_proto_java and message_object_proto_python  visible exclusively  to  <code>//src/main/java/com/flarebuild/message </code>and to<code> //src/main/python/proto </code>respectively.

<details>
  <summary>Hint</summary> Targets now should look like this:


```bazel
java_proto_library(
    name = "message_object_proto_java",
    visibility = ["//src/main/java/com/flarebuild/message:__pkg__"],
    deps = [":message_object_proto"],
)

python_proto_library(
    name = "message_object_proto_python",
    visibility = ["//src/main/python/message:__pkg__"],
    deps = [":message_object_proto"],
)
```
</details>

Invoke:

*   <code>bazel build //src/main/java/com/flarebuild/message:main</code>
*   <code>bazel build //src/main/python/message:message</code>
