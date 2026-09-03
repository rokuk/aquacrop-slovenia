"""
Runtime patches for known bugs in the installed ``pyaquacrop`` package
(import name ``aquacrop``, version pinned via pyproject.toml).

Bug: ``aquacrop.file_generators.DATA.gwt_generator.generate_groundwater_file``
is missing a blank-line separator between the groundwater-type line and the
"Day Depth (m) ECw (dS/m)" observations table when ``groundwater_type == 1``
(fixed depth table). The blank line is only appended as part of the
``groundwater_type == 2`` date block, but AquaCrop's file format expects it
for type 1 as well. Without it, the generated .GWT file is malformed and the
AquaCrop executable fails to parse it correctly.

This module has no public API - importing it (see
``aquacrop_slovenia/__init__.py``) monkeypatches a corrected version of the
function into place everywhere it is used.
"""
import os

from aquacrop.constants import Constants
from aquacrop.entities import ground_water
from aquacrop.file_generators.DATA import gwt_generator


def _generate_groundwater_file_patched(
    file_path,
    description,
    groundwater_type=0,
    first_day=1,
    first_month=1,
    first_year=1901,
    groundwater_observations=None,
):
    if groundwater_observations is None:
        groundwater_observations = []

    lines = [
        f"{description}",
        f" {Constants.AQUACROP_VERSION_NUMBER} : AquaCrop Version ({Constants.AQUACROP_VERSION_DATE})",
        f" {groundwater_type} : {gwt_generator._get_groundwater_type_description(groundwater_type)}",
    ]

    if groundwater_type == 0:  # No groundwater table
        pass

    elif groundwater_type in (1, 2):  # Fixed or variable groundwater table
        if groundwater_type == 2:
            lines.extend([
                f" {first_day} : first day of observations",
                f" {first_month} : first month of observations",
                f" {first_year} : first year of observations {gwt_generator._get_year_description(first_year)}",
            ])

        # Fix: AquaCrop's file format expects a blank line separating the
        # header info from the observations table for BOTH type 1 and
        # type 2 - the original code only ever added it as part of the
        # type == 2 date block above, leaving type 1 files missing it.
        lines.append("")

        lines.extend([
            " Day Depth (m) ECw (dS/m)",
            "====================================",
        ])

        for observation in groundwater_observations:
            lines.append(f" {observation['day']} {observation['depth']:.2f} {observation['ec']:.1f}")

    content = "\n".join(lines)

    if file_path:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)

    return file_path


# Patch every name the buggy function is bound to: the defining module and
# aquacrop.entities.ground_water, which imported it by value with `from ... import`.
gwt_generator.generate_groundwater_file = _generate_groundwater_file_patched
ground_water.generate_groundwater_file = _generate_groundwater_file_patched
