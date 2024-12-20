#!/usr/bin/env python
import re
import sys


def delete_newline(lines):
    in_code = False
    new_lines = []
    for i in range(len(lines)):
        if i == len(lines) - 1:
            new_lines.append(lines[i])
            break

        curr_line = lines[i]
        next_line = lines[i + 1]
        if curr_line.startswith(("```", "---")):
            in_code = not in_code
            new_lines.append(curr_line)
            continue
        if curr_line.strip() == "":
            new_lines.append(curr_line)
            continue
        if next_line.strip() == "":
            new_lines.append(curr_line)
            continue

        if in_code:
            new_lines.append(curr_line)
        else:
            if re.match(
                r"(#+ |\s*- |\s*\* |\s*\d+\. |https?://\S+\s*$|!\[|:::)", curr_line
            ):
                new_lines.append(curr_line)
            elif re.match(
                r"(#+ |\s*- |\s*\* |\s*\d+\. |```|https?://\S+\s*$|!\[|:::)", next_line
            ):
                new_lines.append(curr_line)
            else:
                new_lines.append(curr_line[:-1] + " ")
    return new_lines


def insert_newline(lines):
    in_code = False
    new_lines = []
    for i in range(len(lines)):
        if i == len(lines) - 1:
            new_lines.append(lines[i])
            break

        curr_line = lines[i]
        next_line = lines[i + 1]

        if in_code:
            new_lines.append(curr_line)
        else:
            if re.match(r"(\s*- |\s*\* |\s*\d+\. )", curr_line):
                new_lines.append(curr_line)
                if not re.match(
                    r"(#+ |\s*- |\s*\* |\s*\d+\. |```|https?://\S+\s*$|!\[)", next_line
                ):
                    new_lines.append("\n")
            else:
                new_lines.append(curr_line)
    return new_lines


def adjust_heading(lines):
    in_code = False
    new_lines = []
    for i in range(len(lines)):
        curr_line = lines[i]

        if curr_line.startswith("```"):
            in_code = not in_code

        if in_code:
            new_lines.append(curr_line)
        else:
            if re.match(r"#+ ", curr_line):
                new_lines.append("#" + curr_line)
            else:
                new_lines.append(curr_line)
    return new_lines


if __name__ == "__main__":
    lines = sys.stdin.readlines()

    lines = delete_newline(lines)
    lines = insert_newline(lines)
    lines = adjust_heading(lines)

    print("".join(lines))
