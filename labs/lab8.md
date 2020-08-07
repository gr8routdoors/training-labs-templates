# Lab 8

## Lab 8.1 - Remote cache

This lab should be done in training labs workspace. It is almost identical with local cache lab 4.3

### 1: Add remote cache config groups

In `user.bazelrc`:

```
build:_remote_cache --remote_cache=grpcs://lab-cache.flare.build
build:_remote_cache --remote_download_toplevel

build:_remote_cache_ro --config=_remote_cache
build:_remote_cache_ro --noremote_upload_local_results

build:_remote_cache_s3 --remote_cache=https://flare-build-lab-bazel-cache.s3.amazonaws.com/ --remote_download_toplevel
```

### 2: Run build with and without cache

Without cache: `bazel clean && bazel build //... --keep_going`

With GRPC cache: `bazel clean && bazel build //... --config=_remote_cache --keep_going` - at least 2 times to populate cache.

With S3 cache: `bazel clean && bazel build //... --config=_remote_cache_s3 --keep_going` - at least 2 times to populate cache.

Compare output and find out remote cache hits.

### 3: Check contents of the remote cache in S3

Listing can be found at https://flare-build-lab-bazel-cache.s3.amazonaws.com/list.html

`ac/*` files are the action cache, which is a map of action hashes to action result metadata.
`cas/*` files are content-addressable store (CAS) of output files.

## Lab 8.2 - Remote execution

### 1: Add remote execution config group

In `user.bazelrc`:

```
build:_remote_exec --spawn_strategy=remote
build:_remote_exec --spawn_strategy=remote
build:_remote_exec --remote_executor=grpc://localhost:8080
```

### 2: Run remote execution worker locally

We will use remote worker from bazel repo, so it is possible to check it's CAS and working files.

In a separate terminal:

```
git clone https://github.com/bazelbuild/bazel.git && cd bazel

bazel build src/tools/remote:all

mkdir -p /tmp/worker/{work,cas} && \
bazel-bin/src/tools/remote/worker \
      --cas_path=/tmp/worker/cas \
      --work_path=/tmp/worker/work \
      --listen_port=8080
```

This will start remote execution worker.

### 3: Run build "remotely"

`bazel clean && bazel build //... --config=_remote_exec --keep_going`

During execution, check files in /tmp/worker/work - worker will put inputs and outputs there temporarily.

### 3: Run build "remotely" again

`bazel clean && bazel build //... --config=_remote_exec --keep_going`

This should be much faster the second time, because worker keeps cache in /tmp/worker/cas.

Check `bazel build` output for the number of remote cache hits.

## Lab 8.3 - Build Java docker image for hello world java application

This lab is similar to lab 2.1, but now we build docker image instead of jar.

### 1: Add java_image target

Create a BUILD file under `/src/main/java/com/flarebuild/hello`, load `io_bazel_rules_docker` and import `java_image()`. Name the target “hello_image”. Set <code>srcs</code> and <code>main_class</code> attributes of <code>java_image().</code>

Refer to the [documentation](https://github.com/bazelbuild/rules_docker#java_image) if needed.

Build with<code>bazel build //src/main/java/com/flarebuild/hello:hello_image</code>

<details>
  <summary>Hint</summary> Build file should look like this:

```bazel
load("@io_bazel_rules_docker//java:image.bzl", "java_image")

java_image(
    name = "hello_image",
    srcs = ["Hello.java"],
    main_class = "com.flarebuild.hello.Hello",
)
```

</details>

### 2: Add container_push target

For this task, you'll need account in a docker registry, like hub.docker.com, and use `docker login` to create credentials for the bazel to use.

In the same BUILD file, import `container_push()` from `io_bazel_rules_docker`. Name the target “push_hello”. Set <code>image</code> and <code>registry</code>, <code>repository</code> attributes of <code>container_push().</code>

Refer to the [documentation](https://github.com/bazelbuild/rules_docker#java_image) if needed.

Push the image with<code>bazel run //src/main/java/com/flarebuild/hello:push_hello</code>

<details>
  <summary>Hint</summary> Build file may look like this:

```bazel
load(
    "@io_bazel_rules_docker//container:container.bzl",
    "container_push",
)

container_push(
    name = "push_hello",
    format = "Docker",
    image = ":hello_image",
    registry = "index.docker.io",
    repository = "<your docker hub id>/hello_image",
    tag = "{BUILD_TIMESTAMP}",
    tags = ["manual"],
)
```

</details>
