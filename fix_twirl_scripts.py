import re
import glob
import os
import sys
import difflib
import argparse
import textwrap


def isBlank(str):
    return not (str and str.strip())


def fix(lines, filepath):
    imports = []
    injection = ''
    param = ''
    rest = []
    out = []

    for line in lines:
        # imports
        pattern = re.compile(r'(@+import\s+([^\n@]*))')
        matches = pattern.findall(line)
        for match in matches:
            imports.append('@import ' + match[1] + '\n')
            line = line.replace(match[0], '')
            if isBlank(line):
                continue

        # injector
        pattern = re.compile(r'(@+this\(([^\n@]*)\))')
        match = pattern.match(line)
        if match:
            injection = '@this(' + match.group(2) + ')\n'
            line = line.replace(match.group(1), '')
            if isBlank(line):
                continue

        # view parameters
        pattern = re.compile(r'^(@+(\([^\n@]*\)))')
        match = pattern.match(line)
        if match:
            param = '@' + match.group(2) + '\n'
            line = line.replace(match.group(1), '')
            if isBlank(line):
                continue

        rest.append(line)

    if imports:
        for imp in imports:
            out.append(imp)

        # add a blank line after imports
        out.append('\n')

    if injection:
        out.append(injection)

    if not param:
        raise Exception('this twirl view "' + filepath + '" has no view parameters?')

    out.append(param)

    # add a blank line after view parameters
    out.append('\n')

    # all blank lines at the beginning are skipped,
    # until a non-blank line is encountered
    skipping_mode = True
    for line in rest:
        skipping_mode &= isBlank(line)
        if not skipping_mode:
            out.append(line)

    return out


def diff(orig, new, filepath):
    # prevent bug from difflib when the last line doesn't end with a newline
    # character: https://github.com/pixee/codemodder-python/pull/116
    diff_lines = list(difflib.unified_diff(orig, new, tofile=filepath))
    if diff_lines:
        diff_lines = [
                line if line.endswith("\n") else line + "\n" for line in diff_lines[:-1]
        ] + [diff_lines[-1]]
    return "".join(diff_lines)


def run(filepath, dry):
    original = ''
    fixed = ''

    with open(filepath, 'r') as file:
        original = file.readlines()
        fixed = fix(original, filepath)

    if not dry:
        with open(filepath, 'w') as file:
            for line in fixed:
                file.write(line)

    if original != fixed:
        delta = diff(original, fixed, filepath)
        sys.stdout.writelines(delta)
        # add three linebreaks after, so that multiple printed diffs can
        # be better differentiated. note, this can be split by,
        # since empty lines in the diff itself are printed with a whitespace
        # character, not just a line break
        sys.stdout.write('\n\n\n')


def main(filepath, dry):
    if os.path.isfile(filepath):
        run(filepath, dry)
    elif os.path.exists(filepath):
        for path in glob.glob(filepath + '/**/*.scala.html', recursive=True):
            run(path, dry)
    else:
        for path in glob.glob('./**/*.scala.html', recursive=True):
            run(path, dry)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent('''\
            Find and fix twirl templates that were messed up by
            IntelliJ refactoring and code format. Run with '--dry'
            flag first to see changes.

            Prints diffs of all changes made to stdout.
            '''))
    parser.add_argument(
            'file',
            nargs='?',
            default=os.getcwd(),
            help='file or directory, defaults to current working dir')
    parser.add_argument(
            '--dry',
            action="store_true",
            default=False,
            help="do not write changes, only output diff")
    args = parser.parse_args()

    main(args.file, args.dry)
