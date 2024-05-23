# twirl-intellij-fix

Sometimes IntelliJ messes up your Twirl templates, especially if you are using
dependency injection. JetBrains has been [aware of this issue](https://youtrack.jetbrains.com/issue/SCL-21757/Twirl-Templates-Will-they-ever-be-supported-again)
for a while, but they still haven't addressed it. I have lost so much time 
manually fixing my twirl views that it granted the investment to create this
script.

This script is [idempotent](https://en.wikipedia.org/wiki/Idempotence), meaning
that it should result in the same result, even if applied multiple times.

## Usage

> [!CAUTION]
> Please note that although this script was heavily tested, it might not always
> work and could still mess up some things. Run with the `--dry` flag first
> to see if does what you expect.

```txt
usage: fix_twirl_scripts.py [-h] [--dry] [file]

Find and fix twirl templates that were messed up by
IntelliJ refactoring and code format. Run with '--dry'
flag first to see changes.

Prints diffs of all changes made to stdout.

positional arguments:
  file        file or directory, defaults to current working dir

options:
  -h, --help  show this help message and exit
  --dry       do not write changes, only output diff
```

> [!NOTE]
> I'd advise to create a snapshot of your view before applying this script
> or save the output of this command (diff of changes) to a file, 
> so that it can later be analyzed if the script made wrong changes.


## Example

An example of a twirl messed up by IntelliJ might look as follows:

```twirl
@import org.example.Foo
@@import org.example.Bar


@this(bar: Bar)
@import org.example.Example
@@(foo: String)(args: (Symbol, Any)*)(implicit bar: String)

<p>Hello @foo</p>@import org.example.Baz

```

The script will fix this to:

```twirl
@import org.example.Foo
@import org.example.Bar
@import org.example.Example
@import org.example.Baz

@this(bar: Bar)
@(foo: String)(args: (Symbol, Any)*)(implicit bar: String)

<p>Hello @foo</p>

```

## What it does

This scripts is straightforward, I advise you to take
a quick look at it before running it on your computer.

It will recursively search for `.scala.html` files in your working directory,
or the directory you provided as a parameter. If you provided a file path, 
the script will only run on the provided file.

To fix a twirl view it will:

- find imports (`@import`) anywhere in the file, even if the have multiple `@@`
symbols, are at the end of the file, or multiple imports are on the same line

- find the injector (`@this()`) anywhere in the file, even if it has multiple 
`@@` symbols

- find the view parameters (`@()`) anywhere in the file, even if it has multiple
`@@` symbols

Then it will reconstruct the view by: 

- fixing all found imports and adding them at the beginning of the file
- add a linebreak
- fixing the injector (if found), and add it to the file
- fixing the view parameters, and add it to the file
- add a linebreak
- add the rest of the content (with all previously found imports, injector, 
params removed) and stripping empty lines at the beginning

The reason for the linebreaks and the stripped empty lines is to ensure
an idempotent result.

