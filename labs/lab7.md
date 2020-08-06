# Lab 7 - Platforms & Toolchains

In the training repository, there is a “compiler” provided, which is called Cypher. It takes input sources files ending in .cy and compiles them to “binary” outputs with extension .cb. The “compilation” process converts alphabetical characters to numeric representations (their alphabetical representation), offsetting them by a certain amount, hence the “cypher”.

There are two versions of the Cypher compiler; one which offsets characters by +1, and one that offsets by +5. The targets for these compilers are <code>//src/main/cpp/cypher:compiler1</code> & <code>//src/main/cpp/cypher:compiler5</code>, respectively.

In this lab, we’ll create platforms, toolchains, and a custom build rule to allow users to define <code>cy_library(...)</code> rules in<code> BUILD</code> files, allowing them to compile Cypher sources with Bazel.

#### Part 1: ToolchainType and Toolchain Macro instantiation

1. Create file`tools/cypher/BUILD` - Here we’ll define the toolchain type and instantiate toolchains, platforms, etc.

2. Add the following to `tools/cypher/BUILD`:

   ```bazel
   load(":toolchain.bzl", "declare_cypher_toolchains")
   package(default_visibility = ["//visibility:public"])
   toolchain_type(
     name = "cypher_toolchain",
   )
   declare_cypher_toolchains()
   ```

As you can see, this loads a macro from<code> :toolchain.bzl</code>. We’ll create that next.

#### Part 2: Toolchain definition macro

We’ll use a macro to declare a toolchain for every offset declared in a list of supported offsets; this ensures that no code is duplicated, and no code changes are required as more offsets (compiler versions) are added.

1. Create the file<code> tools/cypher/toolchain.bzl</code>; here we’ll define the macro used above.
2. Add the following to<code> tools/cypher/toolchain.bzl</code>:

   ```bazel
   load(
       "//tools/cypher/private:cypher_toolchain.bzl",
       "declare_toolchains",
       _OFFSETS = "OFFSETS"
   )
   OFFSETS = _OFFSETS

   def declare_cypher_toolchains():
      native.constraint_setting(
          name = "offset",
      )
      for offset in _OFFSETS:
          native.constraint_value(
           name = "offset_%s" % offset,
           constraint_setting = ":offset",
        )
        native.platform(
            name = "cypher%s" % offset,
            constraint_values = [
                ":offset_%s" % offset,
            ],
        )
      declare_toolchains()

   ```

You’ll see that once again, we’re loading undefined symbols<code> \_OFFSETS</code> & <code>declare_toolchains()</code> - we’ll implement these next.

#### Part 3: Implement Cypher toolchain

So far, we’ve been working on the public API (macros/targets which are publicly accessible). Now, we’ll implement the private API.

1. Create file<code> tools/cypher/private/BUILD</code>
2. Create file <code>tools/cypher/private/cypher_toolchain.bzl</code>
3. Define <code>OFFSETS</code> in <code>cypher_toolchain.bzl</code>:

   ```bazel
   OFFSETS = [1, 5]
   ```

4) Define our<code> InfoProvider</code> in<code> cypher_toolchain.bzl</code>, used to provide Cypher specific info to rules:

   ```bazel
   CypherInfo = provider(
     doc = "Information about how to invoke the cypher compiler.",
     fields = [
         "compiler",
         "offset",
     ],
   )
   ```

5. Still in <code>cypher_toolchain.bzl</code>, define a custom rule (the toolchain implementation):

   ```bazel
   def _cypher_toolchain_impl(ctx):
     return [platform_common.ToolchainInfo(
         cypherinfo = CypherInfo(
             compiler = ctx.executable.compiler,
             offset = ctx.attr.offset,
         ),
     )]

   cypher_toolchain = rule(
     implementation = _cypher_toolchain_impl,
     attrs = {
         "offset": attr.int(
             mandatory = True,
             doc = "Cypher offset",
         ),
         "compiler": attr.label(
             mandatory = True,
             cfg = "host",
             executable = True,
             doc = "Cypher Compiler",
         ),
     },
     doc = "Defines a Cypher toolchain",
     provides = [platform_common.ToolchainInfo],
   )
   ```


    Next, we’ll create the toolchain declaration macro invoked in Part 3, #2, completing this file.

6. In <code>cypher_toolchain.bzl</code>:

   ```bazel
   def declare_toolchains():
     for offset in OFFSETS:
         _declare_toolchain(offset)

   def _declare_toolchain(offset):
     toolchain_name = "cypher%s_toolchain" % offset
     impl_name = toolchain_name + "_impl"
     cypher_toolchain(
         name = impl_name,
         offset = offset,
         # select a compiler target based on offset
         # OFFSETS which don't align with targets here will cause issues;
         # As rules authors, it's important to manage this carefully.
         compiler = "//src/main/cpp/cypher:compiler%s" % offset,
     )
     native.toolchain(
         name = toolchain_name,
         toolchain_type = "//tools/cypher:cypher_toolchain",
         target_compatible_with = [
             "//tools/cypher:offset_%s" % offset,
         ],
         toolchain = ":" + impl_name,
     )
   ```


    When this macro is invoked with an argument of say, <code>42</code>, it will declare a toolchain named <code>"cypher42_toolchain</code>” in the package containing the <code>BUILD</code> file which initiated the call. In this case, this macro is called by another macro in<code> //tools/cypher</code>, in a loop over<code> OFFSETS=[1,5]</code>; the end result is that toolchains<code> //tools/cypher:cypher1_toolchain</code> and <code>//tools/cypher:cypher5_toolchain</code> are declared.


    Notice that the executable attribute `compiler` is selected based on the <code>offset</code>. This rule attribute will be used later in a custom rule; this is how the toolchain selects the correct compiler binary for usage in a build based on the specified platform.

7. Finally, we’ll need to register these toolchains in the <code>WORKSPACE</code>, so that they’re available for users at the command line:

   ```bazel
   register_toolchains(
     "//tools/cypher:cypher1_toolchain",
     "//tools/cypher:cypher5_toolchain",
   )

   ```

#### Part 4: Implement cy_library rule

1. Create file<code> tools/cypher.bzl </code>- this is where we’ll define our custom rules
2. Add the rule implementation function:

   ```bazel
   def _cypher_library_impl(ctx):
     info = ctx.toolchains["//tools/cypher:cypher_toolchain"].cypherinfo
     print(info.offset)
   ```

3) Add the rule definition:

   ```bazel
   cypher_library = rule(
     implementation = _cypher_library_impl,
     attrs = {
         "srcs": attr.label_list(allow_files = True),
     },
     toolchains = ["//tools/cypher:cypher_toolchain"],
   )

   ```

Notice two things:

- We tell it to use our toolchain (using the toolchain type defined in <code>tools/cypher/BUILD</code>
- We define one attribute: a list of labels defining our input sources. These can be files, or filegroups

  The rule is not complete (it does nothing of value yet) but at this point, if we were to instantiate a <code>cy_library</code> target in a<code> BUILD</code> and build it with Bazel (passing <code>--platforms=//tools/cypher:cypher5</code>, to select our platform), we’d see the following output:<code> DEBUG: &lt;your path>/tools/cypher/private/cypher.bzl:5:10: 5</code>

4. Complete the rule implementation function:

   ```bazel
   def _cypher_library_impl(ctx):
      info = ctx.toolchains["//tools/cypher:cypher_toolchain"].cypherinfo
      srcs = ctx.attr.srcs
      src_paths = []
      src_files = []
      outputs = []

      args = ctx.actions.args()
      args.add(ctx.bin_dir.path)

      for s in srcs:
          sfiles = s.files.to_list()
          for sfile in sfiles:
              src_files.append(sfile)
              args.add(sfile.path)
              outputs.append(
                  ctx.actions.declare_file(
                      sfile.basename.replace(".cy", ".cb"),
                  ),
              )

      ctx.actions.run(
          inputs = src_files,
          outputs = outputs,
          arguments = [args],
          progress_message =
              "Cypher%s Compiling %s source files" %
              (info.offset, len(srcs)),
          executable = info.compiler,
      )
      return DefaultInfo(
          files = depset(outputs),
      )
   ```


    The rule implementation does the following:

      - Adds the bin_dir path as the first arg to the compiler (the output directory)
      - Reads the individual source file paths for each input, passing each to the compiler
      - Declares a <code>.cb</code> output for each input .cy file
      - Runs an action using the compiler specified by the toolchain
      - Returns a <code>DefaultInfo</code> provider with containing the compiled files

5. Expose this rule for public usage: create file tools/cypher/cypher.bzl:

   ```bazel
   load("//tools/cypher/private:cypher.bzl", _cypher_libary = "cypher_library")
   cypher_library = _cypher_libary
   ```


    This is a common practice for exposing only specific parts of a rule implementation.

#### Part 5: Usage Example

1. Create a .cy source file at <code>tools/cypher/example/hello.cy</code>
2. Add contents to <code>hello.cy</code>:

   ```
   hello world
   ```

3. Create file <code>tools/cypher/example/BUILD</code>

4. Load and use our custom rule to compile the <code>.cy</code> source file:

```bazel
load("//tools/cypher:cypher.bzl", "cypher_library")

# An example cypher library; reads input .cy files and outputs

# enciphered .cb files. To specify the platform (this using a

# different toolchain), use the following command:

# bazel build //tools/cypher/example --platforms=//tools/cypher:cypher1

cypher_library(
    name = "example",
    srcs = [
    ":hello.cy",
    ],
    tags = ["manual"],
)

```

NOTE: The manual tag here ensures that this target is not built when using wildcard Bazel invocactions such as <code>bazel build //...</code> , because the platform specification shown below is necessary for this target to build correctly.

5. Build the target and observe output:

```bash
$ bazel build //tools/cypher/example --platforms=//tools/cypher:cypher5
INFO: Analyzed target //tools/cypher/example:example (22 packages loaded, 306 targets configured).
INFO: Found 1 target...
INFO: From Cypher5 Compiling 1 source files:
Compiling 1 source files...
Done.
Target //tools/cypher/example:example up-to-date:
bazel-bin/tools/cypher/example/hello.cb
INFO: Elapsed time: 7.107s, Critical Path: 1.61s
INFO: 5 processes: 5 darwin-sandbox.
INFO: Build completed successfully, 6 total actions

$ cat bazel-bin/tools/cypher/example/hello.cb
12.9.16.16.19. 27.19.22.16.8.%
```
