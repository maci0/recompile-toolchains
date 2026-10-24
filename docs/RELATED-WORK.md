# How this compares to Compiler Explorer

Current results: [2026-10-25 ingestion and repairs](#ingestion-and-repairs--2026-10-25).

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

## Audit and wider source search — 2026-10-25

**Repair the DOSEMU download pins first, then address consumer coverage.
The best additional compiler candidates are MSVC 12.0 Update 4 and DJGPP;
PSPDEV, PS2DEV and Bootlin offer useful modern cross-compilers.** These are
recommendations from a fresh online audit, not newly ingested profiles.
The catalog remains at 308 profiles across 28 families at
`842c485b7efd708d17fce922b6983f08b1f5101f`.

The [machine-readable evidence](toolchain-audit-2026-10-25.json) records
the upstream revisions, failures, candidate download hashes and the complete
list of catalog names missing from the packaged consumer registry.
Version and asset observations were checked overnight October 24–25 in
Singapore (October 24 UTC); a candidate is not qualified until its image
builds and its output passes consumer tests.

### Current findings, in repair order

| Priority | Finding | Impact and next action |
| --- | --- | --- |
| First | Two DOSEMU pins return HTTP 404 again | `libfdldr35` and `libfdpp35` build `1.11-10003-1716-2f10d8a+202610122230~ubuntu24.04.1` have been pruned. Cold builds of the four original DOS PSY-Q profiles and original Saturn Cygnus profile cannot fetch their runtime. The current [Noble PPA index](https://ppa.launchpadcontent.net/dosemu2/ppa/ubuntu/dists/noble/main/binary-amd64/Packages.gz) advertises build `1.11-10003-1717-f2e1f7d+202610211533~ubuntu24.04.1`; its filenames and advertised hashes are in the evidence file, but that replacement has not been downloaded or qualified here. Verify the replacement pair and smoke both PSY-Q and Saturn. For durable cold builds, retain the exact permitted package inputs or build the runtime from pinned sources instead of repeatedly depending on PPA retention. |
| First | The generic builder couples every selection to DOSEMU | `build.sh:330` unconditionally builds all three bases before any selected toolchain. Consequently an uncached `./build.sh <native-or-daze-profile>` can fail at the unrelated DOSEMU base too. Make base selection follow the selected images' dependency closure. The current Rebrew builder derives the required bases from the selected Dockerfile; the 27 new profiles can use that route. Existing cached images still run. |
| High | Catalog coverage exceeds packaged consumer coverage | The source Rebrew registry has **78 names**. Against all 308 canonical manifest names, **76** resolve to the exact catalog image and an entrypoint, **230** are absent, and **two** IDO names select different native images. This is a pre-existing integration gap; all 27 maspsx/Daze additions resolve correctly. Register useful existing recipes with measured smoke goldens before treating 308 as a service-available count. Manifest aliases belong to the build catalog and are not automatically imported into Rebrew/Recompile. Plugins and project overlays can provide additional names. |
| Review | Existing IDO naming differs between layers | Registry `ido-5.3` and `ido-7.1` select `rebrew/ido:5.3-linux` and `rebrew/ido:7.1-linux`; manifest names select the `5.3-n64` and `7.1-n64` images. The explicit manifest `ido-5.3-linux` / `ido-7.1-linux` names are absent from the packaged registry. Reconcile canonical naming and preserve deliberate native/IRIX choices; do not silently repoint existing profiles. |
| Retained limits | Prior qualification limits still apply | Daze Unicorn can be slow on large input; the inherited PSY-Q 2.6.3 parser rejects relocation type 30 on one globals fixture. The native Saturn assembler's trailing padding differs from DOS, and the SH-2 converter fork still lacks a declared license. Today's smoke successes do not remove those limits. |

### Upstream changes since October 23

- [decomp.me application commit b0e39b5](https://github.com/decompme/decomp.me/commit/b0e39b5aa591586c838df50fc32af1a498096fc5)
  adds `msvc8.0sp1` to the definitions and installation list, bringing active
  compiler IDs to **243**. Our catalog already maps it to `msvc-8.0-sp1`
  using the previously verified identical compiler blobs. It needs no second
  compiler image. The four known IDO Pascal/IRIX4 gaps remain.
- [decompme/compilers](https://github.com/decompme/compilers/tree/c5f041cdc9610fb5213b7ae3c88cce02f554c4d3)
  is unchanged at `c5f041c`: 230 package IDs, 228 mapped locally and two
  declared exclusions (`wibo_dlls` and the broken PSP GCC 1.7.1 archive).
  There are no added release assets or changed published asset digests.
- [maspsx](https://github.com/mkst/maspsx/commit/4ffa8b5106f9780d5d4aa7609f184949433ddbbc)
  remains at our `4ffa8b5` pin. Daze 0.3.0, old-gcc 0.17, Wibo 1.2.0,
  Saturn native v1.0.0, LLVM 23.1.4 and the checked pret/agbcc release asset
  remain current against the inspected sources. [GCC releases](https://gcc.gnu.org/releases.html)
  still list 16.2.0 as the newest release.
- [Compiler Explorer C](https://godbolt.org/api/compilers/c) remains at
  1,057 IDs. [C++](https://godbolt.org/api/compilers/c++) increases to 1,215
  with `gcc_p0917-trunk`. Its [configuration](https://github.com/compiler-explorer/compiler-explorer/blob/main/etc/config/c%2B%2B.amazon.properties)
  marks it nightly and identifies an experimental overloadable conditional
  operator branch. It has no immediate historical-matching priority; only
  ingest it for a specific experiment with a commit and output qualification.
- [Open Watcom](https://github.com/open-watcom/open-watcom-v2/releases/tag/2026-10-01-Build)
  still offers the dated October 1 snapshot beyond our September pin. Mutable
  `Current-build` and `Last-CI-build` tags advanced on October 24; retain a
  separate dated profile if the update is wanted.

### Best next additions using the existing image approach

These priorities are engineering recommendations based on artifact availability,
target coverage and likely consumer work. Modern cross-compilers add useful
coverage, but do not establish matching output for historical vendor builds.
Suggested profile names below are proposals, not registered IDs.

| Priority | Candidate and primary evidence | Concrete ingestion path and qualification |
| --- | --- | --- |
| High | **MSVC 12.0 Update 4** — [open decomp.me PR 82](https://github.com/decompme/compilers/pull/82), [preserved release](https://github.com/heinermann/compilers/releases/tag/msvc12) | A real `msvc12.zip` asset exists, 178,466,409 bytes, with a published SHA-256. Add `msvc-12.0-u4` alongside the 11.0 line using the existing MSVC image pattern. Inspect compiler banners, x86/amd64 layout, headers and companion runtime DLLs; qualify Wibo/Wine behavior and COFF output, external calls and optimized C/C++. PR status alone is not a blocker to independently qualifying the pinned source, and is not proof that it works. |
| High | **DJGPP GCC 12.2.0**, build-djgpp v3.4 — [release](https://github.com/andrewwutw/build-djgpp/releases/tag/v3.4), [build sources](https://github.com/andrewwutw/build-djgpp/tree/v3.4) | Native Linux x86-64 cross-compiler for DOS, so compilation needs no DOS emulator. Downloaded and hashed the 80,596,981-byte archive; it contains `djgpp/bin/i586-pc-msdosdjgpp-gcc` and matching assembler. Add a distinct `djgpp-12.2.0` image, preserve GCC/binutils/library notices and source references, and test GNU COFF symbol extraction and relocations through our actual parser. This is a modern DOS baseline; old DOS games may need earlier compiler versions, separately pinned. |
| Medium | **PSPDEV v20261001** — [dated release](https://github.com/pspdev/pspdev/releases/tag/v20261001) | A Debian Linux archive is available with an asset digest. Package the exact dated SDK and expose its PSP compiler; record the contained GCC/binutils versions rather than naming the SDK date as a GCC version. Check the host glibc floor, driver paths, MIPS/Allegrex flags, libraries and ELF relocations. This complements historical `psp-gcc-1.3.1`, MWCCPSP and SNC profiles. |
| Medium | **PS2DEV v2.0.0** — [release](https://github.com/ps2dev/ps2dev/releases/tag/v2.0.0) | Package the pinned Linux archive and expose EE and IOP compilers as separate profiles sharing the source pin. Verify host compatibility, both target architectures, runtime libraries and relocations. The Ubuntu asset name contains `latest` but the URL's release tag is `v2.0.0`; use that tag plus the verified hash. This complements the archived EE/IOP compiler versions. |
| Medium | **Bootlin cross-toolchains**, stable 2026.08-1 — [catalog](https://toolchains.bootlin.com/), [m68k example](https://toolchains.bootlin.com/releases_m68k-68xxx.html) | Good source for Linux firmware targets such as ARM, MIPS, RISC-V and m68k. Each target/libc/release has a versioned archive, checksum, component sources and license information. Start with one required target and libc; retain its sysroot, relocation script and component versions. The inspected m68k stable bundle uses GCC 15.3.0 and binutils 2.45.1. Linux ABI profiles need separate names from bare-metal or console compilers. |
| Medium | **m68k-atari-mintelf GCC 15.2.0** — [maintainer's packages and build scripts](https://tho-otto.de/crossmint.php) | Useful Atari/m68k coverage. The page offers Linux x86-64 packages, patches and scripts, with both a.out and ELF toolchain variants. Prefer an explicit `mintelf` profile for the current ELF pipeline; also pin binutils and the MiNT patches. Check host dependencies, calling conventions and m68k relocation handling. Legacy a.out needs a separate reader/converter decision. Package filenames alone are not immutable version guarantees. |
| Small follow-up | **Saturn native64 v1.0.0** — [existing upstream release](https://github.com/sozud/saturn-compiler-repro/releases/tag/v1.0.0) | The 814,948-byte `cc1-native64.tar.gz` asset is already known and absent locally. Reuse the existing native Saturn pipeline as a separate variant, then compare instructions, globals, relocations and padding against native32 and DOS. This broadens host execution, not historical compiler-version coverage. |

### Candidates needing consumer or licensing work first

| Candidate | Verified source and scope | Work before calling it a supported toolchain |
| --- | --- | --- |
| **LLVM-MOS SDK v23.3.0** | [Tagged Linux release](https://github.com/llvm-mos/llvm-mos-sdk/releases/tag/v23.3.0), with C/C++ compilers and libraries for 6502-family systems including C64 and NES. | A pinned native image is straightforward, but [MOS ELF](https://www.llvm-mos.org/wiki/ELF_specification) has a distinct machine type and 8/16/24-bit relocations. Qualify LIEF parsing, symbols, disassembly and relocation widths before enabling matching. Start with one explicit platform profile and retain LLVM/component notices. |
| **SDCC 4.6.0** | [Official release announcement](https://sdcc.sourceforge.net/) dated June 22, with a [Linux amd64 archive](https://sourceforge.net/projects/sdcc/files/sdcc-linux-amd64/4.6.0/). Covers SM83, Z80, STM8, 8051 and other small targets. | Pin each selected target separately. The ASxxxx object and linker pipeline needs symbol/section/relocation support rather than the current generic ELF/COFF route. Preserve component licenses; acquire and verify the release archive hash before ingestion. |
| **GBDK-2020 4.5.0** | [Release](https://github.com/gbdk-2020/gbdk-2020/releases/tag/4.5.0), bundled SDCC and platform libraries; downloaded and verified the 6,870,728-byte Linux x64 archive. | Useful Game Boy/SM83 and Sega/Z80 coverage. Its bundled `.o` files contain ASxxxx ASCII records: an inspected `crt0.o` starts `XL4`, not ELF/COFF magic. The [toolchain docs](https://gbdk.org/docs/api/docs_toolchain.html) support `lcc -c -o output.o`; the file extension does not imply parser support. Retain the license inventory, including SDCC and the LCC driver terms. Record the bundled SDCC build independently from standalone SDCC 4.6.0. |
| **cc65 V2.19** | [Tagged source release](https://github.com/cc65/cc65/releases/tag/V2.19), zlib license; [ca65 documentation](https://cc65.github.io/doc/ca65.html). | Build a hash-pinned source archive and use `cl65` for the full C-to-object pipeline. ca65 has its own relocatable object format, so add a tested reader/converter and 6502 matching support. The old stable tag and current master are different choices; record a commit for any newer snapshot. |
| **z88dk v2.4** | [Release](https://github.com/z88dk/z88dk/releases/tag/v2.4), a source tarball with a published digest; includes sccz80 and customized SDCC frontends. | Build the release source inside the image, pin all fetched dependencies and distinguish the two code generators. Qualify z80asm object symbols/relocations and selected CPU/target modes. Retain the distribution's multiple licenses; a generic `.o` suffix is insufficient. |
| **Amsterdam Compiler Kit 6.2+** | [Maintainer's README](https://github.com/davidgiven/ack/blob/default/README) identifies C, Pascal, Modula-2 and BASIC, with DOS, Linux and other targets; BSD-style project terms. | Pin a source commit and build a selected target. The README explicitly identifies ACK's private `.o` format. Add object conversion or parsing before consumer matching; do not ingest the mutable `dev` release as a versioned stable compiler. |
| **VBCC / VASM / VLINK** | [Author's download page](http://www.compilers.de/vbcc.html), Linux x64 multi-target binary archive and January 10, 2026 compiler sources. Covers m68k, PowerPC, 6502/65816 and other targets. | The source manual's Legal section restricts general commercial use and lists specific target exceptions. Review the exact compiler, assembler, linker and library terms before use in this product. Preserve the unmodified inputs and their hashes; select ELF where available, and qualify Hunk/other formats separately. Do not classify the whole suite as permissively licensed. |
| **IA-16 GCC** | [Maintainer's build scripts](https://codeberg.org/tkchia/build-ia16), [segmented ELF design](https://codeberg.org/tkchia/build-ia16/src/branch/master/elf16-writeup.md). Native Linux compiler produces 16-bit x86 code. | Pin GCC, binutils, libi86 and build-script commits, avoiding a moving PPA-only installation. Qualify far pointers, memory models and segment relocations. This is separate from a generic 32-bit x86 ELF profile and from Microsoft OMF. |
| **Retro68** | [Maintainer's project](https://github.com/autc04/Retro68), GCC-based Classic Mac 68k/PowerPC cross-tools. Current source has changed substantially since its 2019 tagged release. | Pin the complete source/submodule graph and select one target. Prefer the included open Multiversal Interfaces where sufficient; upstream says Apple's Universal Interfaces are not included because their license does not permit redistribution. Qualify target object format, resource packaging and relocation handling. A modern GCC port does not reproduce MPW or Metrowerks code generation. |
| **devkitARM / devkitPPC / devkitA64** | [devkitPro build scripts](https://github.com/devkitPro/buildscripts) and package repositories provide maintained console homebrew toolchains. | Worth a targeted follow-up for GBA/DS, GameCube/Wii or Switch homebrew. Select an exact compiler release and freeze every package/source input; the repository's latest release is devkitA64 r29.1, which does not identify the current ARM/PPC packages. No exact ingestible package set was qualified in this audit. |
| **QuickC 2.50** | [decomp.me issue 1350](https://github.com/decompme/decomp.me/issues/1350) documents a concrete real-mode DOS matching need. | Useful historical coverage, but the issue links third-party installation media rather than a qualified compiler package. Verify media provenance, compiler binaries, extraction and terms first; then reuse DOS emulation and test OMF output/memory models. This remains a research lead, not an approved source pin. |

### Concrete candidate pins

The [evidence JSON](toolchain-audit-2026-10-25.json) contains full download
URLs, sizes and SHA-256 values for eight candidate archives: MSVC 12.0u4,
DJGPP, PSPDEV, PS2DEV, Bootlin m68k, LLVM-MOS, GBDK and z88dk.

DJGPP was downloaded and independently hashed as
`8464f17017d6ab1b2bb2df4ed82357b5bf692e6e2b7fee37e315638f3d505f00`;
its old GitHub release publishes no asset digest, so this is a local download
hash, not independent upstream attestation. GBDK's downloaded bytes match
the published digest
`d7857a5f6d135ee4c249043ca26aad9f2ec8ab5d4106d97720d404114f42605c`.
The other candidate hashes came from release metadata or the upstream
checksum file; their complete archives were not downloaded and rehashed.
No candidate compiler was executed or installed as a profile.

For each selected addition, finish the existing ingestion contract:
`sources.json` recipe and provenance; generated Dockerfile/entrypoint;
preserved component notices; Rebrew registry and measured smoke golden;
Recompile resolution; then parser/relocation tests if the target or object
format is new. Preserve separate compiler/runtime variants and existing
aliases. Linking to a website or recognizing the output suffix is not proof
of usable byte-matching support.

### Checks actually run

- All 607 generated files and generated catalog/provenance docs are current.
  Lint, type checks, wrapper helper tests and 29 catalog unit tests passed.
- Rebrew's 125 toolchain tests passed. All 27 maspsx/Daze profiles passed
  their existing measured smoke goldens again, using already-built local
  images; this does not validate a cold image build.
- All 452 pinned URL checks completed: 450 passed and the two DOSEMU URLs
  returned 404. Availability checks do not rehash archive contents.
- Published primary-asset digests matched 71 manifest profiles spanning
  44 distinct assets from the inspected GitHub releases. This is a metadata
  comparison, not a download-integrity sweep of every archive or helper.
- Recompile was checked against the source Rebrew registry for every
  canonical catalog name; the 230 missing names and two image differences
  are listed in the evidence JSON.

This audit changes documentation only. No recipes, pins, consumer registrations
or image tags were changed, and no full 308-image rebuild was attempted.

## Ingestion and repairs — 2026-10-25

The follow-up adds **27 profiles**, bringing the catalog to **335 profiles
across 46 families**. Rebrew now packages all 335 canonical names, the exact
catalog image tags and their entrypoints, and a measured smoke fixture for
each. That closes the original 230-name gap and adds all 27 new profiles.
The five KVM-dependent originals run through local Rebrew; Recompile's
container runners support the other 330 names without exposing host devices.
Availability still depends on building or admitting the corresponding image.

The earlier audit above is a historical baseline. This section and the
[qualification receipt](toolchain-qualification-2026-10-25.json) describe the
resulting implementation, including its limits.

### Added profiles

| Source | New canonical profiles | Output and integration |
| --- | --- | --- |
| [Preserved VC 2013 Update 4](https://github.com/heinermann/compilers/releases/tag/msvc12) | `msvc-12.0-u4` | i386 COFF; native MSVCR120/MSVCP120 DLLs and header/library paths included. Optimized C/C++ with STL and stdio qualifies under Wine. Wibo's C++ runtime still lacks `RtlCreateUnicodeString`; use Wine. |
| [build-djgpp](https://github.com/andrewwutw/build-djgpp/releases) | `djgpp-12.2.0` | Linux-hosted DOS GCC, GNU i386 COFF; function extraction works. |
| [PSPDEV](https://github.com/pspdev/pspdev/releases/tag/v20261001) | `pspdev-20261001` | Complete dated SDK, MIPS ELF. |
| [PS2DEV](https://github.com/ps2dev/ps2dev/releases/tag/v2.0.0) | `ps2dev-2.0.0-ee`, `ps2dev-2.0.0-iop` | Distinct EE/IOP drivers from the same pinned SDK; MIPS ELF. |
| [Bootlin](https://toolchains.bootlin.com/releases_m68k-68xxx.html) | `bootlin-m68k-glibc-2026.08-1` | Relocated Linux m68k SDK, GCC 15.3.0/binutils 2.45.1 with glibc sysroot. |
| [MiNT cross tools](https://tho-otto.de/crossmint.php) | `mintelf-gcc-15.2.0` | Pinned GCC 15.2.0, binutils 2.45 and mintlib package revisions; MiNT ELF. |
| [LLVM-MOS SDK](https://github.com/llvm-mos/llvm-mos-sdk/releases/tag/v23.3.0) | `llvm-mos-23.3.0-c64`, `llvm-mos-23.3.0-nes` | Target-specific configurations; `-fno-lto` ensures MOS ELF rather than default LLVM bitcode. Compilation only; matching refuses unsupported relocation widths. |
| [GBDK](https://github.com/gbdk-2020/gbdk-2020/releases/tag/4.5.0) | `gbdk-4.5.0-sm83` | Bundled SDCC and Game Boy libraries; native ASxxxx object output. |
| [SDCC](https://sourceforge.net/projects/sdcc/files/sdcc-linux-amd64/4.6.0/) | `sdcc-4.6.0-sm83`, `sdcc-4.6.0-z80`, `sdcc-4.6.0-stm8`, `sdcc-4.6.0-8051` | Native ASxxxx `.rel` output; STM8 does not honor an `.o` output suffix, so all four profiles declare `.rel`. |
| [cc65](https://github.com/cc65/cc65/releases/tag/V2.19) | `cc65-2.19-c64` | Builds the V2.19 source tag; its tools identify as 2.18. Native xo65 object; translation time and temporary assembly mtime are masked only in smoke metadata. |
| [z88dk](https://github.com/z88dk/z88dk/releases/tag/v2.4) | `z88dk-2.4-sccz80` | Complete dependency-bearing source archive, sccz80 frontend; native `Z80RMF18` object. |
| [ACK](https://github.com/davidgiven/ack/commit/7afa32a0a0f13e865fa2e8104e442689005cd627) | `ack-6.2-7afa32a-linux386` | Source-built linux386 target; native ACK object format. |
| [IA-16](https://launchpad.net/~tkchia/+archive/ubuntu/build-ia16) | `ia16-gcc-6.3.0-20260612` | Exact GCC, binutils, newlib and libi86 packages; segmented 16-bit x86 ELF. |
| [Retro68](https://github.com/autc04/Retro68/commit/0cbd3cb918a127a0d30a675b337f8f8e15062786) | `retro68-16.0.0-0cbd3cb-m68k` | Source-built m68k compiler with pinned open Multiversal Interfaces; Apple Universal Interfaces are excluded. Component notices retained. |
| [devkitPro packages](https://devkitpro.org/wiki/devkitPro_pacman) | `devkitarm-16.1.0-1`, `devkita64-16.1.0-1`, `devkitppc-16.2.0-1` | Pin the split GCC/binutils/newlib/rules/CRT packages together. Use the official repository's recorded SHA-256 values, checked again after download. The base image's curl receives HTTP 403; a standard-library HTTPS client succeeds. |
| [QuickC media](https://winworldpc.com/product/quick-c/2x) | `quickc-2.50` | Original eight floppy images retained. Pinned libmspack frontend expands QBasic SZDD files; QCL and headers run under DOSBox, producing 16-bit OMF. |
| [VBCC preservation mirror](https://github.com/erique/vbcc_vasm_vlink/commit/647720b664c0599a4b5b28b3232987673615fe11) | `vbcc-0.9h-p2-amiga` | Builds VBCC 0.9h p2, VASM 2.0d and VLINK 0.18a with Amiga target p3. Original archives and component terms retained; native Amiga Hunk object. The current official Linux bundle has no working HTTPS endpoint here, so this profile names the qualified archived version explicitly. |
| [Saturn native64 reproduction](https://github.com/sozud/saturn-compiler-repro/releases/tag/v1.0.0) | `saturn-cygnus-2.7-96Q3-native64` | Separately pinned x86-64 host reproduction. Code/data and relocation parity with native32 checked on add, loop and global-data fixtures. |
| [Open Watcom October snapshot](https://github.com/open-watcom/open-watcom-v2/releases/tag/2026-10-01-Build) | `watcom-2.0-20261001-win16`, `watcom-2.0-20261001-win32` | Separate dated profiles; September remains selectable. |

### Repairs applied

- Replace the two deleted FDPP runtime downloads with versioned, verified
  packages from the same PPA; rebuild the DOSEMU base and its five profiles.
- Both builders now follow the selected image's complete local base chain.
  Native builds no longer require the unrelated DOS runtime to build.
- Add POSIX `-c ... -o ...` ELF adapters for five AGBCC frontends, eleven SHC
  versions and PSY-Q 4.6. Invocations without `-c` retain the original raw
  compiler behavior. Stages keep watchdogs; failed compiles preserve an
  existing destination, relative include paths resolve from the caller's
  directory, and source/output aliasing is rejected.
- Copy complete SHC support directories, including nested include trees.
  Keep each compiler's own flags and target mode.
- Replace PSY-Q 2.6.3's bundled old converter with a source-built
  [PCSX-Redux converter](https://github.com/grumpycoders/pcsx-redux/commit/c2edcc4c0d3d1ac573c95b8be5349dd8fbdbf0c2)
  and exact submodule pins. The former relocation-30 fixture now compiles
  under both DOSEMU and Daze with matching code/data and relocations.
  NOBITS sections are compared by size, not by nonexistent file bytes.
- Mark single-source pipelines explicitly so batch dispatch cannot silently
  discard translation units. Add KVM only for local DOSEMU runs. Smoke
  compilation never pulls an image implicitly.
- Align canonical IDO 5.3/7.1 image names with the manifest. Their `-n64` and
  explicit `-linux` recipes use the same payload; this was a tag mismatch,
  not a native-versus-IRIX compiler choice. The IRIX profile remains separate.
- Correct MSVC 7.0's stale 7.1 source description/pin and golden to the true
  13.00.9466 compiler its image already builds. The explicit 7.1 profile
  remains available for 13.10.3077 output.
- Correct Turbo C 2.0's timestamp mask to all four bytes of its OMF E9
  timestamp plus that record's checksum. The old mask covered part of the
  record header and left half the date unmasked.
- Refresh Delphi's stale smoke hash for the preserved module name. A
  `SRC.DPR` control reproduces the previous hash exactly; `t.dpr` produces
  module `T`, with all three executable segments byte-identical.
- Use `-pipe` for the papermario GCC 2.8.1 profile so a random assembly
  temporary filename does not enter `.mdebug`.
- Preserve ARM Thumb entry markers, exact ELF function sizes and assembler
  local-label boundaries during symbol extraction. Recognize Xbox 360
  PowerPC COFF objects through the LIEF path.
- Recompile captures `.rel` artifacts and reports versionless image tags as
  `unversioned`, instead of emitting an empty compiler version. Catalog
  tests accept the wider target set. Release guards now recognize the
  already-pinned Rebrew 6 public wheel.

### Matching and release limits

Eleven new profiles are **compilation only** in Rebrew: the two LLVM-MOS
profiles, GBDK, four SDCC targets, cc65, z88dk, ACK and VBCC. ASxxxx, xo65,
Z80RMF, ACK and Amiga Hunk require native readers; pretending these objects
are ELF would discard their actual relocations. MOS additionally needs a
scorer that represents its one-, two- and three-byte fixups.

Leaf functions from m68k and IA-16 ELF can be extracted. Relocation-bearing
m68k functions with widths unavailable from LIEF, and 16-bit x86 fixups,
are refused by the current four-byte matcher. Signature generation also
refuses unknown m68k fixup widths. Native Saturn profiles retain the GNU
assembler's trailing NOP difference from the DOS assembler; the variants
are not aliases. Daze's software backend still has the previously measured
large-input performance limit.

The SHC ROF converter gists still have no verified declared licence; their
provenance is now recorded as unresolved rather than incorrectly classified
as MIT. VBCC/VASM/VLINK's original terms are retained and include actual
commercial-use/redistribution restrictions. This work builds local images
and source changes; it does not publish compiler payloads or deploy a new
Rebrew/Recompile release. Recompile's normal dependency remains the pinned
public Rebrew wheel; source-integration checks select this checkout explicitly.

### Qualification completed

All **335 profiles** passed their measured smoke fixture twice using local
images and `--pull=never`. Only each fixture's recorded timestamp metadata
is masked; the receipt records the image ID and object hash for every run.
All 27 new profiles also compiled optimized external-call and global-data
fixtures; VBCC additionally compiled its stdio header fixture. PSY-Q
2.6.3 DOSEMU/Daze and Saturn native32/native64 passed code, data, relocation
and NOBITS-size comparisons across three fixtures each.

The toolchain repository's lint, type checks, generated-file checks, wrapper
harness and **33 unit tests** pass. Rebrew's compiler/parser tests, type
checks and layering check pass. Recompile's full source-integration suite
passes with **1,397 passed, two skipped**; its type check covers 49 modules.
These are local source-integration results; no public dependency or deployed
service was updated.

### Release integration

This qualified catalog ships as **toolchains 1.7.0**, with the complete
packaged registry in **Rebrew 6.1.0** and its consumer in **Recompile 7.3.0**.
The release integration retains main's rootless archive safeguards, applies
those flags to the nested VBCC and devkitPro archives, and rebuilds and
smokes those four profiles twice. The migration verifier admits only exact
fingerprints for the reviewed pipeline/access repairs; an unrelated later
recipe or wrapper edit still fails it.

The final catalog suite has **36 passing tests**; migration verification
compares 272 original profiles, identifies 63 additions and admits 25
reviewed changes with no unexpected differences. Rebrew's full integration
suite passes **13,142 tests**, with 32 environment-dependent skips. The
original qualification results and image identities above remain a dated
receipt; the JSON's `release_integration` section records these later checks.
