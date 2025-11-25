import gradio as gr
import json
import os
import time


class SageCompassUI:
    def __init__(self, app):
        self.app = app

    def _dump_obj(self, obj):
        if hasattr(obj, "model_dump"):
            return json.dumps(obj.model_dump(), indent=2, ensure_ascii=False)

        if isinstance(obj, list):
            try:
                return json.dumps(
                    [
                        (x.model_dump() if hasattr(x, "model_dump") else x)
                        for x in obj
                    ],
                    indent=2,
                    ensure_ascii=False,
                )
            except TypeError:
                return repr(obj)

        try:
            return json.dumps(obj, indent=2, ensure_ascii=False)
        except TypeError:
            return repr(obj)

    def _summarize_chunk(self, label, value) -> str:
        """
        Produce a short, human-friendly status line per section,
        instead of dumping the full JSON.
        """

        # PROBLEM FRAME
        if label == "PROBLEM FRAME":
            try:
                domain = getattr(value, "business_domain", None) or value.get("business_domain")
                outcome = getattr(value, "primary_outcome", None) or value.get("primary_outcome")
                return f"[PF] Problem framed – domain: {domain}; outcome: {outcome}"
            except Exception:
                return "[PF] Problem framed."

        # BUSINESS GOALS
        if label == "BUSINESS GOALS":
            try:
                goals = list(value)
                n = len(goals)
                subjects = []
                for g in goals[:3]:
                    subj = getattr(g, "subject", None) or g.get("subject")
                    if subj:
                        subjects.append(subj)
                subjects_str = "; ".join(subjects)
                return f"[BG] {n} business goals identified. Top: {subjects_str}"
            except Exception:
                return "[BG] - Business goals identified."

        # ELIGIBILITY
        if label == "ELIGIBILITY":
            try:
                category = getattr(value, "category", None) or value.get("category")
                confidence = getattr(value, "confidence", None) or value.get("confidence")
                return f"[EA] Eligibility: {category} (confidence {confidence:.2f})"
            except Exception:
                return "[EA] Eligibility result ready."

        # KPIs
        if label == "KPIs":
            try:
                kpis = list(value)
                n = len(kpis)
                subjects = []
                for k in kpis[:3]:
                    subj = getattr(k, "subject", None) or k.get("subject")
                    if subj:
                        subjects.append(subj)
                subjects_str = "; ".join(subjects)
                return f"[KPI] {n} KPIs defined. Examples: {subjects_str}"
            except Exception:
                return "[KPI] KPI set ready."

        # SOLUTION DESIGN
        if label == "SOLUTION DESIGN":
            try:
                options = getattr(value, "options", None) or value.get("options", [])
                options = list(options)
                n = len(options)
                rec_id = getattr(value, "recommended_option_id", None) or value.get("recommended_option_id")
                return f"[SDA] {n} solution options. Recommended: {rec_id or 'not specified'}"
            except Exception:
                return "[SDA] Solution design ready."

        # COST ESTIMATES
        if label == "COST ESTIMATES":
            try:
                ests = list(value)
                n = len(ests)
                opt_ids = []
                for e in ests[:3]:
                    oid = getattr(e, "option_id", None) or e.get("option_id")
                    if oid:
                        opt_ids.append(oid)
                return f"[CEA] Cost estimates for {n} options (e.g. {', '.join(opt_ids)})"
            except Exception:
                return "[CEA] Cost estimates ready."

        # FINAL RECOMMENDATION (if you ever use it again)
        if label == "FINAL RECOMMENDATION":
            try:
                text = str(value)
                preview = text.split("\n", 1)[0]
                return f"[RECO] {preview}"
            except Exception:
                return "[RECO] Final recommendation ready."

        # HTML REPORT
        if label == "HTML REPORT":
            return "[REPORT] HTML report generated. You can download it from the UI."

        # Fallback – in case of new sections
        return f"[{label}] Section ready."

    def chat(self, message, _history=None):
        chunks = []

        for label, value in self.app.ask_stream(message):
            if label == "HTML REPORT":
                # value should be the raw HTML string stored by node_output_formatter
                if hasattr(value, "html"):
                    html_str = value.html
                else:
                    html_str = str(value)

                # Save HTML report
                reports_dir = os.path.join(os.path.dirname(__file__), "reports")
                os.makedirs(reports_dir, exist_ok=True)

                filename = f"sagecompass_report_{int(time.time())}.html"
                file_path = os.path.join(reports_dir, filename)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_str)

                section_text = (
                    "HTML report generated.\n\n"
                    f"Saved to:\n{file_path}\n\n"
                    "Open this file in your browser to view the formatted report."
                )
            else:
                # Use compact summary instead of full JSON
                section_text = self._summarize_chunk(label, value)

            chunks.append(f"=== {label} ===\n{section_text}")
            yield "\n\n".join(chunks)

    def launch(self):
        demo = gr.ChatInterface(
            fn=self.chat,
            title="SageCompass",
            examples=[],
            description="SageCompass reasoning interface",
        )

        demo.launch(
            server_name="0.0.0.0",
            server_port=8000,
            share=False,
            inbrowser=True,
        )
