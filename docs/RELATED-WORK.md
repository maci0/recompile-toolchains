# How this compares to Compiler Explorer

[Compiler Explorer](https://godbolt.org) ("godbolt") is the other large public
collection of old and new compilers, and it solves the same first problem we do:
how do you keep hundreds of pinned toolchains installable and honest.  Its
pipeline, from the project's own
[overview](https://github.com/compiler-explorer/compiler-explorer/blob/main/docs/AddingCustomCompilersOverview.md):

1. build each compiler (for GCC, in
   [`compiler-explorer/gcc-builder`](https://github.com/compiler-explorer/gcc-builder),
   itself a Docker build);
2. upload the tarball to S3;
3. install it with
   [`ce_install`](https://github.com/compiler-explorer/infra/blob/main/bin/lib/ce_install.py)
   driven by YAML such as
   [`bin/yaml/cpp.yaml`](https://github.com/compiler-explorer/infra/blob/main/bin/yaml/cpp.yaml),
   into a shared NFS tree at `/opt/compiler-explorer/<compiler>-<version>/`;
4. point the site at it from an
   [`etc/config/*.properties`](https://github.com/compiler-explorer/compiler-explorer/blob/main/etc/config/c%2B%2B.amazon.properties)
   entry (`exe`, `options`, `versionRe`, `semver`, …), with per-compiler
   behaviour in the TypeScript
   [drivers](https://github.com/compiler-explorer/compiler-explorer/tree/main/lib/compilers).

The YAML and our `sources.json` are recognisably the same idea: a declarative
list of downloads with a verification step (`check_exe`/`check_file` there, a
`sha256sum -c` inside the Docker build here).  The differences are deliberate:

| | Compiler Explorer | rebrew (this repo) |
| --- | --- | --- |
| Unit | a compiler install in a shared tree | one self-contained OCI image per toolchain |
| Isolation | host install plus CE's own execution sandbox | the container boundary; `--network none` runs |
| Fetch | tarballs, S3, installer scripts, `url` templates with `{{name}}` | one pinned URL + sha256 per profile (secondary pins for binutils/parsers/SDKs) |
| Verification | `check_exe` runs the installed binary once | sha256 verified in-build, plus a per-image smoke compile and contract tests |
| Name normalisation | `compiler.<id>` entries may share one install, differing in flags/target | `aliases` map community ids to a profile, with hash evidence in [`PROVENANCE.md`](PROVENANCE.md) |
| Per-compiler flags/version regex | yes, first-class (`options`, `versionRe`) | no: the wrapper forwards argv, the consumer supplies flags |
| Scope | a compile *service* (execution, caching, UI) | the toolchains and their runtimes only |

What we borrowed conceptually: a pinned, declarative source list; an explicit
install-verification step (ours is the smoke test in
[`ADDING-TOOLCHAIN.md`](ADDING-TOOLCHAIN.md)); and keeping one installation
behind several names; CE does it with per-compiler flag sets, we do it with
`aliases` when the compiler binary is byte-identical and with a separate image
when the entry point differs (`ido7.1_c++`, `wpp10.0a`, `agbcc_arm`).

What we deliberately do not have: CE's `versionRe`/`options` metadata, its
runtime sandboxing and caching, and its hundreds of *upstream GCC/Clang builds*
fetched from CE's own S3; that repository is the source of truth for those, and
this one is the source of truth for preserved, vendor and console toolchains.

## Upstream inventory check — 2026-10-21

**Three useful decomp.me profiles are missing, plus one verified MSVC alias.**
Repair the two dead DOS-runtime downloads before qualifying another release.
This is an ingestion assessment; no compiler recipes, pins or images were changed.

The local baseline is `a17e20094f46abfd140e227ee94311e6741f5eb8`:
276 profiles across 28 families in `sources.json`, not the 272 still quoted in
some workspace overview documents. Profiles are build definitions, not proof
that every image has been built or qualified.

Compared both upstream layers, because neither alone lists every usable profile:

- [decompme/compilers values.yaml](https://github.com/decompme/compilers/blob/1f528ebeaf198e747d75caffaa319985b3a33a2d/values.yaml):
  230 distinct package IDs, including shared runtime packages.
- [decomp.me compiler definitions](https://github.com/decompme/decomp.me/blob/8ae25062310f3af726e1b1a35c3d65c5854f9f6a/cromper/cromper/compilers.py)
  and [Linux installation list](https://github.com/decompme/decomp.me/blob/8ae25062310f3af726e1b1a35c3d65c5854f9f6a/cromper/compilers/compilers.linux.yaml):
  242 active compiler definitions. Their paths have moved under `cromper/`;
  the old `backend/coreapp/compilers.py` location now returns 404.
- [Compiler Explorer C](https://godbolt.org/api/compilers/c) and
  [C++](https://godbolt.org/api/compilers/c++), its
  [installation inventory](https://github.com/compiler-explorer/infra/blob/main/bin/yaml/cpp.yaml),
  and the upstream releases listed below. CE IDs include target/flag variants;
  its counts are not counts of distinct compiler implementations.

### Ingest next

| Priority | Candidate | Evidence and required work |
| --- | --- | --- |
| First | Repair `base-dosemu` pins | The existing `tests/check_pins.py` completed 334 URL checks: 332 passed; the pinned `libfdldr35` and `libfdpp35` downloads returned HTTP 404. These block fresh builds inheriting `base-dosemu`, including the current DOS Saturn compiler. Select a compatible retained package set, verify hashes, then rebuild and smoke-test the DOS runtime. |
| High | `mwcc_41_51213p1` | A distinct PowerPC compiler in `GC/3.0a3p1` of `compilers_20251118.zip`. Add a separate profile beside `mwcc-4.1-51213`, using its recipe pattern and the new bundle pin. The unpatched compiler is not an alias for this binary. |
| High | `cygnus-2.7-96Q3-native` | decomp.me now uses the Linux i386 `cc1-native` from [saturn-compiler-repro v1.0.0](https://github.com/sozud/saturn-compiler-repro/releases/tag/v1.0.0). Add the native profile with preprocessing and `sh-elf-as`; it avoids DOSEMU/KVM at compile time. Upstream also publishes `cc1-native64`, which is a separate candidate requiring output-parity checks. |
| High | `shc-v5.0r32-sh2` | An active Saturn profile derived from the SHC 5.0r32 tree we already package. Upstream supplies SH-2/big-endian flags and ROF-to-ELF conversion with `--isa=sh2 --padding 0xff`. Our image exposes the raw compiler and an older converter without the padding option. Package a distinct Saturn profile and pin the updated helper; an alias alone would not supply this pipeline. |
| Small | `msvc8.0sp1` alias | Upstream's new `Drahsid/ffxiv_msvc8.0sp1@0d6f444cfc120e4e62a092726844fa310c74b1bc` package has exactly the same Git blobs for `cl.exe`, `c1.dll`, `c1xx.dll` and `c2.dll` as our pinned `archaic-msvc/msvc800_sp1@4b1bafba636f67eb76f548f0f0e7f38864091a4a`. Add the alias/equivalence to the existing `msvc-8.0-sp1`; no second compiler tree is needed. It appears in the package inventory but not yet in the inspected application compiler definitions. |

Artifact checks supporting these recommendations:

- Downloaded both dated decomp.dev bundles and compared every common file's
  bytes. The November bundle adds exactly five files in `GC/3.0a3p1`, removes
  none and changes only `info.txt` elsewhere. Existing compiler payloads are
  unchanged, so there is no need to replace the old bundle for existing profiles.
- `GC/3.0a3/mwcceppc.exe` SHA256:
  `66553cf100ee7e1793f368a39be6218292cd19a7c8636f2f1493b572ad5eaec2`.
  Patch 1 SHA256:
  `a601144936eab972a9c9d7c443bef80e417260a5940cac083373dfe1eb5cafc9`.
- [November bundle](https://files.decomp.dev/compilers_20251118.zip), 77,332,914 bytes,
  SHA256 `69b0d4980a2eccea4ae6e70b486714b5190cb6c75e3bc7b8fb5878a8854d0d1c`.
- Downloaded and checked both Saturn release archives against GitHub's asset
  digests: `cc1-native.tar.gz` SHA256
  `3f215db5c6c6040461b82b85f4d7564da59da3064d7c13b872c16ad9f5731497`
  contains an ELF32 executable; `cc1-native64.tar.gz` SHA256
  `67f8072355ea2860decb48df87001badbad180008044be1181c1178b65163320`
  contains an ELF64 executable. Native execution and matching output remain
  unqualified; the upstream reconstruction includes a deterministic CSE fix.
- The [updated ROF converter](https://gist.githubusercontent.com/masonc15/cb2354b439e35f1400c71edfca7171ca/raw/2556b4f781d49b167be0952b4420fadd2b5a313f/rof2elf.py)
  SHA256 is `807f34336f9f3c803ccc2ab01fbd1630e4c7388c29a357fe2f5ba10d2c7dfdef`.
  Confirm its licensing/provenance before adding this new upstream source.

### Other sources and lower-priority updates

| Source | Current finding | Recommendation |
| --- | --- | --- |
| [GNU GCC releases](https://gcc.gnu.org/releases.html) / Compiler Explorer | Our native x86-64 GCC profiles stop at 12.3.0 and 14.2.0. Upstream now has 12.5, 13.5, 14.4, 15.3 and 16.2; CE lists GCC 16.2. | Add a separate 16.2.0 profile as the smallest modern baseline expansion. Add older release lines when a target needs them; preserve existing matching pins. |
| [LLVM releases](https://github.com/llvm/llvm-project/releases/tag/llvmorg-23.1.4) / Compiler Explorer | Our newest native x86-64 Clang is 18.1.8. CE has 19/20/21/22/23-era entries; LLVM's latest stable release is 23.1.4, published October 20. | Add a separate 23.1.4 profile if modern coverage is wanted, after checking prebuilt host dependencies. CE's 23.1.0 entry is not the latest LLVM patch release. |
| [Open Watcom releases](https://github.com/open-watcom/open-watcom-v2/releases/tag/2026-10-01-Build) | A dated October 1 snapshot follows our September 1 snapshot. | Optional new snapshot profile. Do not silently replace the existing `2.0` pin: compiler output may change. Avoid the mutable `Current-build`/`Last-CI-build` tags. |
| [decompals/old-gcc](https://github.com/decompals/old-gcc/releases/tag/0.17) | Latest release remains 0.17; our old-GCC profiles already use it. | No version refresh needed. decomp.me still references older release packages for many of these IDs. |
| [decompals/wibo](https://github.com/decompals/wibo/releases/tag/1.2.0) and [pret/agbcc](https://github.com/pret/agbcc/releases/tag/release) | Latest wibo is our 1.2.0, including the same x86-64 asset digest. The current pret/agbcc release asset digest also matches our pin. | No refresh needed for those checked artifacts. |
| [decompme/compilers PR 82](https://github.com/decompme/compilers/pull/82) | Open proposal to add MSVC 12.0 Update 4, beyond our 11.0 line. | Watchlist, not merged catalog coverage or a qualified ingestion source yet. |

### Accounted-for gaps and limits

Of the 242 active upstream compiler IDs, seven lack a local name/equivalence:
the three high-priority profiles above, plus the four IDO Pascal/IRIX4 IDs
already explained in the generated [provenance gaps](PROVENANCE.md). The package
inventory separately includes the already-documented broken PSP GCC 1.7.1
archive and `wibo_dlls`, which is a runtime bundle rather than a compiler.

Also swept the `decompme/compilers` release asset list. Its 14 URLs not directly
referenced by our manifest include alternate MSVC/SN/ProDG packages, the two
EE-GCC versions we already extract from `ps2_compilers.tar.xz`, and the known
broken PSP archive. These names alone do not establish new compiler builds;
this check did not rehash every alternate repack. Available GitHub primary
asset digests for currently referenced decompme/old-gcc URLs matched our pins.

The public `decomp.me/api/compilers` endpoint returned HTTP 403, so decomp.me
coverage here means its pinned repository definitions, not a proven deployed
inventory. URL checks establish availability, not full download integrity.
No Docker builds, compiler executions or output-parity smoke tests were run.

### Ingestion follow-up — 2026-10-21

The five recommended compiler profiles and the verified MSVC alias are now
registered, bringing the manifest to 281 profiles. Existing compiler source
pins remain unchanged. The two deleted DOSEMU library URLs have been replaced
with verified October 12 packages from the same PPA.

The Saturn pipelines retain failed-stage errors and only copy a completed
object to the requested output. Their smoke cases also check that invalid C
fails without replacing an existing output. Rebrew registers all five images
and publishes their explicit entrypoints for Recompile consumers. The SHC
golden masks only the ROF timestamp copied into ELF `.comment`.

The native and DOS Saturn profiles produced matching instruction bodies for
three optimized samples (addition, a loop and a conditional). GNU's assembler
added a trailing SH NOP to two native sections; complete section-byte parity
with the DOS profile is not claimed. Keep the DOS profile for exact historical
section padding.

Qualification: all five images built and compiled the smoke source, the
refreshed DOSEMU base compiled both Saturn and PS1 samples, and all 340 URL
checks passed. The catalog's 29 unit tests and wrapper harness, Rebrew's 125
toolchain tests, lint and type checks passed. Recompile's source consumer
resolved all five new profiles against the updated Rebrew source; installed
releases need the updated Rebrew package before those IDs appear.

The optional Watcom snapshot and native64 Saturn variant remain outside this
ingestion; neither replaces an existing pinned compiler.

## Recheck — 2026-10-23

**No new compiler IDs or compiler release assets since October 21. One PS1
assembly-pipeline update needs attention, and Daze is a runtime candidate.**
The local manifest remains at 281 profiles. This recheck changes documentation
only; the previous ingestion remains local and unpublished.

### PS1: ingest maspsx as a qualified pipeline variant

[decompme/compilers commit c5f041c](https://github.com/decompme/compilers/commit/c5f041cdc9610fb5213b7ae3c88cce02f554c4d3)
advances maspsx from `423ffc6bca05e53f9b7ab06159d0cbe71111bc90` to
`4ffa8b5106f9780d5d4aa7609f184949433ddbbc` across 22 PS1 GCC packages.
There are seven intervening maspsx commits, including common-symbol alignment,
`.comm`/`.lcomm` and gp-relative handling, immediate-load expansion, and
[NOP/label ordering around mflo/mult](https://github.com/mkst/maspsx/commit/4ffa8b5106f9780d5d4aa7609f184949433ddbbc).

The existing gap is larger than a stale helper pin: **none of our 22 matching
profiles packages maspsx**. Their recipes point the GCC assembler at
`/usr/bin/mipsel-linux-gnu-as` directly. Upstream instead installs an assembler
shim invoking maspsx with `--run-assembler`; maspsx transforms GCC assembly to
reproduce PSY-Q ASPSX behavior before calling GNU as. Therefore matching GCC
front ends and aliases do not establish equivalent object output.

Next ingestion should pin this maspsx revision, preserve the current plain-GNU-as
profiles, and qualify explicit matching variants against upstream fixtures.
Prioritize multiplication/division hazards, labels, common-symbol layout and
gp-relative accesses. No local PS1 output-equivalence run was performed here.

### DOS: evaluate Daze 0.3.0

The updated [maspsx assembler test instructions](https://github.com/mkst/maspsx/blob/4ffa8b5106f9780d5d4aa7609f184949433ddbbc/aspsx/README.md)
replace DOSEMU2/Wine with Daze/Wibo for the reference ASPSX executables.
[Daze 0.3.0](https://github.com/mkst/daze/releases/tag/0.3.0), released October 17,
is newly identified by this recheck, not a release since the previous audit.
It supports KVM and a Unicorn software backend; source is MIT and release
binaries include GPLv2 dependency terms.

It is a candidate for reducing the DOS images' dependence on KVM and the
pruned Ubuntu PPA packages. Test our exact PSY-Q and Saturn binaries before
changing the runtime. Upstream's [known limits](https://github.com/mkst/daze-tests/blob/main/KNOWN-LIMITS.md)
include a large CC1PSX 2.7.2 workload exceeding a 60-second Unicorn limit;
software emulation is not automatically a performance-equivalent replacement.

### Health and unchanged sources

- All 340 URL availability checks passed, including the refreshed DOSEMU pins.
- All 29 catalog unit tests passed; all 553 generated files are current.
- The five newly ingested profiles passed their existing Rebrew smoke goldens.
- Compared 49 manifest profiles against available upstream primary-asset
  SHA256 digests; no mismatches. This does not rehash every downloaded archive.
- decomp.me application compiler definitions and install list are unchanged at
  `1b15f4891a736d1629967d205e58d7605caa09ca`: 242 compiler IDs, with only the
  four previously documented IDO Pascal/IRIX4 IDs unmapped locally.
- Compiler Explorer C/C++ API snapshots are unchanged. GCC 16.2, LLVM 23.1.4,
  old-gcc 0.17, Wibo 1.2.0, the checked pret/agbcc asset and native Saturn
  v1.0.0 remain current. Open Watcom's dated October snapshot remains optional;
  its mutable build tags advanced. MSVC 12.0 Update 4 PR 82 is still open.

No images were rebuilt, no new toolchain was ingested, and Daze was not executed
in this recheck. The existing Saturn padding and converter-licensing limits
remain as documented above.

## Ingestion follow-up — 2026-10-23

The requested maspsx and Daze variants are now ingested locally. The catalog
contains **308 profiles**, including 27 new variants; all 281 definitions from
the recheck are unchanged. Existing aliases still select their original images.

### PS1 GCC with maspsx

All 22 matching GCC profiles have an explicit `-maspsx-4ffa8b5` variant.
Each retains its original compiler archive and pins the MIT-licensed maspsx
source at `4ffa8b5106f9780d5d4aa7609f184949433ddbbc` (archive SHA-256
`c9d007c88bd2ac7f63ba65e8b7b07732a2b06034eba55b41c3ccfaacc926f464`).
The GCC assembler shim invokes `maspsx.py --run-assembler`; select another
ASPSX behavior version with GCC's `-Wa,--aspsx-version=<version>` when needed.
The original plain-GNU-as profiles remain available separately.

### DOS compilers with Daze

Five explicit `-daze-0.3.0` variants cover PSY-Q 2.6.3 build 221, 3.3, 3.5,
3.6 and Saturn Cygnus 2.7-96Q3. They preserve the DOS compiler and converter
pins and use the [Daze 0.3.0 release](https://github.com/mkst/daze/releases/tag/0.3.0)
binary (SHA-256
`4b6f55e5813a0752eedd1462ef4e3877a7ab0d0a244d806f3fab495bcee2894c`).
All 11 release notice and source-reference text assets are pinned and installed
in `/opt/daze-notices`, including the dependency license terms.

The wrappers explicitly select `--backend unicorn`; these images need neither
`/dev/kvm` nor the DOSEMU PPA at runtime. Compiler files mount read-only, each
DOS stage uses a private writable scratch mount and the shared timeout watchdog,
and the finished ELF replaces the destination only after every stage succeeds.
Saturn uses line-marker-free host preprocessing before its original DOS CPP,
CC1 and assembler stages. Existing DOSEMU profiles remain selectable.

Build and qualify a variant through the updated Rebrew source registry:

```sh
rebrew toolchain build gcc-2.7.2-psx-maspsx-4ffa8b5
rebrew toolchain smoke gcc-2.7.2-psx-maspsx-4ffa8b5 --json
rebrew toolchain build psyq-3.3-daze-0.3.0
rebrew toolchain smoke psyq-3.3-daze-0.3.0 --json
```

### Qualification and limits

- All 27 images built and passed their measured Rebrew smoke goldens. Repeated
  smoke compiles produced stable full-object hashes.
- The pinned maspsx source passed all 169 upstream unit tests inside its image.
  The retained image smoke harness runs those tests for maspsx profiles.
- Compared Daze and DOSEMU on three C samples per compiler: all 14 accepted
  pairs matched initialized allocated section bytes, BSS sizes and relocation
  records. This is not a claim of whole-file ELF identity. The remaining
  PSY-Q 2.6.3 globals sample failed identically in both pipelines because the
  existing bundled parser rejects relocation type 30.
- All five Daze variants passed retained checks for output-first arguments,
  source/output collision refusal and preservation of an existing output after
  invalid source fails. A representative maspsx image passed the image harness.
- All 452 source URL checks, 29 catalog unit tests, wrapper helper tests and
  125 Rebrew toolchain tests passed; generation, lint and type checks passed.
  Recompile resolves all 27 profiles against the updated Rebrew source, and
  its 13 entrypoint and catalog-pin consumer tests passed.

Large DOS inputs can be slow under Unicorn, as upstream documents; the Daze
variants do not automatically switch to KVM. The PSY-Q 2.6.3 relocation-parser
limit is inherited and remains unresolved. The full 308-profile image matrix
was not rebuilt. These changes and local images are not published; installed
consumers need the updated Rebrew package to resolve the new IDs.
