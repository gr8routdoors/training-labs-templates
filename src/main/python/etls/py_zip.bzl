def py_zip(name, srcs, out_override = None):
    out = "%s.zip" % (out_override if out_override else name)
    native.genrule(
        name = name,
        srcs = srcs,
        tools = ["@bazel_tools//tools/zip:zipper"],
        outs = [out],
        cmd = "$(location @bazel_tools//tools/zip:zipper) c $@ $(SRCS)",
    )
