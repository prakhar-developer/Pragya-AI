from datetime import datetime, timezone
from io import BytesIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from services import supabase_service

router = APIRouter(prefix="/api/v1/conflicts", tags=["conflicts"])

_RESPONSIBLE_ROLE = "shift_supervisor"


@router.get("")
async def list_conflicts():
    return supabase_service.get_conflicts()


@router.get("/{conflict_id}")
async def get_conflict(conflict_id: str):
    conflict = supabase_service.get_conflict_by_id(conflict_id)
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return conflict


@router.patch("/{conflict_id}/resolve")
async def resolve_conflict(conflict_id: str):
    resolved_at = datetime.now(timezone.utc).isoformat()
    updated = supabase_service.update_conflict(
        conflict_id, {"status": "resolved", "resolved_at": resolved_at}
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return updated


from reportlab.lib import colors

def _wrap(text: str, width: int) -> list[str]:
    words = str(text or "").split()
    if not words:
        return ["—"]
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width:
            if current:
                lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or ["—"]


def _build_work_order_pdf(conflict: dict) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 20 * mm
    right = width - 20 * mm
    content_width = right - left
    y = height - 20 * mm

    # Top Brand Header Banner
    pdf.setFillColor(colors.HexColor("#1E3A5F"))
    pdf.rect(left, y - 18 * mm, content_width, 18 * mm, fill=True, stroke=False)
    
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(left + 5 * mm, y - 8 * mm, "PRAGYA AI — INDUSTRIAL REASONING ENGINE")
    pdf.setFont("Helvetica", 9)
    pdf.drawString(left + 5 * mm, y - 14 * mm, "AUTOMATED MITIGATION WORK ORDER & SAFETY PERMIT DIRECTIVE")

    y -= 25 * mm

    # Conflict Severity Banner
    severity_val = float(conflict.get("severity", 0.0) or 0.0)
    exposure_inr = conflict.get("financial_exposure_inr", 0) or 0
    formatted_exposure = f"INR {exposure_inr:,.0f}" if isinstance(exposure_inr, (int, float)) else str(exposure_inr)

    banner_bg = colors.HexColor("#FFF1F2") if severity_val >= 0.7 else colors.HexColor("#FFFBEB")
    banner_border = colors.HexColor("#E11D48") if severity_val >= 0.7 else colors.HexColor("#D97706")
    banner_text = colors.HexColor("#9F1239") if severity_val >= 0.7 else colors.HexColor("#B45309")

    pdf.setFillColor(banner_bg)
    pdf.setStrokeColor(banner_border)
    pdf.rect(left, y - 12 * mm, content_width, 12 * mm, fill=True, stroke=True)

    pdf.setFillColor(banner_text)
    pdf.setFont("Helvetica-Bold", 11)
    status_label = "HIGH PRIORITY CONFLICT" if severity_val >= 0.7 else "MEDIUM PRIORITY CONFLICT"
    pdf.drawString(left + 5 * mm, y - 8 * mm, f"STATUS: {status_label} (SEVERITY: {severity_val:.2f})")
    pdf.drawRightString(right - 5 * mm, y - 8 * mm, f"EXPOSURE: {formatted_exposure}")

    y -= 18 * mm

    # Information Table Box
    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.rect(left, y - 55 * mm, content_width, 55 * mm, fill=True, stroke=True)

    table_fields = [
        ("Conflict ID", conflict.get("id", "N/A")),
        ("Equipment Tag", conflict.get("equipment_tag", "Line-4 / Plant Wide")),
        ("Responsible Role", conflict.get("responsible_role") or _RESPONSIBLE_ROLE),
        ("Governing Regulation", conflict.get("regulatory_reference", "OISD-GDN-105 / OISD-STD-116")),
        ("Resolution Target", conflict.get("deadline", "Immediate shift handover")),
        ("Generated Timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")),
    ]

    ty = y - 7 * mm
    for label, val in table_fields:
        pdf.setFillColor(colors.HexColor("#475569"))
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(left + 5 * mm, ty, f"{label}:")
        pdf.setFillColor(colors.HexColor("#0F172A"))
        pdf.setFont("Helvetica", 9)
        pdf.drawString(left + 50 * mm, ty, str(val))
        ty -= 8 * mm

    y -= 62 * mm

    # Conflict Description Block
    pdf.setFillColor(colors.HexColor("#1E293B"))
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(left, y, "1. Conflict Description & Cross-System Findings")
    y -= 6 * mm

    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica", 10)
    for line in _wrap(conflict.get("description", ""), 85):
        pdf.drawString(left + 3 * mm, y, line)
        y -= 5.5 * mm

    y -= 4 * mm

    # Mandatory Corrective Action Box
    pdf.setFillColor(colors.HexColor("#1E293B"))
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(left, y, "2. Recommended Corrective Actions & Resolution Steps")
    y -= 6 * mm

    action_text = conflict.get("recommended_action", "Execute safety inspection and update operational permit register.")
    pdf.setStrokeColor(colors.HexColor("#CCFBF1"))
    pdf.setFillColor(colors.HexColor("#F0FDFA"))
    pdf.rect(left, y - 24 * mm, content_width, 24 * mm, fill=True, stroke=True)

    pdf.setFillColor(colors.HexColor("#0F766E"))
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(left + 4 * mm, y - 6 * mm, "[MANDATORY SHIFT ACTION PLAN]")

    pdf.setFillColor(colors.HexColor("#1E293B"))
    pdf.setFont("Helvetica", 9)
    ay = y - 12 * mm
    for line in _wrap(action_text, 80):
        pdf.drawString(left + 4 * mm, ay, f"• {line}")
        ay -= 5 * mm

    y -= 32 * mm

    # Operational Checkpoints
    pdf.setFillColor(colors.HexColor("#1E293B"))
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(left, y, "3. Field Verification Checkpoints")
    y -= 6 * mm

    checkpoints = [
        "[ ] Hydrocarbon gas sniff test verified (LEL < 1% measured by certified technician)",
        "[ ] Conflicting hot-work or welding permits suspended and logged in PTW kiosk",
        "[ ] Lockout/Tagout (LOTO) mechanical isolation confirmed on valves and breakers",
        "[ ] Equipment state updated in live PRAGYA AI knowledge graph registry",
    ]
    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.HexColor("#334155"))
    for cp in checkpoints:
        pdf.drawString(left + 4 * mm, y, cp)
        y -= 5.5 * mm

    y -= 4 * mm

    # Supervisor Sign-off Footer Box
    pdf.setStrokeColor(colors.HexColor("#94A3B8"))
    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.rect(left, y - 20 * mm, content_width, 20 * mm, fill=True, stroke=True)

    pdf.setFillColor(colors.HexColor("#475569"))
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(left + 4 * mm, y - 6 * mm, "AUTHORIZED SHIFT SUPERVISOR SIGN-OFF")
    pdf.drawString(left + 65 * mm, y - 6 * mm, "FIELD SAFETY OFFICER SIGNATURE")
    pdf.drawString(left + 125 * mm, y - 6 * mm, "DATE / TIME COMPLETED")

    pdf.setFont("Helvetica", 8)
    pdf.drawString(left + 4 * mm, y - 15 * mm, "Name / Badge: _____________________")
    pdf.drawString(left + 65 * mm, y - 15 * mm, "Sign: ________________________")
    pdf.drawString(left + 125 * mm, y - 15 * mm, "____ / ____ / 2026   __:__ hrs")

    # Document Footer
    pdf.setFont("Helvetica", 7)
    pdf.setFillColor(colors.HexColor("#94A3B8"))
    pdf.drawString(left, 10 * mm, "PRAGYA AI Industrial Reasoning Engine · System Architect: Prakhar Srivastava · OISD/OSHA Audit Directive")
    pdf.drawRightString(right, 10 * mm, f"Doc Ref: WO-GEN-{conflict.get('id', 'AUTO')}")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


@router.post("/{conflict_id}/generate")
async def generate_work_order(conflict_id: str):
    conflict = supabase_service.get_conflict_by_id(conflict_id)
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    pdf_bytes = _build_work_order_pdf(conflict)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=work_order_{conflict_id}.pdf"
        },
    )
