"""
Water Quality Analysis Engine
Computes parameter evaluations, Water Quality Index (WQI), classification (Safe, Moderate, Unsafe),
and actionable treatment recommendations based on WHO and BIS standards.
"""

def evaluate_ph(ph):
    ph = float(ph)
    if 6.5 <= ph <= 8.5:
        if 6.8 <= ph <= 7.8:
            detail = "Ideal neutral range, optimal for human consumption."
        else:
            detail = "Within permissible WHO drinking water limits."
        return {
            "status": "Safe",
            "class": "safe",
            "score": max(80, 100 - abs(ph - 7.2) * 15),
            "label": "Optimal / Permissible",
            "detail": detail,
            "standard": "6.5 - 8.5"
        }
    elif (6.0 <= ph < 6.5) or (8.5 < ph <= 9.0):
        if ph < 6.5:
            detail = "Slightly acidic. Mild pipe corrosion risk; may leach trace metals."
        else:
            detail = "Slightly alkaline. Can cause mild mineral scaling and mineral aftertaste."
        return {
            "status": "Moderate",
            "class": "moderate",
            "score": 60.0 - abs(ph - 7.2) * 8,
            "label": "Mild Deviation",
            "detail": detail,
            "standard": "6.5 - 8.5"
        }
    else:
        if ph < 6.0:
            detail = "Highly acidic & corrosive. Potential for heavy metal leaching (lead, copper). Unfit for drinking."
        else:
            detail = "Excessively alkaline/caustic. Bitter taste, severe scale deposits, skin/eye irritation."
        return {
            "status": "Unsafe",
            "class": "unsafe",
            "score": max(10, 40 - abs(ph - 7.2) * 6),
            "label": "Severe Deviation",
            "detail": detail,
            "standard": "6.5 - 8.5"
        }

def evaluate_tds(tds):
    tds = float(tds)
    if tds < 300:
        return {
            "status": "Safe",
            "class": "safe",
            "score": 95.0,
            "label": "Excellent",
            "detail": "Ideal mineral balance; pristine palatability and taste.",
            "standard": "< 500 mg/L"
        }
    elif tds <= 500:
        return {
            "status": "Safe",
            "class": "safe",
            "score": 85.0 - ((tds - 300) / 200) * 10,
            "label": "Good / Acceptable",
            "detail": "Within recommended WHO drinking limits; safe for daily consumption.",
            "standard": "< 500 mg/L"
        }
    elif tds <= 900:
        return {
            "status": "Moderate",
            "class": "moderate",
            "score": 65.0 - ((tds - 500) / 400) * 20,
            "label": "Fair / Elevated",
            "detail": "Elevated mineral hardness. May cause appliance scaling and mineral taste.",
            "standard": "< 500 mg/L"
        }
    else:
        return {
            "status": "Unsafe",
            "class": "unsafe",
            "score": max(5, 40.0 - ((tds - 900) / 600) * 30),
            "label": "Poor / Unacceptable",
            "detail": "Excessive dissolved solids (>900 mg/L). High salinity/contaminants risk.",
            "standard": "< 500 mg/L"
        }

def evaluate_turbidity(turbidity):
    turbidity = float(turbidity)
    if turbidity <= 1.0:
        return {
            "status": "Safe",
            "class": "safe",
            "score": 98.0 - (turbidity * 5),
            "label": "Pristine / Clear",
            "detail": "Exceptional optical clarity; ideal for effective UV and chlorine disinfection.",
            "standard": "<= 5.0 NTU"
        }
    elif turbidity <= 5.0:
        return {
            "status": "Safe",
            "class": "safe",
            "score": 85.0 - ((turbidity - 1.0) / 4.0) * 15,
            "label": "Acceptable Limit",
            "detail": "Acceptable under WHO/BIS standards, minor colloidal particles present.",
            "standard": "<= 5.0 NTU"
        }
    elif turbidity <= 10.0:
        return {
            "status": "Moderate",
            "class": "moderate",
            "score": 65.0 - ((turbidity - 5.0) / 5.0) * 25,
            "label": "Cloudy / Suspended",
            "detail": "Noticeable murkiness. Particulates may shield microbes from disinfection.",
            "standard": "<= 5.0 NTU"
        }
    else:
        return {
            "status": "Unsafe",
            "class": "unsafe",
            "score": max(5, 35.0 - ((turbidity - 10.0) / 20.0) * 30),
            "label": "High Turbidity / Muddy",
            "detail": "Severely turbid (>10 NTU). High risk of suspended contaminants and pathogens.",
            "standard": "<= 5.0 NTU"
        }

def analyze_water_sample(ph, tds, turbidity):
    """
    Performs full scientific analysis of water sample.
    Returns:
        dict: Detailed result containing overall status, WQI score, parameter evaluations,
              and recommendations.
    """
    ph_val = float(ph)
    tds_val = float(tds)
    turb_val = float(turbidity)

    eval_ph = evaluate_ph(ph_val)
    eval_tds = evaluate_tds(tds_val)
    eval_turb = evaluate_turbidity(turb_val)

    # Calculate weighted Water Quality Index (WQI: 0 - 100)
    # Weights: pH: 0.35, TDS: 0.35, Turbidity: 0.30
    wqi_score = round(
        (eval_ph["score"] * 0.35) + 
        (eval_tds["score"] * 0.35) + 
        (eval_turb["score"] * 0.30), 1
    )
    wqi_score = max(0.0, min(100.0, wqi_score))

    # Overall Status Determination:
    # Rule 1: Any unsafe parameter immediately downgrades overall sample to Unsafe
    # Rule 2: Any moderate parameter without unsafe downgrades to Moderate
    # Rule 3: All safe -> Safe
    statuses = [eval_ph["status"], eval_tds["status"], eval_turb["status"]]
    
    if "Unsafe" in statuses or wqi_score < 50:
        overall_status = "Unsafe"
        status_class = "unsafe"
        summary_title = "Water is Unsafe for Drinking"
        summary_desc = "One or more critical parameters exceed health-based thresholds. Direct consumption poses significant health or gastrointestinal risks. Immediate purification is mandatory."
    elif "Moderate" in statuses or wqi_score < 75:
        overall_status = "Moderate"
        status_class = "moderate"
        summary_title = "Water Quality is Moderate / Marginal"
        summary_desc = "Parameters lie in the borderline acceptable zone. Suitable for general domestic, washing, or agricultural use, but filtration/treatment is advised before drinking."
    else:
        overall_status = "Safe"
        status_class = "safe"
        summary_title = "Water is Safe for Consumption"
        summary_desc = "All monitored chemical and physical parameters comply with WHO and national drinking water quality standards. Water is safe, potable, and clear."

    # Treatment & Actionable Recommendations
    recommendations = []
    
    # pH recommendations
    if ph_val < 6.5:
        recommendations.append({
            "title": "pH Neutralization (Acidity Treatment)",
            "body": "Install a calcite/magnesium oxide neutralizing filter or add food-grade sodium bicarbonate to elevate pH to neutral (7.0 - 7.4) and halt pipe corrosion."
        })
    elif ph_val > 8.5:
        recommendations.append({
            "title": "pH Reduction (Alkalinity Treatment)",
            "body": "Utilize mild food-grade citric or phosphoric acid dosing, or pass water through an ion-exchange water softener to balance alkalinity."
        })
        
    # TDS recommendations
    if tds_val > 500:
        recommendations.append({
            "title": "Reverse Osmosis (RO) Demineralization",
            "body": "Employ a multi-stage Reverse Osmosis (RO) filtration system or electrodialysis to filter excess dissolved minerals, salts, and hardness below 300 mg/L."
        })
    elif tds_val < 50:
        recommendations.append({
            "title": "Mineral Remineralization",
            "body": "Water is demineralized (over-purified). Add a remineralization cartridge (calcium & magnesium) to enhance palatability and nutritional value."
        })

    # Turbidity recommendations
    if turb_val > 5.0:
        recommendations.append({
            "title": "Sediment Filtration & Coagulation",
            "body": "Pass water through a 5-micron spun polypropylene sediment filter followed by alum/polyaluminium chloride coagulation to eliminate suspended solids."
        })
    
    # Disinfection recommendation
    if overall_status in ["Moderate", "Unsafe"]:
        recommendations.append({
            "title": "Pathogen Disinfection",
            "body": "Bring water to a rolling boil for at least 3 minutes, or install an inline Ultraviolet (UV) disinfection chamber to destroy microbiological pathogens."
        })
    else:
        recommendations.append({
            "title": "Routine Maintenance",
            "body": "Maintain periodic testing every 30 days and replace pre-filter cartridges annually to safeguard sustained potability."
        })

    return {
        "overall_status": overall_status,
        "status_class": status_class,
        "wqi_score": wqi_score,
        "summary_title": summary_title,
        "summary_desc": summary_desc,
        "parameters": {
            "ph": {
                "name": "pH Level",
                "value": ph_val,
                "unit": "pH scale",
                "status": eval_ph["status"],
                "class": eval_ph["class"],
                "label": eval_ph["label"],
                "detail": eval_ph["detail"],
                "standard": eval_ph["standard"]
            },
            "tds": {
                "name": "Total Dissolved Solids",
                "value": tds_val,
                "unit": "mg/L (ppm)",
                "status": eval_tds["status"],
                "class": eval_tds["class"],
                "label": eval_tds["label"],
                "detail": eval_tds["detail"],
                "standard": eval_tds["standard"]
            },
            "turbidity": {
                "name": "Turbidity",
                "value": turb_val,
                "unit": "NTU",
                "status": eval_turb["status"],
                "class": eval_turb["class"],
                "label": eval_turb["label"],
                "detail": eval_turb["detail"],
                "standard": eval_turb["standard"]
            }
        },
        "recommendations": recommendations
    }
