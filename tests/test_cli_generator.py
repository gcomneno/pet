import subprocess
import sys


def test_cli_generator_examples():
    cases = [
        (7776, "36"),
        (1024, "64"),
        (4620, "4620"),
        (1296, "1296"),
    ]

    for n, expected in cases:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pet.cli",
                "generator",
                str(n),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        assert result.stdout.strip() == expected
