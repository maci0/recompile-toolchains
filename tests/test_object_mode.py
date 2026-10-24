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
            self.assertNotEqual(run("-c", str(source), "-o", str(source)).returncode, 0)
            self.assertEqual(source.read_bytes(), before)
            self.assertNotEqual(run("-c", str(source), "-o").returncode, 0)
            self.assertEqual(list(work.glob("*.tmp.*")), [])


if __name__ == "__main__":
    unittest.main()
