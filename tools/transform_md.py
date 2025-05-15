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


def treat_image(lines):
    new_lines = []
    for i in range(len(lines)):
        line = lines[i]
        new_line = re.sub(r"\!\[\[([^\]]+)\]\]", r"![\1](/images/link/\1)", line)
        new_lines.append(new_line)
    return new_lines


def treat_devio(lines):
    devio_lines = [line for line in lines if line.startswith("devio: ")]
    if len(devio_lines) == 0:
        return lines
    devio_line = devio_lines[0]
    if devio_line.rstrip("\n") == "devio: true":
        for i in range(len(lines)):
            if lines[i].startswith("title: "):
                lines[i] = f"title: 【DevIO】{lines[i][7:]}\n"
                print(lines[i], file=sys.stderr)
                break
    return lines


if __name__ == "__main__":
    lines = sys.stdin.readlines()

    lines = delete_newline(lines)
    lines = insert_newline(lines)
    lines = adjust_heading(lines)
    lines = treat_image(lines)

    lines = treat_devio(lines)

    print("".join(lines))
