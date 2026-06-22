from aquacrop import SoilLayer, GroundWater, FieldManagement, InitialConditions

rakican_maize_params = {
    # Basic classifications
    "crop_type": 2,  # forage crop
    "is_sown": True,
    "cycle_determination": 0,  # by growing degree-days
    "adjust_for_eto": True,
    # Temperature parameters
    "base_temp": 8.0,
    "upper_temp": 30.0,
    "gdd_cycle_length": 1466,
    "dormancy_eto_threshold": 50,
    # Crop water stress parameters
    "p_upper_canopy": 0.14,
    "p_lower_canopy": 0.72,
    "shape_canopy": 2.9,
    "p_upper_stomata": 0.69,
    "shape_stomata": 6.0,
    "p_upper_senescence": 0.69,
    "shape_senescence": 2.7,
    "p_upper_pollination": 0.80,
    "aeration_stress_threshold": 5,
    # Soil fertility stress parameters
    "fertility_stress_calibration": 50,
    "shape_fertility_canopy_expansion": 25,
    "shape_fertility_max_canopy": 25,
    "shape_fertility_water_productivity": 25,
    "shape_fertility_decline": 25,
    # Temperature stress parameters
    "cold_stress_for_pollination": 10,
    "heat_stress_for_pollination": 40,
    "minimum_growing_degrees_pollination": 12.0,
    # Salinity stress parameters
    "salinity_threshold_ece": 2,
    "salinity_max_ece": 10,
    "salinity_shape_factor": -9,
    "salinity_stress_cc": 25,
    "salinity_stress_stomata": 100,
    # Transpiration parameters
    "kc_max": 1.05,
    "kc_decline": 0.300,
    # Rooting parameters
    "min_rooting_depth": 0.30,
    "max_rooting_depth": 2.30,
    "root_expansion_shape": 13,
    "max_water_extraction_top": 0.045,
    "max_water_extraction_bottom": 0.011,
    "soil_evaporation_reduction": 50,
    # Canopy development parameters
    "canopy_cover_per_seedling": 6.50,
    "canopy_regrowth_size": 6.50,
    "plant_density": 85900,
    "max_canopy_cover": 0.90,
    "canopy_growth_coefficient": 0.16312,
    "canopy_thinning_years": -9,
    "canopy_thinning_shape": -9,
    "canopy_decline_coefficient": 0.11691,
    # Crop cycle parameters (Calendar days)
    "days_emergence": 6,
    "days_max_rooting": 108,
    "days_senescence": 107,
    "days_maturity": 132,
    "days_flowering": 66,
    "days_flowering_length": 13,
    "days_crop_determinancy": 1,
    "days_hi_start": 61,
    # Crop cycle parameters (Growing degree days)
    "gdd_emergence": 38,
    "gdd_max_rooting": 1207,
    "gdd_senescence": 1193,
    "gdd_maturity": 1466,
    "gdd_flowering": 660,
    "gdd_flowering_length": 164,
    "cgc_gdd": 0.012494,
    "cdc_gdd": 0.010000,
    "gdd_hi_start": 595,
    # Biomass and yield parameters
    "water_productivity": 33.7,
    "water_productivity_yield_formation": 100,
    "co2_response_strength": 50,
    "harvest_index": 0.51, # Povprecje na podlagi meritev biomase in zrnja za Rakican A-N1,2,3
    "water_stress_hi_increase": 0,
    "veg_growth_impact_hi": 7.0,
    "stomatal_closure_impact_hi": 3.0,
    "max_hi_increase": 15,
    "dry_matter_content": 83,  # Na podlagi meritev v tabelah KIS FAO300 Rakican 2024
    # Perennial crop parameters
    "is_perennial": False,
    "first_year_min_rooting": 0.00,
    "assimilate_transfer": 0,
    "assimilate_storage_days": 0,
    "assimilate_transfer_percent": 0,
    "root_to_shoot_transfer_percent": 0,
    # Crop calendar for perennials - dummy values not used
    "restart_type": 0,
    "restart_window_day": 0,
    "restart_window_month": 0,
    "restart_window_length": 0,
    "restart_gdd_threshold": 0,
    "restart_days_required": 0,
    "restart_occurrences": 0,
    "end_type": 0,
    "end_window_day": 0,
    "end_window_month": 0,
    "end_window_years_offset": 0,
    "end_window_length": 0,
    "end_gdd_threshold": 0,
    "end_days_required": 0,
    "end_occurrences": 0,
}

rakican_soil_layers = [ # FC in WP na podlagi zbornika, ocena gravel na podlagi opisa KIS
    SoilLayer(
        thickness=1,
        sat=38.0,
        fc=21.7,
        wp=9.3,
        ksat=2200.0,
        penetrability=100,
        gravel=0,
        cra=-0.333200,
        crb=0.365805,
        description="loamy sand",
    ),
    SoilLayer(
        thickness=0.5,
        sat=38.0,
        fc=21.7,
        wp=9.3,
        ksat=2200.0,
        penetrability=100,
        gravel=20,
        cra=-0.333200,
        crb=0.365805,
        description="loamy sand",
    ),
    SoilLayer(
        thickness=0.5,
        sat=38.0,
        fc=21.7,
        wp=9.3,
        ksat=2200.0,
        penetrability=100,
        gravel=50,
        cra=-0.333200,
        crb=0.365805,
        description="loamy sand",
    ),
    SoilLayer(
        thickness=0.1,
        sat=0.5,
        fc=0.3,
        wp=0.1,
        ksat=0.0,
        penetrability=0,
        gravel=0,
        cra=-9.0,
        crb=9.0,
        description="impermeable",
    )
]

rakican_soil_layers_old = [
    SoilLayer(
        thickness=0.6,
        sat=38.0,
        fc=16.0,
        wp=8.0,
        ksat=2200.0,
        penetrability=100,
        gravel=0,
        cra=-0.333200,
        crb=0.365805,
        description="loamy sand",
    ),
    SoilLayer(
        thickness=0.4,
        sat=38.0,
        fc=16.0,
        wp=8.0,
        ksat=2200.0,
        penetrability=100,
        gravel=10,
        cra=-0.333200,
        crb=0.365805,
        description="loamy sand",
    ),
    SoilLayer(
        thickness=0.5,
        sat=38.0,
        fc=16.0,
        wp=8.0,
        ksat=2200.0,
        penetrability=100,
        gravel=50,
        cra=-0.333200,
        crb=0.365805,
        description="loamy sand",
    ),
    SoilLayer(
        thickness=1,
        sat=0.5,
        fc=0.3,
        wp=0.1,
        ksat=0.0,
        penetrability=0,
        gravel=0,
        cra=-9.0,
        crb=9.0,
        description="impermeable",
    )
]

rakican_soil_layers_podrobno = [
    SoilLayer(
        thickness=0.22,
        sat=50.0,
        fc=33.8,
        wp=26.8,
        ksat=35.0,
        penetrability=100,
        gravel=0,
        cra=-0.569100,
        crb=-1.613423,
        description="loamy sand",
    ),
    SoilLayer(
        thickness=0.15,
        sat=38.0,
        fc=30.3,
        wp=25.8,
        ksat=2200.0,
        penetrability=100,
        gravel=0,
        cra=-0.655700,
        crb=0.838797,
        description="loamy sand",
    ),
    SoilLayer(
        thickness=0.25,
        sat=50.0,
        fc=30.5,
        wp=22.9,
        ksat=125.0,
        penetrability=100,
        gravel=0,
        cra=-0.572700,
        crb=-0.859573,
        description="loamy sand",
    ),
    SoilLayer(
        thickness=0.88,
        sat=50.0,
        fc=32.7,
        wp=23.9,
        ksat=125.0,
        penetrability=100,
        gravel=50,
        cra=-0.572700,
        crb=-0.859573,
        description="loamy sand",
    ),
    SoilLayer(
        thickness=1,
        sat=0.5,
        fc=0.3,
        wp=0.1,
        ksat=0.0,
        penetrability=0,
        gravel=0,
        cra=-9.0,
        crb=9.0,
        description="impermeable",
    )
]

rakican_curve_number = 46

rakican_readily_evaporable_water = 7

rakican_groundwater = GroundWater(
    name="DeepGroundwater",
    description="Fixed deep groundwater table at given depth",
    params={
        'groundwater_type': 1,  # Fixed groundwater table
        'groundwater_observations': [
            {'day': 1, 'depth': 1.8, 'ec': 0.0}
        ]
    }
)

rakican_optimal_management = FieldManagement(
    name="Optimal Field Management",
    description="Optimal field management with no fertility stress, runoff adjustment for row crops",
    params={
        "fertility_stress": 0,
        "mulch_cover": 0,
        "mulch_effect": 50,
        "bund_height": 0.00,
        "surface_runoff_affected": 0,
        "runoff_adjustment": 20,
        "weed_cover_initial": 0,
        "weed_cover_increase": 0,
        "weed_shape_factor": 100.00,
        "weed_replacement": 100,
        "multiple_cuttings": False,
    },
)

rakican_initial_cond = InitialConditions(
    name="FieldCapacityInitial Rakican",
    description="Initial soil water content at field capacity",
    params = {
        "initial_canopy_cover": -9.00,  # Default calculated by AquaCrop
        "initial_biomass": 0.000,
        "initial_rooting_depth": -9.00,  # Default calculated by AquaCrop
        "water_layer": 0.0,
        "water_layer_ec": 0.00,
        "soil_water_content_type": 0,  # For specific layers
        "soil_data": [
            {'thickness': 1.0, 'water_content': 21.7, 'ec': 0.00},
            {'thickness': 0.5, 'water_content': 21.7, 'ec': 0.00},
            {'thickness': 0.5, 'water_content': 21.7, 'ec': 0.00},
        ]
    }
)