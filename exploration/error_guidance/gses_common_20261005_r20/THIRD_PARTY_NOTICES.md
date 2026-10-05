# Third-party source identity

Improved GSES / STPG: original author repository and commit are pinned by `valid_nominal_schedule/PHASE1_REGISTRATION.json` and the existing R13 `AUTHOR_SOURCE.json`; commit `25fb931eff03f1cce23a22a68ab42b7533f85ab3`. `STPG_LICENSE` is copied unchanged from that checkout's MIT LICENSE. Its unchanged source archive is already retained in `../gses_online_adoption_20261004_r13/AUTHOR_SOURCES.tar.gz`; this round does not duplicate the archive or redistribute the ELF. The wrapper ELF path/hash and original wrapper source hash are in every native registration/receipt.

The inherited event executor and graph compiler depend on SADG controller, original commit `c2626d996121a9d6c128844a167b917db24418ac`, AGPL-3.0. The original source and license are retained by R16 under `../sadg_preflight_20261004_r16/`; the isolated compiler changes and R18/R19 execution provenance remain separately identified. No claim is made that the STPG MIT license replaces the inherited SADG dependency's license.

New files here are research adapter/audit code, with upstream components used under their original licenses. Author algorithm source files and old frozen artifacts were not modified.
