# ER-схема

## Strain

`strain_id, species, collection_number, origin, biosafety_level, reactivation_rule`.

## Medium

`medium_id, name, purpose, pH, state, status`.

## MediumComponent

`medium_id, component, concentration_g_l, hydrate_form, role`.

## BatchRun

`batch_id, strain_id, medium_id, bioreactor_id, working_volume_l, inoculum_volume_ml, start_datetime`.

## Observation

`observation_id, batch_id, time_h, pH, pO2_percent, temperature_C, rpm, biomass, kla, protein, sugars, amino_nitrogen`.

## Rule

`rule_id, condition, conclusion, recommendation, confidence`.
