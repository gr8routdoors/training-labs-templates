# VS Code Config

This folder contains rich VS Code settings and extensions for running Java, Bazel, Go, Docker, and other tools from inside VS Code IDE.

## Simple Install

1. Download and Install VSCode from: https://code.visualstudio.com/download

2. Start Visual Studio Code (you can do it from the Terminal with this command:
    `open '/Applications/Visual Studio Code.app'`)

3. Next, you must invoke the 'Show All Commands' drop down, but pressing either ⌘-⇧-P (Command-Shift-P), or alternatively  ⌘-⇧-A. 
   
4. Once you see the drop down, type "shell co" and you should see "Shell Command: install `code` command in the `PATH`" — select that option and press Enter.

From now on, you should be able to open a source folder from the iTerm or Terminal, by running `code .`

Now, let's install VSCode Extensions that will allow you to work with C/C++, Python, Java, Go and Bazel:

```
make install
```

If everything worked, you are done. This would have installed 

The rest is optional.

## Contents of the `.vscode` Folder

### Required Files for VSCode

`settings.json`
: "Workspace" settings for VS Code, such as fonts, themes, and other settings.

`extensions.json`
: The recommended way to suggest a list of extensions to install for this Workspace.

### Optional Installers

The file `extensions.json` offers a way to install extensions via a user action.

To install all extensions on the command line, you can use the commands below:

`mono-install`
: a script that downloads and installs several high-quality mono-spaced fonts, and can be invoked directly, OR via the Makefile.

`extensions.txt`
: A frozen "extensions list" file, generated with the `Makefile` below.

`Makefile`
: You can use this to either generate the list of current extension, or auto-load the previously frozen list of extensions, if the previous method is somehow not working for you.

: To see list of Makefile targets, run `make help`:

```
   install                       Install mono-fonts and VS Code Extensions
   freeze-extensions             Freeze VS Code Extensions
   install-extensions            Installed previously frozen extensions
   install-mono-fonts            Install Mono-Spaced fonts for IDE
```
