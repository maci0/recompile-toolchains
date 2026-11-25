# Release readiness for 1.19.2

On 2026-11-25, all 21 compiler profiles whose generated recipes or wrappers differed from the accepted migration baseline compiled a test source. The object inspection in `tests/check_images.py` agreed with the catalog architecture and width for all 21. The four SN0001 and SN0006 C and C++ images ran as their default user and produced 32-bit big-endian MIPS objects after the compiler directory permissions were corrected.

With uv 0.13.6, `make lint test verify` passed, including 120 Python tests and the wrapper regression suite. The migration verifier compared 272 profiles against 07a7268, found 63 new profiles and accepted 47 recorded changes by their checks. Zero differences remained. The catalog passed `sha256sum -c toolchains.json.sha256` with SHA-256 `5df24837811e3d5c0d22fb3925ca09af3fd34c162f333609b2af3f8a0678643c`.

The source release publishes the recipes. Hosted runner image installation is a separate deployment. The local image checks covered the 21 affected profiles. The weekly download-pin sweep keeps its normal schedule.
