from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from flask import Flask, jsonify, render_template_string, request

from outreach_pipeline import (
    add_prospect,
    generate_outreach_email,
    list_due_followups,
    load_prospects,
    pipeline_summary,
    update_status,
)

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Outreach Pipeline Dashboard</title>
    <style>
      :root {
        --bg: #09111c;
        --bg-soft: #101b2b;
        --card: rgba(15, 24, 36, 0.92);
        --card-soft: rgba(17, 28, 43, 0.78);
        --primary: #8ef2c8;
        --primary-strong: #52d7a3;
        --secondary: #c7d3ff;
        --text: #ecf4ff;
        --muted: #a7b7cc;
        --line: rgba(142, 242, 200, 0.15);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: Inter, Arial, sans-serif;
        background: radial-gradient(circle at top, rgba(94, 121, 255, 0.18), transparent 30%), linear-gradient(180deg, #09111c 0%, #0b1220 100%);
        color: var(--text);
      }
      .container {
        width: min(1200px, calc(100% - 32px));
        margin: 0 auto;
      }
      .topbar {
        background: rgba(9,17,28,0.8);
        border-bottom: 1px solid var(--line);
        backdrop-filter: blur(10px);
        position: sticky;
        top: 0;
        z-index: 10;
      }
      .nav {
        min-height: 72px;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .brand { display: flex; align-items: center; gap: 10px; font-weight: 800; }
      .brand-mark {
        width: 28px; height: 28px; border-radius: 8px; display: inline-grid; place-items: center;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%); color: #07111a; font-size: 13px; font-weight: 900;
      }
      main { padding: 32px 0 64px; }
      .grid { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 24px; }
      .card {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 20px;
        box-shadow: 0 18px 36px rgba(6, 10, 17, 0.34);
      }
      .summary {
        display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px; margin-bottom: 24px;
      }
      .summary-item {
        padding: 20px 18px; background: var(--card-soft); border: 1px solid var(--line); border-radius: 18px; text-align: center;
      }
      .summary-item strong { display: block; font-size: 2rem; margin-top: 8px; }
      .panel { padding: 20px; }
      table { width: 100%; border-collapse: collapse; margin-top: 16px; }
      th, td { text-align: left; padding: 12px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
      th { color: var(--muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; }
      .pill {
        display: inline-block; border-radius: 999px; padding: 6px 10px; font-size: 0.77rem; font-weight: 700;
        background: rgba(142, 242, 200, 0.12); color: var(--primary);
      }
      form { display: grid; gap: 14px; }
      label { display: grid; gap: 8px; font-weight: 600; color: var(--muted); }
      input, select, textarea, button {
        width: 100%; border-radius: 12px; border: 1px solid var(--line); padding: 0.8rem 0.9rem; font: inherit;
      }
      input, select, textarea { background: rgba(255,255,255,0.02); color: var(--text); }
      button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%); color: #07111a; border: 0; cursor: pointer; font-weight: 800; border-radius: 999px;
        transition: transform 0.15s ease;
      }
      button:hover { transform: translateY(-1px); }
      .row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      .email-box {
        margin-top: 20px; padding: 18px; background: rgba(255,255,255,0.02); border: 1px solid var(--line); border-radius: 14px; white-space: pre-wrap;
        color: var(--text); line-height: 1.6;
      }
      .list { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
      .list li { border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; background: rgba(255,255,255,0.02); }
      .muted { color: var(--muted); }
      .hidden { display: none; }
      @media (max-width: 900px) { .grid, .summary { grid-template-columns: 1fr; } }
    </style>
  </head>
  <body>
    <header class="topbar">
      <div class="container nav">
        <div class="brand">
          <span class="brand-mark">S</span>
          <span>Sundai Outreach Lab</span>
        </div>
      </div>
    </header>

    <main>
      <div class="container">
        <section style="margin-bottom: 24px; padding: 22px 20px; border: 1px solid var(--line); border-radius: 20px; background: rgba(142,242,200,0.04);">
          <div class="muted" style="text-transform: uppercase; letter-spacing: 0.14em; font-size: 11px; font-weight: 800;">Sunday build cycle</div>
          <h2 style="margin: 12px 0 6px; font-size: clamp(2rem, 3vw, 2.8rem); letter-spacing: -0.05em;">Build, ship, and share what matters.</h2>
          <p class="muted" style="margin: 0; max-width: 760px; line-height: 1.7;">
            Sundai runs like a hacker club: prototypes are tested weekly, public demos are shipped fast, and every outreach thread becomes a reusable system for the next build.
          </p>
        </section>

        <section class="summary" id="summary"></section>

        <div class="grid">
          <section class="card panel">
            <h2>Prospects</h2>
            <table>
              <thead>
                <tr>
                  <th>Organization</th>
                  <th>Officer</th>
                  <th>Stage</th>
                  <th>Priority</th>
                  <th>Next follow-up</th>
                </tr>
              </thead>
              <tbody id="prospect-table-body"></tbody>
            </table>
          </section>

          <aside class="card panel">
            <h2>Add prospect</h2>
            <form id="prospect-form">
              <div class="row">
                <label>
                  Name
                  <input name="name" required />
                </label>
                <label>
                  Organization
                  <input name="organization" required />
                </label>
              </div>
              <div class="row">
                <label>
                  Website
                  <input name="website" type="url" required />
                </label>
                <label>
                  Program officer
                  <input name="officer" required />
                </label>
              </div>
              <label>
                Mission fit
                <textarea name="mission_fit" rows="3" placeholder="e.g. Youth opportunity and local resilience"></textarea>
              </label>
              <label>
                Focus areas (comma-separated)
                <input name="focus_areas" placeholder="community health, food access" />
              </label>
              <div class="row">
                <label>
                  Priority
                  <select name="priority">
                    <option value="high">High</option>
                    <option value="medium" selected>Medium</option>
                    <option value="low">Low</option>
                  </select>
                </label>
                <label>
                  Stage
                  <select name="stage">
                    <option value="new" selected>New</option>
                    <option value="contacted">Contacted</option>
                    <option value="follow_up">Follow-up</option>
                    <option value="reply_received">Reply received</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </label>
              </div>
              <button type="submit">Save prospect</button>
            </form>
          </aside>
        </div>

        <section class="card panel" style="margin-top: 24px;">
          <h2>Follow-up queue</h2>
          <ul id="due-list" class="list"></ul>
        </section>

        <section class="card panel" style="margin-top: 24px;">
          <h2>Email preview</h2>
          <div class="row" style="margin-bottom: 12px;">
            <label>
              Prospect
              <select id="email-prospect"></select>
            </label>
            <label>
              Template
              <select id="email-template">
                <option value="intro">Intro</option>
                <option value="follow_up">Follow-up</option>
              </select>
            </label>
          </div>
          <button id="preview-email" type="button">Generate email</button>
          <div id="email-output" class="email-box hidden"></div>
        </section>
      </div>
    </main>

    <script>
      const summaryEl = document.getElementById('summary');
      const tableBody = document.getElementById('prospect-table-body');
      const dueList = document.getElementById('due-list');
      const emailProspect = document.getElementById('email-prospect');
      const emailOutput = document.getElementById('email-output');
      const prospectForm = document.getElementById('prospect-form');

      async function fetchJson(url, options = {}) {
        const response = await fetch(url, {
          headers: { 'Content-Type': 'application/json' },
          ...options,
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || 'Request failed');
        }
        return data;
      }

      function renderSummary(summary) {
        const cards = [
          { label: 'Total', value: summary.total || 0 },
          { label: 'New', value: summary.new || 0 },
          { label: 'Contacted', value: summary.contacted || 0 },
          { label: 'Follow-up', value: summary.follow_up || 0 },
          { label: 'Replies', value: summary.reply_received || 0 },
        ];

        summaryEl.innerHTML = cards.map(item => `
          <div class="summary-item card">
            <span class="muted">${item.label}</span>
            <strong>${item.value}</strong>
          </div>
        `).join('');
      }

      function renderProspects(prospects) {
        if (!prospects.length) {
          tableBody.innerHTML = '<tr><td colspan="5" class="muted">No prospects yet.</td></tr>';
          return;
        }

        tableBody.innerHTML = prospects.map((prospect) => `
          <tr>
            <td>
              <strong>${prospect.organization}</strong><br>
              <span class="muted">${prospect.name}</span>
            </td>
            <td>${prospect.program_officer || '—'}</td>
            <td><span class="pill">${prospect.stage}</span></td>
            <td>${prospect.priority || 'medium'}</td>
            <td>${prospect.next_follow_up_at || 'Not scheduled'}</td>
          </tr>
        `).join('');

        emailProspect.innerHTML = prospects.map((prospect) => `
          <option value="${prospect.id}">${prospect.organization}</option>
        `).join('');
      }

      function renderDueList(items) {
        if (!items.length) {
          dueList.innerHTML = '<li class="muted">No follow-ups due in the next window.</li>';
          return;
        }

        dueList.innerHTML = items.map((item) => `
          <li>
            <strong>${item.organization}</strong><br>
            <span class="muted">${item.program_officer} • ${item.primary_stage || item.stage} • ${item.next_follow_up_at || 'No date'}</span>
          </li>
        `).join('');
      }

      async function loadData() {
        const prospects = await fetchJson('/api/prospects');
        const summary = await fetchJson('/api/summary');
        const dueItems = await fetchJson('/api/due?days=14');
        renderSummary(summary);
        renderProspects(prospects.prospects || []);
        renderDueList(dueItems || []);
      }

      prospectForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(prospectForm);
        const payload = {
          name: formData.get('name'),
          organization: formData.get('organization'),
          website: formData.get('website'),
          officer: formData.get('officer'),
          stage: formData.get('stage'),
          mission_fit: formData.get('mission_fit') || '',
          focus_areas: (formData.get('focus_areas') || '').split(',').map((value) => value.trim()).filter(Boolean),
          priority: formData.get('priority'),
        };

        await fetchJson('/api/prospects', {
          method: 'POST',
          body: JSON.stringify(payload),
        });

        prospectForm.reset();
        await loadData();
      });

      document.getElementById('preview-email').addEventListener('click', async () => {
        const prospectId = emailProspect.value;
        const template = document.getElementById('email-template').value;
        const response = await fetch(`/api/prospects/${prospectId}/email?template=${template}`);
        const data = await response.json();
        emailOutput.textContent = data.email;
        emailOutput.classList.remove('hidden');
      });

      loadData().catch((error) => {
        console.error(error);
        summaryEl.innerHTML = '<div class="summary-item card"><span class="muted">Error</span><strong>Unable to load dashboard</strong></div>';
      });
    </script>
  </body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/health")
def health():
    return jsonify({"ok": True})


@app.route("/api/prospects")
def prospects():
    return jsonify(load_prospects())


@app.route("/api/prospects", methods=["POST"])
def add_prospect_route():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    organization = (data.get("organization") or "").strip()
    website = (data.get("website") or "").strip()
    officer = (data.get("officer") or "").strip()

    if not name or not organization or not website or not officer:
        return jsonify({"error": "Name, organization, website, and officer are required."}), 400

    prospect = add_prospect(
        name=name,
        organization=organization,
        website=website,
        officer=officer,
        stage=data.get("stage", "new"),
        mission_fit=data.get("mission_fit"),
        focus_areas=data.get("focus_areas") or [],
        priority=data.get("priority", "medium"),
    )
    return jsonify(prospect), 201


@app.route("/api/summary")
def summary():
    return jsonify(pipeline_summary())


@app.route("/api/due")
def due_followups():
    days = int(request.args.get("days", 14))
    return jsonify(list_due_followups(days_ahead=days))


@app.route("/api/prospects/<prospect_id>/email")
def email_preview(prospect_id: str):
    template = request.args.get("template", "intro")
    email = generate_outreach_email(prospect_id=prospect_id, template=template)
    return jsonify({"template": template, "email": email})


@app.route("/api/prospects/<prospect_id>/status", methods=["POST"])
def update_status_route(prospect_id: str):
    data = request.get_json(silent=True) or {}
    updated = update_status(
        prospect_id,
        stage=data.get("stage"),
        status=data.get("status"),
        note=data.get("note"),
        follow_up_days=int(data.get("follow_up_days") or 14),
    )
    return jsonify(updated)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
