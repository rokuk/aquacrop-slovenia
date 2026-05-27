# Default management with no fertility stress, runoff ajusted for row crops
from aquacrop import FieldManagement

optimal_management = FieldManagement(
    name="Optimal Field Management",
    description="Optimal field management with no fertility stress",
    params={
        "fertility_stress": 0,
        "mulch_cover": 0,
        "mulch_effect": 50,
        "bund_height": 0.00,
        "surface_runoff_affected": 0,
        "runoff_adjustment": 10,
        "weed_cover_initial": 0,
        "weed_cover_increase": 0,
        "weed_shape_factor": 100.00,
        "weed_replacement": 100,
        "multiple_cuttings": False,
    },
)
