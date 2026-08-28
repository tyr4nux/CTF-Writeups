#!/usr/bin/python3

from pathlib import Path

# Get machine tags
machine_tags = set()
for file in Path(__file__).parent.parent.glob('*.md'):
    data = file.read_text().splitlines()
    start = data.index('tags:') + 1
    stop = data.index('---', start)
    tags = [tag.split('- ', 1)[1] for tag in data[start:stop]]
    machine_tags.update(tags)

# Get tags from Tags.md file
my_tags = set()
file = tuple(Path(__file__).parent.parent.rglob('Tags.md'))[0]
data = file.read_text().splitlines()
tags = [tag.removeprefix('- ') for tag in data if tag.startswith('-')]
my_tags.update(tags)

print("\n--- MACHINE TAGS ---")
for tag in sorted(machine_tags):
    print(f"- {tag}")

print("\n--- EXTRA TAGS ---")
for tag in sorted(my_tags - machine_tags):
    print(f"- {tag}")

print("\n--- MISSING TAGS ---")
for tag in sorted(machine_tags - my_tags):
    print(f"- {tag}")

