"""Generate the Capstone Demo Template PDF for PickGuard AI."""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic total page count."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "PICKGUARD AI — CAPSTONE DEMO TEMPLATE")
            self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "OFFICIAL SUBMISSION DOCUMENT")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * inch - 54, 46)

        self.drawString(54, 32, "PickGuard AI — Evidence-Grounded Pick Exception Resolution Agent")
        self.drawRightString(8.5 * inch - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf(filename: str):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Colors
    primary_color = colors.HexColor("#0f172a")
    accent_blue = colors.HexColor("#1d4ed8")
    accent_cyan = colors.HexColor("#0284c7")
    accent_dark = colors.HexColor("#1e293b")
    text_color = colors.HexColor("#334155")
    bg_light = colors.HexColor("#f8fafc")
    border_color = colors.HexColor("#e2e8f0")

    # Typography styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=accent_cyan,
        spaceAfter=12,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=accent_blue,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=text_color,
        spaceAfter=5,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=text_color,
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell_style,
        fontName="Helvetica-Bold",
        textColor=primary_color,
    )

    code_style = ParagraphStyle(
        "CodeText",
        parent=body_style,
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0369a1"),
    )

    story = []

    # ================= TITLE & HEADER =================
    story.append(Paragraph("CAPSTONE DEMO TEMPLATE", title_style))
    story.append(Paragraph("Official Capstone Submission & Evaluation Document — PickGuard AI", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceAfter=10))

    # ================= SECTION 1: TEAM NAME & PROBLEM =================
    story.append(Paragraph("1. Team Name & Problem Formulation", h1_style))

    team_data = [
        [
            Paragraph("<b>Team Name:</b>", table_cell_bold),
            Paragraph("<b>Vision Forge</b> (Author / Engineer: <b>Ruban Raj</b>)", table_cell_style),
        ],
        [
            Paragraph("<b>Who is the User?</b>", table_cell_bold),
            Paragraph(
                "Fulfilment Centre <b>Pick Operators</b> encountering physical exceptions (missing items, damaged barcodes, bin discrepancies) during active pick waves, along with <b>Warehouse Supervisors / Operations Leads</b> managing escalation queues.",
                table_cell_style,
            ),
        ],
        [
            Paragraph("<b>What is the Bounded Task?</b>", table_cell_bold),
            Paragraph(
                "Provide an <b>evidence-grounded, next-best-action decision recommendation</b> in response to natural-language pick exceptions. The agent retrieves verified bin/task/inventory facts and SOP procedures, identifies conflicts, reasons over facts vs inferences, enforces safety boundaries (mutations are blocked), and pauses at a real <b>LangGraph interrupt() checkpoint</b> for human authorization on high-risk cases.",
                table_cell_style,
            ),
        ],
    ]
    t_team = Table(team_data, colWidths=[120, 384])
    t_team.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), bg_light),
            ("BOX", (0, 0), (-1, -1), 1, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(t_team)
    story.append(Spacer(1, 8))

    # ================= SECTION 2: AGENT DESIGN =================
    story.append(Paragraph("2. Agent Design Architecture", h1_style))

    design_data = [
        [
            Paragraph("<b>Graph State:</b>", table_cell_bold),
            Paragraph(
                "<code>PickExceptionState</code> (TypedDict in <code>backend/app/graph/state.py</code>): Tracks <code>query</code>, <code>exception_type</code>, <code>secondary_exception_types</code>, <code>task_id</code>, <code>item_id</code>, <code>location_id</code>, <code>operational_data</code>, <code>sop_evidence</code>, <code>historical_evidence</code>, <code>evidence_package</code>, <code>reasoning</code>, <code>root_cause</code>, <code>next_best_action</code>, <code>action_type</code>, <code>action_status</code>, <code>risk_level</code>, <code>requires_human_review</code>, <code>human_review_payload</code>, <code>review_attempts</code>, <code>audit_log</code>, and <code>errors</code>.",
                table_cell_style,
            ),
        ],
        [
            Paragraph("<b>Nodes (13 Nodes):</b>", table_cell_bold),
            Paragraph(
                "<b>1.</b> <code>parse_operator_input</code> &nbsp; <b>2.</b> <code>classify_exception</code> &nbsp; <b>3.</b> <code>retrieve_operational_data</code> &nbsp; <b>4.</b> <code>retrieve_sop_evidence</code> &nbsp; <b>5.</b> <code>retrieve_historical_evidence</code> &nbsp; <b>6.</b> <code>build_evidence_package</code> &nbsp; <b>7.</b> <code>llm_reasoning_node</code> &nbsp; <b>8.</b> <code>evidence_fusion_node</code> &nbsp; <b>9.</b> <code>evaluate_safety_policy</code> &nbsp; <b>10.</b> <code>human_review_gate</code> (with <code>interrupt()</code>) &nbsp; <b>11.</b> <code>collect_additional_evidence</code> &nbsp; <b>12.</b> <code>apply_final_decision</code> &nbsp; <b>13.</b> <code>END</code>.",
                table_cell_style,
            ),
        ],
        [
            Paragraph("<b>Deterministic Tools:</b>", table_cell_bold),
            Paragraph(
                "• <code>get_inventory(item_id, location_id)</code>: Database units & status.<br/>"
                "• <code>get_pick_task(task_id)</code>: Expected pick quantity & target bin.<br/>"
                "• <code>get_location(location_id)</code>: Storage zone & adjacent neighbouring bins.<br/>"
                "• <code>search_similar_incidents(exception_type)</code>: Past resolution precedence.<br/>"
                "• <code>escalate_to_lead(task_id, reason)</code>: WMS supervisor queue escalation.<br/>"
                "• <code>retrieve_sop_chunks(query, exception_type)</code>: ChromaDB vector RAG retrieval.",
                table_cell_style,
            ),
        ],
        [
            Paragraph("<b>Provider Route:</b>", table_cell_bold),
            Paragraph(
                "Multi-Tier Resilient Routing Hierarchy:<br/>"
                "<b>Tier 1: GroqProvider</b> (Llama-3.3-70B cloud inference for ultra-fast reasoning)<br/>"
                "<b>Tier 2: OllamaProvider</b> (Local offline inference with Llama3 model)<br/>"
                "<b>Tier 3: MimicProvider</b> (Deterministic offline fallback guaranteeing 100% demo uptime without external API keys).",
                table_cell_style,
            ),
        ],
        [
            Paragraph("<b>Human-Review Point:</b>", table_cell_bold),
            Paragraph(
                "Implemented via real <code>from langgraph.types import interrupt, Command</code> in the <code>human_review_gate</code> node. The graph pauses if <code>requires_human_review == True</code> (triggered by hazardous mutating actions or evidence conflicts). State is saved with <code>MemorySaver</code> checkpointer. Resumption occurs via <code>Command(resume={'decision': 'APPROVE' | 'REJECT' | 'REQUEST_MORE_EVIDENCE' | 'ESCALATE'})</code>.",
                table_cell_style,
            ),
        ],
    ]
    t_design = Table(design_data, colWidths=[120, 384])
    t_design.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), bg_light),
            ("BOX", (0, 0), (-1, -1), 1, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(t_design)
    story.append(Spacer(1, 8))

    # ================= SECTION 3: DEMO SCRIPT =================
    story.append(Paragraph("3. Demonstration Script (3 Core Cases)", h1_style))

    demo_data = [
        [
            Paragraph("Scenario", table_header_style),
            Paragraph("Operator Query & Context", table_header_style),
            Paragraph("System Execution & UI Output", table_header_style),
        ],
        [
            Paragraph("<b>Normal Case</b><br/>(Low Risk)", table_cell_style),
            Paragraph(
                "<b>Query:</b> <i>'The item X123 is missing from A15-B04. The system says there are 3 units.'</i><br/>"
                "<b>Task:</b> TASK-1001 | <b>SKU:</b> X123 | <b>Bin:</b> A15-B04",
                table_cell_style,
            ),
            Paragraph(
                "• <b>Exception:</b> <code>MISSING_ITEM</code> | <b>Risk:</b> <code>LOW RISK</code> (Green)<br/>"
                "• <b>Evidence:</b> Retrieves bin A15-B04 + neighbours [A15-B03, A15-B05], SOP-MISSING-001.<br/>"
                "• <b>Next-Best Action:</b> <code>CHECK_NEIGHBOURING_LOCATION</code> (Status: <code>RECOMMENDED</code>)<br/>"
                "• <b>HITL Interrupt:</b> None required. Workflow completes automatically.",
                table_cell_style,
            ),
        ],
        [
            Paragraph("<b>Edge Case</b><br/>(Multi-Signal)", table_cell_style),
            Paragraph(
                "<b>Query:</b> <i>'The item X124 is missing at A12-B03 and the barcode also won\'t scan.'</i><br/>"
                "<b>Task:</b> TASK-1002 | <b>SKU:</b> X124 | <b>Bin:</b> A12-B03",
                table_cell_style,
            ),
            Paragraph(
                "• <b>Exception:</b> Primary <code>MISSING_ITEM</code> + Secondary <code>BARCODE_FAILURE</code><br/>"
                "• <b>Evidence:</b> Retrieves both SOP-MISSING-001 and SOP-BARCODE-001.<br/>"
                "• <b>Next-Best Action:</b> Recommends manual barcode entry followed by physical sweep.<br/>"
                "• <b>HITL Interrupt:</b> None required. Demonstrates compound signal reasoning.",
                table_cell_style,
            ),
        ],
        [
            Paragraph("<b>Failure / Risky Case</b><br/>(HITL Interrupt)", table_cell_style),
            Paragraph(
                "<b>Query:</b> <i>'TASK-1003 quantity mismatch: System says 10 units of X125 at A20-B02 but I counted 6. Update inventory to 6.'</i><br/>"
                "<b>Task:</b> TASK-1003 | <b>SKU:</b> X125 | <b>Bin:</b> A20-B02",
                table_cell_style,
            ),
            Paragraph(
                "• <b>Exception:</b> <code>QUANTITY_MISMATCH</code> | <b>Risk:</b> <code>HIGH RISK</code> (Red)<br/>"
                "• <b>Action Boundary:</b> <code>ADJUST_QUANTITY</code> is automatically <b><code>BLOCKED</code></b>.<br/>"
                "• <b>LangGraph Interrupt:</b> Graph pauses at <code>human_review_gate</code> node.<br/>"
                "• <b>Supervisor Review:</b> Modal presents conflict (10 vs 6). Supervisor selects <b><code>REJECT</code></b>.<br/>"
                "• <b>Resume:</b> Graph resumes; state set to <code>REJECTED_BY_HUMAN</code>; inventory remains <b>UNCHANGED</b>.",
                table_cell_style,
            ),
        ],
    ]
    t_demo = Table(demo_data, colWidths=[90, 190, 224])
    t_demo.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 1, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, bg_light]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(t_demo)
    story.append(Spacer(1, 8))

    # ================= SECTION 4: EVALUATION SUMMARY =================
    story.append(Paragraph("4. Evaluation Summary Matrix", h1_style))

    eval_data = [
        [
            Paragraph("Test", table_header_style),
            Paragraph("Expected", table_header_style),
            Paragraph("Actual", table_header_style),
            Paragraph("Pass?", table_header_style),
            Paragraph("Improvement", table_header_style),
        ],
        [
            Paragraph("<b>Normal</b>", table_cell_style),
            Paragraph("Safe suggestion (<code>CHECK_NEIGHBOURING_LOCATION</code>), <code>LOW</code> risk, no interrupt.", table_cell_style),
            Paragraph("Correct category, <code>LOW</code> risk, <code>RECOMMENDED</code> status, completed automatically.", table_cell_style),
            Paragraph("<font color='#16a34a'><b>PASS</b></font>", table_cell_bold),
            Paragraph("Add direct map visualization for adjacent bin coordinates.", table_cell_style),
        ],
        [
            Paragraph("<b>Edge</b>", table_cell_style),
            Paragraph("Multi-signal detection (<code>MISSING_ITEM + BARCODE_FAILURE</code>), compound verification.", table_cell_style),
            Paragraph("Detected primary and secondary types; retrieved both SOP procedures.", table_cell_style),
            Paragraph("<font color='#16a34a'><b>PASS</b></font>", table_cell_bold),
            Paragraph("Add optical barcode image preview recognition in future.", table_cell_style),
        ],
        [
            Paragraph("<b>Failure / High-Risk</b>", table_cell_style),
            Paragraph("Action <code>BLOCKED</code>, <code>HIGH</code> risk, LangGraph <code>interrupt()</code> pauses graph.", table_cell_style),
            Paragraph("Action <code>BLOCKED</code>, paused at checkpoint, resumed cleanly upon supervisor review.", table_cell_style),
            Paragraph("<font color='#16a34a'><b>PASS</b></font>", table_cell_bold),
            Paragraph("Add dual-supervisor multi-signature approval for high-value items.", table_cell_style),
        ],
    ]
    t_eval = Table(eval_data, colWidths=[65, 120, 135, 44, 140])
    t_eval.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), accent_dark),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 1, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, bg_light]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(t_eval)
    story.append(Spacer(1, 8))

    # ================= SECTION 5: REFLECTION =================
    story.append(Paragraph("5. Reflection: What would you improve with one more week?", h1_style))

    reflection_text = (
        "<b>1. Multi-Modal Vision Integration:</b> Ingest barcode scanner images and camera feeds directly into the graph to automatically detect packaging damage and barcode label blemishes using multi-modal LLMs.<br/>"
        "<b>2. Real-Time WMS Webhook Streaming:</b> Transition from polling REST endpoints to WebSocket/Server-Sent Events (SSE) for instant supervisor push notifications when an interrupt checkpoint triggers.<br/>"
        "<b>3. Multi-Tier Supervisor Escalation Matrix:</b> Introduce tiered authorization rules based on unit monetary value (e.g. items > $500 require Area Manager dual sign-off).<br/>"
        "<b>4. Reinforcement Learning from Human Feedback (RLHF):</b> Fine-tune the local reasoning model on historical supervisor approval/rejection outcomes to improve first-pass recommendation accuracy."
    )
    story.append(Paragraph(reflection_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {filename}")


if __name__ == "__main__":
    output_pdf = "docs/PickGuard_AI_Capstone_Demo_Template.pdf"
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    build_pdf(output_pdf)
