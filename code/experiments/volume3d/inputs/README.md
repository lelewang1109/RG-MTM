# Pinned public input metadata

`tangaroa_archive_inventory.json` is the exact ZIP directory used for the
verified 201-frame run. It describes all official Amira members (names, byte
offsets, lengths and CRC32); it contains no raw volume or login/session data.
`setup_inputs.py` copies it to the ignored acquisition directory on a fresh
checkout. Every acquired member must still pass its header, length and CRC32
checks; if the remote archive changes, acquisition fails rather than silently
using a different version. Official source and archive size are in the JSON.

`tangaroa_closer_camera.json` records camera numbers extracted from the public
TMTM workspace at the stated commit, with the original workspace SHA256. The
paper-style renderer needs no local clone or temporary XML file. Transfer
function and preprocessing evidence remain in the saved input-audit report.

These are descriptive reproduction inputs. The TTK and TMTM source archives,
raw velocity volumes and full generated arrays are not distributed here.
