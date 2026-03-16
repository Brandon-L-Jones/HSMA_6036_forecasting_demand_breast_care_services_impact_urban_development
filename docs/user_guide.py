# docs/user_guide.py

def get_user_guide():
    return """
# RDUH Breast Service Demand Forecasting Tool
HSMA 6036 – Forecasting Demand for Breast Care Services

---

## 1. Purpose of This Tool

This application supports strategic planning for breast diagnostic services.
It forecasts future 2WW (Two-Week Wait) referral demand and estimates
the diagnostic capacity required to meet demand under uncertainty.

The tool is designed to inform workforce and imaging planning decisions
within Royal Devon University Healthcare NHS Foundation Trust (RDUH).

---

## 2. What the Model Does

The system combines:

1. A deterministic demand forecast model
2. A discrete event simulation (DES) of the diagnostic pathway
3. A Monte Carlo uncertainty wrapper
4. A capacity search function to test resource requirements

Outputs include:
- Projected daily and annual referrals
- Year-on-year growth
- Simulated waiting times
- Estimated capacity needed to meet targets

---

## 3. Key Assumptions

### Population Growth
Each geography has:
- Baseline annual growth (%)
- Additional housing-related growth (%)

These are illustrative assumptions and should be replaced with:
- ONS Subnational Population Projections
- Local authority housing plans

### Referral Inflation
Represents increasing GP referral behaviour or awareness effects.

### Age Weighting
Older age groups generate higher diagnostic demand.
Age weights are simplified and not tumour-incidence-based.

### Simulation
The DES assumes:
- Exponential inter-arrival times
- Fixed resource capacity
- No dynamic workforce reallocation
- No emergency prioritisation

---

## 4. What This Tool Is NOT

- It is not a clinical decision system.
- It is not a replacement for national cancer modelling.
- It does not model screening pathways.
- It does not include financial costing (unless extended).

---

## 5. How to Use the Tool

Step 1: Select geography  
Step 2: Choose scenario  
Step 3: Adjust simulation parameters  
Step 4: Review forecast outputs  
Step 5: Run capacity search if required  

---

## 6. Interpretation Guidance

If utilisation > 85%:
→ The system is likely operating near saturation.

If simulated waiting times increase rapidly under small demand changes:
→ The pathway is highly capacity-sensitive.

If capacity search increases resources significantly:
→ Long-term workforce planning intervention may be required.

---

## 7. Model Limitations

- Uses simplified age weighting
- Does not include deprivation gradients
- Assumes stable clinical pathways
- Does not model workforce sickness or leave
- Uses synthetic service time distributions

Future improvements could include:
- Real SUS pathway data
- Screening demand integration
- Workforce costing
- Scenario comparison dashboard

---

## 8. Governance and Validation

Before operational use:
- Validate baseline referrals against RTT/SUS data
- Compare forecast with historical trend
- Conduct sensitivity analysis
- Peer review assumptions

---

End of User Guide
"""
