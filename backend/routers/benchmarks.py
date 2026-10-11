from fastapi import APIRouter

from services import supabase_service

router = APIRouter(prefix="/api/v1/benchmarks", tags=["benchmarks"])

_BENCHMARK_QUESTIONS = [
    {
        "query_id": "BM-01",
        "question": "What is the minimum safe distance mandated by OISD-STD-118 between two "
        "floating roof crude storage tanks in a refinery tank farm?",
        "ground_truth": "OISD-STD-118 requires the inter-tank spacing between adjacent "
        "floating roof tanks to be a minimum of the diameter of the smaller tank, subject "
        "to a minimum of 10 metres, to allow fire-fighting access and limit fire spread.",
        "category": "OISD compliance",
    },
    {
        "query_id": "BM-02",
        "question": "Under OISD-STD-116, what is the required frequency of thickness "
        "monitoring for piping in hydrocarbon service subject to corrosion?",
        "ground_truth": "OISD-STD-116 requires thickness surveys of corrosion-prone "
        "hydrocarbon piping at intervals not exceeding the remaining-life-based schedule, "
        "typically every 2 to 4 years depending on measured corrosion rate.",
        "category": "OISD compliance",
    },
    {
        "query_id": "BM-03",
        "question": "Is a hot work permit valid for a full shift on a running crude "
        "distillation unit under OISD-GDN-105 permit-to-work requirements?",
        "ground_truth": "No. Under OISD-GDN-105 a hot work permit is valid only for the "
        "specified duration (normally one shift or less) and must be revalidated after any "
        "break, gas test lapse, or change in job conditions.",
        "category": "OISD compliance",
    },
    {
        "query_id": "BM-04",
        "question": "What is the current operational state of pump P-101A according to the "
        "latest recorded state transition?",
        "ground_truth": "Pump P-101A is in the 'under_maintenance' state following its last "
        "recorded transition from 'running' due to high bearing vibration flagged in the "
        "inspection work order.",
        "category": "equipment state",
    },
    {
        "query_id": "BM-05",
        "question": "Which crude preheat exchanger E-104 shell has been isolated and why?",
        "ground_truth": "Exchanger E-104 shell side is isolated for tube-bundle cleaning "
        "because fouling raised the pressure drop above the OEM design limit, reducing "
        "preheat train efficiency.",
        "category": "equipment state",
    },
    {
        "query_id": "BM-06",
        "question": "Has pressure safety valve PSV-220 on the debutanizer been tested within "
        "its OISD-mandated certification interval?",
        "ground_truth": "PSV-220 is overdue: its last pop-test was beyond the OISD-STD-132 "
        "recommended interval, so it is flagged non-compliant and scheduled for immediate "
        "bench testing.",
        "category": "equipment state",
    },
    {
        "query_id": "BM-07",
        "question": "Is there a conflict between the maintenance schedule for compressor "
        "K-301 and the active hot work permit in its vicinity?",
        "ground_truth": "Yes. A conflict exists because the planned online maintenance of "
        "K-301 overlaps with an active hot work permit in the same unit, which violates "
        "simultaneous-operations safety rules and must be rescheduled.",
        "category": "conflict detection",
    },
    {
        "query_id": "BM-08",
        "question": "Do the OEM lubrication interval for pump P-205 and the site preventive "
        "maintenance procedure disagree?",
        "ground_truth": "Yes. The OEM manual specifies a 3-month lubrication interval while "
        "the site PM procedure lists 6 months, creating a compliance gap that favours the "
        "stricter OEM interval.",
        "category": "conflict detection",
    },
    {
        "query_id": "BM-09",
        "question": "Is there a contradiction between the fire-water demand for the tank "
        "farm and the installed pump capacity per OISD-STD-116?",
        "ground_truth": "Yes. The calculated fire-water demand for simultaneous tank cooling "
        "and foam application exceeds the installed fire-water pump capacity, a shortfall "
        "against OISD-STD-116 that requires capacity augmentation.",
        "category": "conflict detection",
    },
    {
        "query_id": "BM-10",
        "question": "What corrective action is recommended when a nitrogen purge procedure "
        "conflicts with a confined space entry permit on vessel V-410?",
        "ground_truth": "The confined space entry must be suspended until the nitrogen purge "
        "is completed and the vessel is re-tested for oxygen at 19.5-23.5 percent, since "
        "entry during inert purging is prohibited under confined space safety rules.",
        "category": "conflict detection",
    },
]


@router.get("")
async def list_benchmarks():
    return supabase_service.get_benchmark_results()


@router.post("/seed")
async def seed_benchmarks():
    return supabase_service.seed_benchmarks(_BENCHMARK_QUESTIONS)
