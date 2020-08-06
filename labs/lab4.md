# Lab 4 - Bazel CLI usage

## Lab 4.1 - Queries

### Part 1: Preparations

#### 1: Let’s clone some rather solid Bazel repository to practice in query invocation

<code>git clone https://github.com/grpc/grpc-java.git && cd grpc-java</code>

#### 2: (Optional) Install graphviz package to visualize dependencies graphs

Warning: Installation can take a lot of time.

For other platforms please follow instructions on graphiz site.

<code>brew install graphviz</code>

### Part 2: Query output formats

#### 1: Let Bazel initialize workspace and query all targets there

<code>bazel query //...</code>

You will see just list of target names, like:

    $ bazel query //...
    //testing:testing
    //testing:internal
    //services:reflection
    //services:health
    //services:channelz
    //services:binarylog
    //services:_reflection_java_grpc
    ...

Bazel query supports different output formats by defining it with <code>--output</code> format flag. Try run it with some unexpected format to see possible variants, like:

    $ bazel query //... --output abc
    ERROR: Invalid output format 'abc'. Valid values are: label, label_kind, build, minrank, maxrank, package, location, graph, xml, proto, streamed_proto

Default output is <code>label</code>, it is just ordinal build rule target name.

#### 2: Output: package

    $ bazel query //... --output package
    grpclb
    netty
    netty/shaded
    okhttp
    protobuf
    protobuf-lite
    rls
    …

Here are list of different packages exist in workspace, note list is smaller than just labels list.

#### 3: Output: label_kind

    $ bazel query //... --output label_kind
    java_library rule //testing:testing
    _java_grpc_library rule //services:_reflection_java_grpc
    java_rpc_toolchain rule //compiler:java_lite_grpc_library_toolchain
    genrule rule //alts:protobuf_imports
    …

Now you can see label’s <code>kind</code>, it is type of rule by which target is defined in BUILD file. For example, <code>java_library</code> is the native Bazel’s rule, it comes with Bazel out of the box. And <code>\_java_grpc_library</code> is the custom rule, which is defined in <code>grpc_java</code> workspace.

#### 4: Output: location, build

    $ bazel query //... --output location
    //some/path/grpc-java/protobuf-lite/BUILD.bazel:22:15: config_setting rule //protobuf-lite:android
    //some/path/grpc-java/api/BUILD.bazel:1:13: java_library rule //api:api
    //some/path/grpc-java/context/BUILD.bazel:1:13: java_library rule //context:context
    //some/path/grpc-java/compiler/BUILD.bazel:5:10: cc_binary rule //compiler:grpc_java_plugin
    //some/path/grpc-java/BUILD.bazel:17:19: java_proto_library rule //:api_proto_java

Here are each target BUILD file path, position inside and label_kind

    $ bazel query //... --output build

    # //some/path/grpc-java/BUILD.bazel:17:19

    java_proto_library(
    name = "api_proto_java",
    deps = ["@com_google_protobuf//:api_proto"],
    )
    ...

Now for each target you can see the actual rule definition and BUILD file path in which it is contained.

Both queries outputs very useful for different third-party BUILD files parser tools integrations.

#### 5: Output: minrank, maxrank

    $ bazel query //... --output minrank
    $ bazel query //... --output maxrank

Like <code>label</code>, the <code>minrank</code> and <code>maxrank</code> output formats print the labels of each target in the resulting graph, but instead of appearing in topological order, they appear in rank order, preceded by their rank number.
There are two variants of this format: <code>minrank</code> ranks each node by the length of the shortest path from a root node to it, <code>maxrank</code> ranks each node by the length of the longest path from a root node to it.
These output formats are useful for discovering how deep a graph is.

#### 6: Output: xml, proto, streamed_proto

    $ bazel query //... --output xml
    $ bazel query //... --output proto
    $ bazel query //... --output streamed_proto

These output formats represent each rule serialized with its properties, inputs and outputs. Proto is the binary protobuf representation.

#### 7: (Optional) Output: graph

If you installed graphiz package, lets true to visualize query graph. First, check if dot cmd util exist:

    $ dot -V
    dot - graphviz version 2.44.1 (20200629.0846)

If all ok, let’s try this:

    $ bazel query //... --output graph | dot -Tpng > /tmp/test.png
    $ open /tmp/test.png

And here is ours target dependency graph visualization!

#### 8: Summary

It was just the most basic query, but now we have expectations about output formats of query we can use. Combining different output formats with more complex queries give very powerful weapon in our hands.

### Part 3: Dependencies query

#### 1: deps()

Let’s take //core:core target and query it’s dependencies

    $ bazel query 'deps(//core:core)'

You will see long list of labels, containing jre deps, different tools, source files and even zlib sources. Most likely we do not want to see all of it, so we can do:

    $ bazel query 'deps(//core:core)' --notool_deps --noimplicit_deps

Now we can see only direct api dependency libraries and source files.

<code>--noimplicit_deps</code> - option causes implicit dependencies not to be included in the dependency graph over which the query operates. An implicit dependency is one that is not explicitly specified in the BUILD file but added by bazel.

<code>--notool_deps</code> - option causes dependencies in non-target configurations not to be included in the dependency graph over which the query operates.

#### 2: kind

What if we want to query all <code>java_libraries</code> in workspace? We should use kind function:

    $ bazel query 'kind(java_library, //...)'

Returning to //core:core, how to query only <code>java_libraries</code> in its deps, we should combine <code>kind</code> and <code>deps</code>:

    $ bazel query 'kind(java_library, deps(//core:core))'

And what if we want to query all source files which <code>//core:core</code> depends on?

    $ bazel query 'kind("source file", deps(//core:core))'

#### 3: rdeps()

But if we want the opposite, find all targets which depends on <code>//core:core</code>? We should use reverse deps:

    $ bazel query 'rdeps(..., //core:core)'

#### 4: query intersection

What if we want to find all deps of both <code>//core:core</code> and <code>//netty:netty</code> targets?

    $ bazel query 'deps(//netty:netty) + deps(//core:core)'

And what if we want to find only <code>java_libraries</code> there?

    $ bazel query 'kind(java_library, deps(//netty:netty) + deps(//core:core))'

#### 5: Summary

Now we know how to do basic queries, for more complex examples:

https://docs.bazel.build/versions/master/query.html
https://docs.bazel.build/versions/master/query-how-to.html

### Part 4: genquery

Let’s define query as rule with output in file.

Open root <code>BUILD.bazel</code> file in <code>grpc_core</code> directory and append this:

    genquery(
    name = "test_genquery",
    expression = "deps(//core:core)",
    scope = ["//core:core"],
    opts = ["--output", "label_kind", "--notool_deps", "--noimplicit_deps"],
    )

Now, run it:

    $ bazel build :test_genquery
    INFO: Analyzed target //:test_genquery (0 packages loaded, 0 targets configured).
    INFO: Found 1 target...
    Target //:test_genquery up-to-date:
    bazel-bin/test_genquery

Inside <code>bazel-bin/test_genquery</code> file you will find text output similar to invocation:

    bazel query 'deps(//core:core)' --notool_deps --noimplicit_deps --output label_kind

## Lab 4.2 - Profiling

Let’s build <code>//core:core</code> and inspect it’s profile information.

    $ bazel build //core:core --profile=/tmp/profile.gz

Open **chrome://tracing** in a Chrome browser tab, click **Load** and pick the (potentially compressed) profile file. For more detailed results, click the boxes in the lower left corner.

You can use these keyboard controls to navigate:

- Press 1 for “select” mode. In this mode, you can select particular boxes to inspect the event details (see lower left corner). Select multiple events to get a summary and aggregated statistics.
- Press 2 for “pan” mode. Then drag the mouse to move the view. You can also use a/d to move left/right.
- Press 3 for “zoom” mode. Then drag the mouse to zoom. You can also use w/s to zoom in/out.
- Press 4 for “timing” mode where you can measure the distance between two events.
- Press ? to learn about all controls.

Also, run:

    $ bazel analyze-profile ~/profile.gz

To see some summary information from the profile.

## Lab 4.3 - Local disk cache

This lab should be done in training labs workspace.

### 1: Clean up workspace

Run <code>bazel clean</code>

### 2: Create directory for disk cache

Run <code>mkdir /tmp/bazel-disk-cache</code>

### 3: Populate disk cache

Run <code>bazel build --disk_cache /tmp/bazel-disk-cache //...</code>

Check contents of the disk cache directory.

<details>
  <summary>Hint</summary> <code>ls -lh</code> output will look like below:

```
training-labs$ ls -lh /tmp/bazel-disk-cache/
total 448M
-rw-r--r-- 1 me me  56K Aug  6 19:08 0014baf050e3e572ff6dc1e75b9d5ac5d795d3ae298ce3ee4abb3d97ed91c71f
-rw-r--r-- 1 me me 1.5K Aug  6 19:08 0043a851d451d29523714216c6f0a0ccce01347892ccf2720c03be15c2c39457
-rw-r--r-- 1 me me  142 Aug  6 19:07 00d000c2891db234fe6d08344edd61f337a5e8072157bce92c11af76ac1bc071
-rw-r--r-- 1 me me  142 Aug  6 19:08 00ec9118414add045bb26008a62e0ba717abb033e876cd4d18186f94348fd933
-rw-r--r-- 1 me me  12K Aug  6 19:08 0114820786393a46a2985fa0d369de6139739dd86408900024bb5659c989c5e9
...
```

</details>

### 4: Clean up workspace again

Run <code>bazel clean</code>

### 5: Run build again with cached actions

Run <code>bazel build --disk_cache /tmp/bazel-disk-cache //...</code>

Check how much cache hits you have and how much time the build takes now.

<details>
  <summary>Hint</summary> <code>bazel build</code> output will look like below:

```
training-labs$ bazel build --disk_cache /tmp/bazel-disk-cache //...
INFO: Invocation ID: 72a10c23-1d9f-462d-8097-6c22209c94ea
INFO: Analyzed 39 targets (165 packages loaded, 21329 targets configured).
...
INFO: Elapsed time: 3.414s, Critical Path: 0.64s
INFO: 284 processes: 284 remote cache hit.
INFO: Build completed successfully, 381 total actions
```

</details>

## Lab 4.4 - Bazel config groups

This lab should be done in training labs workspace.

Bazel supports shorthands for groups of CLI options in it's RC files so you don't have to type it over and over.

Add these lines to <code>user.bazelrc</code>:

```
build:_myconfig --disk_cache /tmp/bazel-disk-cache/
build:_myconfig --show_timestamps
build:_myconfig --subcommands
```

Now, if you run build with <code>--config=\_myconfig</code>, it will use disk cache, will show timestamps and subcommands.

Try it with <code>bazel clean && bazel build --config=\_myconfig //...</code> to see the difference.
