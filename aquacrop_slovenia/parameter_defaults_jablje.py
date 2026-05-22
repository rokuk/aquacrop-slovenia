from aquacrop import SoilLayer

jablje_maize_params = {
    # Basic classifications
    'crop_type': 2,  # forage crop
    'is_sown': True,
    'cycle_determination': 1,  # by growing degree-days
    'adjust_for_eto': True,

    # Temperature parameters
    'base_temp': 10.0,
    'upper_temp': 30.0,
    'gdd_cycle_length': 1700,
    'dormancy_eto_threshold': 50,

    # Crop water stress parameters
    'p_upper_canopy': 0.14,
    'p_lower_canopy': 0.72,
    'shape_canopy': 2.9,
    'p_upper_stomata': 0.69,
    'shape_stomata': 6.0,
    'p_upper_senescence': 0.69,
    'shape_senescence': 2.7,
    'p_upper_pollination': 0.80,
    'aeration_stress_threshold': 5,

    # Soil fertility stress parameters
    'fertility_stress_calibration': 50,
    'shape_fertility_canopy_expansion': 25,
    'shape_fertility_max_canopy': 25,
    'shape_fertility_water_productivity': 25,
    'shape_fertility_decline': 25,

    # Temperature stress parameters
    'cold_stress_for_pollination': 10,
    'heat_stress_for_pollination': 40,
    'minimum_growing_degrees_pollination': 12.0,

    # Salinity stress parameters
    'salinity_threshold_ece': 2,
    'salinity_max_ece': 10,
    'salinity_shape_factor': -9,
    'salinity_stress_cc': 25,
    'salinity_stress_stomata': 100,

    # Transpiration parameters
    'kc_max': 1.05,
    'kc_decline': 0.300,

    # Rooting parameters
    'min_rooting_depth': 0.30,
    'max_rooting_depth': 2.30,
    'root_expansion_shape': 13,
    'max_water_extraction_top': 0.045,
    'max_water_extraction_bottom': 0.011,
    'soil_evaporation_reduction': 50,

    # Canopy development parameters
    'canopy_cover_per_seedling': 6.50,
    'canopy_regrowth_size': 6.50,
    'plant_density': 80000,
    'max_canopy_cover': 0.96,
    'canopy_growth_coefficient': 0.16312,
    'canopy_thinning_years': -9,
    'canopy_thinning_shape': -9,
    'canopy_decline_coefficient': 0.11691,

    # Crop cycle parameters (Calendar days)
    'days_emergence': 6,
    'days_max_rooting': 108,
    'days_senescence': 107,
    'days_maturity': 132,
    'days_flowering': 66,
    'days_flowering_length': 13,
    'days_crop_determinancy': 1,
    'days_hi_start': 61,

    # Crop cycle parameters (Growing degree days)
    'gdd_emergence': 80,
    'gdd_max_rooting': 1409,
    'gdd_senescence': 1400,
    'gdd_maturity': 1700,
    'gdd_flowering': 880,
    'gdd_flowering_length': 180,
    'cgc_gdd': 0.012494,
    'cdc_gdd': 0.010000,
    'gdd_hi_start': 750,

    # Biomass and yield parameters
    'water_productivity': 33.7,
    'water_productivity_yield_formation': 100,
    'co2_response_strength': 50,
    'harvest_index': 0.431, # calculated based on the mean harvest index of all years for treatment A-N0 in jablje
    'water_stress_hi_increase': 0,
    'veg_growth_impact_hi': 7.0,
    'stomatal_closure_impact_hi': 3.0,
    'max_hi_increase': 15,
    'dry_matter_content': 90, # TODO preveri ali mogoče oceniti iz podatkov zrnje,slama

    # Perennial crop parameters
    'is_perennial': False,
    'first_year_min_rooting': 0.00,
    'assimilate_transfer': 0,
    'assimilate_storage_days': 0,
    'assimilate_transfer_percent': 0,
    'root_to_shoot_transfer_percent': 0,

    # Crop calendar for perennials - dummy values not used
    'restart_type': 0,
    'restart_window_day': 0,
    'restart_window_month': 0,
    'restart_window_length': 0,
    'restart_gdd_threshold': 0,
    'restart_days_required': 0,
    'restart_occurrences': 0,
    'end_type': 0,
    'end_window_day': 0,
    'end_window_month': 0,
    'end_window_years_offset': 0,
    'end_window_length': 0,
    'end_gdd_threshold': 0,
    'end_days_required': 0,
    'end_occurrences': 0
}

jablje_soil_layers=[
    SoilLayer(
        thickness=4,
        sat=46.0,
        fc=33.0,
        wp=13.0,
        ksat=575.0,
        penetrability=100,
        gravel=0,
        cra=-0.446850,
        crb=0.904118 ,
        description="silt loam"
    )
]

jablje_curve_number=61

jablje_readily_evaporable_water=11