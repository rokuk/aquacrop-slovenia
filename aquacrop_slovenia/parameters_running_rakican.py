from aquacrop import SoilLayer, GroundWater, FieldManagement, InitialConditions

# Parameter version 2.0

rakican_maize_params = {
    # Basic classifications
    "crop_type": 2,  # forage crop
    "is_sown": True,
    "cycle_determination": 0,  # by growing degree-days
    "adjust_for_eto": True,
    # Temperature parameters
    "base_temp": 10.0,
    "upper_temp": 30.0,
    "gdd_cycle_length": 1152,
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
    "min_rooting_depth": 0.3,
    "max_rooting_depth": 1.5,
    "root_expansion_shape": 13,
    "max_water_extraction_top": 0.045,
    "max_water_extraction_bottom": 0.011,
    "soil_evaporation_reduction": 50,
    # Canopy development parameters
    "canopy_cover_per_seedling": 6.50,
    "canopy_regrowth_size": 6.50,
    "plant_density": 85900,
    "max_canopy_cover": 0.96,
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
    "gdd_emergence": 30,
    "gdd_max_rooting": 897,
    "gdd_senescence": 943,
    "gdd_maturity": 1065,
    "gdd_flowering": 530,
    "gdd_flowering_length": 186,
    "cgc_gdd": 0.01571,
    "cdc_gdd": 0.01323,
    "gdd_hi_start": 434,
    # Biomass and yield parameters
    "water_productivity": 33.7,
    "water_productivity_yield_formation": 100,
    "co2_response_strength": 50,
    "harvest_index": 0.48,
    "water_stress_hi_increase": 0,
    "veg_growth_impact_hi": 7.0,
    "stomatal_closure_impact_hi": 3.0,
    "max_hi_increase": 15,
    "dry_matter_content": 90,  # Na podlagi meritev v tabelah KIS FAO300 Rakican 2024
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

rakican_soil_layers = [
    SoilLayer(
        thickness=0.2,
        sat=38.0,
        fc=21.7,
        wp=9.3,
        ksat=2550.0,
        penetrability=100,
        gravel=3,
        cra=-0.333200,
        crb=0.365805,
        description="Ap1 0-20",
    ),
    SoilLayer(
        thickness=0.75,
        sat=38.0,
        fc=21.7,
        wp=9.3,
        ksat=170.0,
        penetrability=100,
        gravel=0,
        cra=-0.333200,
        crb=0.365805,
        description="Bg1 70-95",
    ),
    SoilLayer(
        thickness=0.55,
        sat=38.0,
        fc=21.7,
        wp=9.3,
        ksat=1190.0,
        penetrability=100,
        gravel=0,
        cra=-0.333200,
        crb=0.365805,
        description="Bg2 95-150",
    ),
    SoilLayer(
        thickness=0.8,
        sat=38.0,
        fc=21.7,
        wp=9.3,
        ksat=7500.0,
        penetrability=100,
        gravel=50,
        cra=-0.333200,
        crb=0.365805,
        description="I. Sp 150-230",
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

rakican_curve_number = 46

rakican_readily_evaporable_water = 7

rakican_groundwater = GroundWater(
    name="DeepGroundwater",
    description="Fixed deep groundwater table at given depth",
    params={
        'groundwater_type': 1,  # Fixed groundwater table
        'groundwater_observations': [
            {'day': 1, 'depth': 2.4, 'ec': 0.0}
        ]
    }
)

rakican_management = FieldManagement(
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