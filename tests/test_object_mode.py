"""The ELF adapter preserves raw calls and publishes only successful outputs."""

from __future__ import annotations

import copy
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import generate


class TestObjectMode(unittest.TestCase):
    def test_raw_compile_and_failed_publish(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            compiler = work / "compiler"
            compiler.write_text(
                '#!/bin/sh\nprintf "%s\\n" "$@" > "$CC_LOG"\n'
                '[ "${CC_FAIL:-0}" = 0 ] || exit 7\n'
                'while [ "$#" -gt 0 ]; do\n'
                '  if [ "$1" = -o ]; then printf "assembly\\n" > "$2"; exit; fi\n'
                "  shift\ndone\n"
            )
            compiler.chmod(0o755)
            assembler = work / "arm-none-eabi-as"
            assembler.write_text(
                '#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\n'
                '  if [ "$1" = -o ]; then printf "ELF object\\n" > "$2"; exit; fi\n'
                "  shift\ndone\n"
            )
            assembler.chmod(0o755)
            entry = copy.deepcopy(generate.manifest()["agbcc"])
            rec = generate.recipe(entry)
            rec["binary"] = str(compiler)
            wrapper = work / "cc"
            body = generate.render_wrapper("agbcc", entry)
            common = generate.REPO / "base/wrapper-common.sh"
            body = body.replace("/usr/local/lib/rebrew/wrapper-common.sh", str(common))
            wrapper.write_text(body)
            wrapper.chmod(0o755)
            source = work / "source with spaces.c"
            source.write_text('#include "offset.h"\nint add(int a,int b){return a+b+OFFSET;}\n')
            headers = work / "headers"
            headers.mkdir()
            (headers / "offset.h").write_text("#define OFFSET 2\n")
            output = work / "output with spaces.o"
            log = work / "args"
            env = dict(os.environ, PATH=f"{work}:{os.environ['PATH']}", CC_LOG=str(log))

            def run(*args: str, fail: bool = False) -> subprocess.CompletedProcess[str]:
                return subprocess.run(  # noqa: S603 (generated wrapper in isolated test directory)
                    [str(wrapper), *args],
                    cwd=work,
                    env=env | {"CC_FAIL": str(int(fail))},
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )

            raw = run(str(source), "-o", str(output))
            self.assertEqual(raw.returncode, 0, raw.stderr)
            self.assertEqual(output.read_bytes(), b"assembly\n")
            self.assertEqual(log.read_text().splitlines(), [str(source), "-o", str(output)])
            compiled = run("-c", "-Iheaders", str(source), "-o", str(output))
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            self.assertEqual(output.read_bytes(), b"ELF object\n")
            failed = run("-c", "-Iheaders", str(source), "-o", str(output), fail=True)
            self.assertEqual(failed.returncode, 7)
            self.assertEqual(output.read_bytes(), b"ELF object\n")
            before = source.read_bytes()
            self.assertNotEqual(
                run("-c", "-Iheaders", str(source), "-o", str(source)).returncode, 0
            )
            self.assertEqual(source.read_bytes(), before)
            self.assertNotEqual(run("-c", str(source), "-o").returncode, 0)
            self.assertEqual(list(work.glob("*.tmp.*")), [])
            output_directory = work / "objects"
            output_directory.mkdir()
            link = work / "objects-link"
            link.symlink_to(output_directory, target_is_directory=True)
            for destination in (output_directory, link):
                with self.subTest(destination=destination.name):
                    result = run("-c", "-Iheaders", str(source), "-o", str(destination))
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(list(output_directory.iterdir()), [])

    def test_daze_refuses_directory_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            tools = {
                "daze": (
                    '#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\n'
                    '  if [ "$1" = -o ]; then printf "stage\\n" > "${2#D:/}"; exit; fi\n'
                    "  shift\ndone\nexit 2\n"
                ),
                "unix2dos": '#!/bin/sh\ncp -- "$3" "$4"\n',
                "convert": '#!/bin/sh\ncp -- "$1" "$3"\n',
            }
            for name, script in tools.items():
                tool = work / name
                tool.write_text(script)
                tool.chmod(0o755)
            profile = "psyq-3.3-daze-0.3.0"
            entry = generate.manifest()[profile]
            body = generate.render_wrapper(profile, entry)
            body = body.replace(
                "/usr/local/lib/rebrew/wrapper-common.sh",
                str(generate.REPO / "base/wrapper-common.sh"),
            )
            body = body.replace("/usr/local/bin/daze", str(work / "daze"))
            body = body.replace(
                f"/opt/{generate.install_root(entry)}/psyq-obj-parser", str(work / "convert")
            )
            wrapper = work / "cc"
            wrapper.write_text(body)
            wrapper.chmod(0o755)
            source = work / "input.c"
            source.write_text("int x;\n")
            output_directory = work / "objects"
            output_directory.mkdir()
            link = work / "objects-link"
            link.symlink_to(output_directory, target_is_directory=True)
            for destination in (work / "result.o", output_directory, link):
                with self.subTest(destination=destination.name):
                    result = subprocess.run(  # noqa: S603 (generated wrapper, stub tools)
                        [str(wrapper), "-c", str(source), "-o", str(destination)],
                        cwd=work,
                        env=dict(os.environ, PATH=f"{work}:{os.environ['PATH']}"),
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=False,
                    )
                    if destination.name == "result.o":
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(destination.read_bytes(), b"stage\n")
                    else:
                        self.assertNotEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(list(output_directory.iterdir()), [])
            self.assertEqual(list(work.glob("*.tmp.*")), [])


if __name__ == "__main__":
    unittest.main()
