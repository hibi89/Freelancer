"""Accessible, offline-only owner dashboard HTML. No model calls or external assets."""
from __future__ import annotations

from html import escape
from string import Template

STATES = ("QUEUED", "CODING", "IMPLEMENTED", "REVIEW", "PREPARED", "VERIFIED", "HOLD")
TITLES = {
    "QUEUED": "대기 중", "CODING": "AI 코딩", "IMPLEMENTED": "구현 후보",
    "REVIEW": "독립 검증", "PREPARED": "커밋 준비", "VERIFIED": "검증 통과", "HOLD": "보류",
}
STYLES = r"""
:root{color-scheme:dark;--bg:#090d17;--surface:#131b2b;--surface2:#182338;--line:#263148;--text:#f2f5ff;--muted:#9aa9c1;--accent:#9e91ff;--mint:#65ddbd;--danger:#ff9d9d;--radius:20px;font-family:Inter,Pretendard,'Malgun Gothic',system-ui,-apple-system,sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 81% -10%,#1b2443 0,transparent 43%),var(--bg);color:var(--text)}a{color:inherit;text-decoration:none}button{font:inherit;cursor:pointer}button:disabled{cursor:not-allowed;opacity:.5}a:focus-visible,button:focus-visible{outline:3px solid var(--mint);outline-offset:4px}svg{display:block} .shell{display:grid;grid-template-columns:246px minmax(0,1fr);min-height:100vh}.side{background:#0d1422;border-right:1px solid var(--line);padding:31px 20px;display:flex;flex-direction:column;gap:38px}.brand{display:flex;align-items:center;gap:11px;padding:0 10px}.brandmark{display:grid;place-items:center;width:43px;height:43px;border-radius:14px;background:linear-gradient(140deg,#a694ff,#5a9fff);color:#101525;font-weight:900;font-size:20px;box-shadow:0 8px 26px #8166ff35}.brand-title{font-size:16px;font-weight:800;letter-spacing:-.45px}.brand-sub{font-size:10px;font-weight:700;color:var(--muted);letter-spacing:1.65px;margin-top:4px}.nav-label{font-size:10px;color:#697996;letter-spacing:1.8px;font-weight:800;margin:0 12px 11px}.nav{display:grid;gap:5px}.nav a{padding:13px 14px;border-radius:12px;color:#aab7ce;font-size:13px;font-weight:650;display:flex;align-items:center;gap:12px}.nav a.active{color:#f6f6ff;background:#232545;box-shadow:inset 3px 0 var(--accent)}.nav a:hover{background:#1e2940}.nav i{width:18px;height:18px;border:1.5px solid currentColor;border-radius:5px;display:inline-block;opacity:.75}.side-foot{margin-top:auto;background:#141e30;border:1px solid #29354d;border-radius:15px;padding:17px}.side-foot small{color:var(--muted);display:block;font-size:11px;line-height:1.7}.side-foot strong{font-size:12px;color:var(--mint);display:block;margin-bottom:6px}.content{padding:36px clamp(22px,5vw,74px) 46px;max-width:1550px;width:100%;margin:0 auto}.top{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:29px}.eyebrow{font-size:10px;letter-spacing:2.15px;color:var(--accent);font-weight:800}.top h1{font-size:clamp(24px,2.4vw,33px);letter-spacing:-1px;margin:7px 0 0;font-weight:800}.top-actions{display:flex;align-items:center;gap:12px}.pill{display:inline-flex;align-items:center;gap:8px;border:1px solid #35405a;border-radius:999px;padding:9px 13px;font-size:11px;color:#c1cee0;font-weight:750}.dot{width:7px;height:7px;border-radius:50%;background:var(--mint);box-shadow:0 0 0 4px #65ddbd18}.refresh{padding:10px 15px;border-radius:11px;border:1px solid #37445c;background:#1b2639;font-size:12px;font-weight:750}.refresh:hover{background:#273650}.hero{display:flex;align-items:center;justify-content:space-between;gap:25px;overflow:hidden;position:relative;background:linear-gradient(115deg,#292458 0%,#202648 52%,#132f46 100%);border:1px solid #47477d;border-radius:23px;padding:29px 32px;margin-bottom:22px}.hero:after{content:'';position:absolute;right:-96px;top:-130px;width:360px;height:360px;border:1px solid #ffffff18;border-radius:50%;box-shadow:0 0 0 45px #ffffff05,0 0 0 94px #ffffff05;pointer-events:none}.hero-copy{position:relative;z-index:1}.hero-kicker{font-size:10px;letter-spacing:1.8px;color:#b6b2ff;font-weight:800}.hero h2{font-size:clamp(19px,2.1vw,26px);letter-spacing:-.7px;margin:11px 0 9px}.hero p{color:#c9d2e7;font-size:12px;line-height:1.8;max-width:570px;margin:0}.hero-status{position:relative;z-index:1;white-space:nowrap;display:grid;gap:5px;justify-items:end}.hero-status small{color:#cbd1ee;font-size:10px;letter-spacing:1px}.hero-status strong{font-size:23px;letter-spacing:1px;color:var(--mint)}.hero-status strong.paused{color:#ffc181}.section-title{display:flex;align-items:end;justify-content:space-between;gap:12px;margin:27px 0 13px}.section-title h2{font-size:15px;letter-spacing:-.3px;margin:0}.section-title small{font-size:11px;color:var(--muted)}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px}.metric{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:20px;min-height:130px}.metric-label{font-size:12px;color:#acbad0;font-weight:650}.metric-number{font-size:31px;letter-spacing:-1.4px;font-weight:800;margin:14px 0 7px;font-variant-numeric:tabular-nums}.metric-hint{font-size:10px;color:#7f91ad}.metric.accent .metric-number{color:#a79fff}.metric.green .metric-number{color:var(--mint)}.metric.red .metric-number{color:var(--danger)}.columns{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(280px,.9fr);align-items:start;gap:17px}.panel{background:var(--surface);border:1px solid var(--line);border-radius:19px;overflow:hidden}.panel-header{padding:21px 24px 17px;display:flex;justify-content:space-between;align-items:center;gap:10px;border-bottom:1px solid #273149}.panel-header h3{font-size:14px;letter-spacing:-.3px;margin:0}.panel-header span{font-size:10px;color:#98a8c1}.bar-area{padding:23px 24px}.bar-track{height:10px;border-radius:99px;background:#26334c;overflow:hidden}.bar-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,#8379fc,#62dec7)}.bar-labels{display:flex;justify-content:space-between;gap:10px;margin-top:13px;color:#a7b6cd;font-size:11px}.bar-labels strong{color:#e7eeff}.stages{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:26px}.stage{border:1px solid #2b3851;border-radius:12px;background:#172136;padding:13px 8px;text-align:center}.stage strong{font-size:18px;display:block;font-variant-numeric:tabular-nums}.stage small{font-size:10px;color:#8d9fb9;display:block;margin-top:6px}.stage.done{border-color:#326458}.stage.done strong{color:var(--mint)}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;text-align:left;font-size:12px}th{color:#8496b2;text-transform:uppercase;font-size:10px;letter-spacing:1px;font-weight:750}td,th{padding:14px 23px;border-bottom:1px solid #233048}tr:last-child td{border-bottom:0}td:first-child{font-weight:740;color:#e1eaff}td{color:#a8b8d0}.status{display:inline-flex;padding:6px 9px;border-radius:8px;font-size:10px;font-weight:800;white-space:nowrap;background:#25314b;color:#c8d5ee}.status.verified{background:#163d37;color:#73e6c1}.status.hold{background:#432b37;color:#ff9caa}.status.coding,.status.review{background:#302b50;color:#c2b5ff}.empty{text-align:center;padding:29px 15px;color:#8799b5}.controls{padding:22px 24px}.control-sub{font-size:12px;color:#a2b1c9;line-height:1.75;margin:0 0 20px}.action{width:100%;border-radius:12px;padding:13px 15px;border:1px solid #4c5670;background:#25314a;color:#f7f9ff;font-size:12px;font-weight:800;margin-top:10px;text-align:center}.action.stop{background:#41313c;border-color:#78495e;color:#ffc5c9}.action.resume{background:#224a46;border-color:#2b7065;color:#a7f1db}.action:not(:disabled):hover{filter:brightness(1.15)}.action-note{display:block;margin-top:17px;color:#8193af;font-size:10px;line-height:1.75}.risk-list{list-style:none;margin:0;padding:2px 24px 17px}.risk-list li{padding:12px 0;border-bottom:1px solid #263148;display:flex;justify-content:space-between;gap:10px;align-items:center;font-size:11px}.risk-list li:last-child{border-bottom:0}.risk-list span{color:#adbad0}.risk-list b{font-weight:800;color:#86dac9}.risk-list b.unknown{color:#e5bf82}.foot{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;color:#687c99;font-size:10px;padding-top:28px}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
@media(max-width:1150px){.shell{grid-template-columns:190px 1fr}.side{padding:25px 12px}.content{padding:28px 25px}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.columns{grid-template-columns:1fr}}
@media(max-width:690px){.shell{display:block}.side{border-right:0;border-bottom:1px solid var(--line);display:block;padding:14px 20px}.brand{padding:0}.side .nav,.nav-label,.side-foot{display:none}.content{padding:24px 15px}.hero{padding:22px;display:block}.hero-status{justify-items:start;margin-top:19px}.metrics{gap:9px}.metric{padding:16px;min-height:115px}.metric-number{font-size:26px}.stages{grid-template-columns:repeat(2,1fr)}.top-actions{width:100%;justify-content:space-between}td,th{padding:13px 15px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

PAGE = Template("""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#090d17"><title>AX Dev Factory | Owner Console</title><style>$css</style></head>
<body><div class="shell">
<aside class="side"><div class="brand"><div class="brandmark" aria-hidden="true">AX</div><div><div class="brand-title">AX Dev Factory</div><div class="brand-sub">LOCAL AI STUDIO</div></div></div>
<div><div class="nav-label">WORKSPACE</div><nav class="nav" aria-label="섹션 이동"><a href="#overview" class="active"><i aria-hidden="true"></i> 대시보드</a><a href="#pipeline"><i aria-hidden="true"></i> 작업 파이프라인</a><a href="#tasks"><i aria-hidden="true"></i> 작업 목록</a><a href="#controls"><i aria-hidden="true"></i> 실행 제어</a><a href="#safety"><i aria-hidden="true"></i> 안전 상태</a></nav></div>
<div class="side-foot"><strong>● 로컬 전용 환경</strong><small>외부 서버 연결 없이 내 PC에서 작업을 관리합니다. 이 화면에서 AI 실행이나 GitHub 게시를 시작하지 않습니다.</small></div></aside>
<main class="content" id="overview">
<header class="top"><div><div class="eyebrow">CONTROL CENTER / OWNER VIEW</div><h1>워크스페이스 개요</h1></div><div class="top-actions"><span class="pill"><span class="dot"></span>$mode</span><a class="refresh" href="$refresh_href" aria-label="$refresh_label">↻ $refresh_label</a></div></header>
<section class="hero" aria-labelledby="hero-title"><div class="hero-copy"><div class="hero-kicker">AUTONOMOUS DEVELOPMENT ENGINE</div><h2 id="hero-title">나만의 로컬 AI 개발 시스템</h2><p>승인된 작업 계약을 기준으로 코딩, 독립 검증, 복구를 관리합니다. 이 화면은 저장된 체크포인트를 표시하며 모델 실행 여부를 추정하지 않습니다.</p></div><div class="hero-status"><small>다음 작업 실행 허용 신호</small><strong class="$paused_class" aria-live="polite">$queue_status</strong></div></section>
<section id="pipeline" aria-labelledby="metrics-title"><div class="section-title"><h2 id="metrics-title">실행 현황</h2><small>로컬 SQLite 상태 기준 · 공식 검증 완료율과 별개</small></div><div class="metrics">
<div class="metric"><div class="metric-label">등록된 작업</div><div class="metric-number">$total</div><div class="metric-hint">현재 로컬 큐 전체</div></div>
<div class="metric green"><div class="metric-label">독립 검증 통과</div><div class="metric-number">$verified</div><div class="metric-hint">VERIFIED 체크포인트</div></div>
<div class="metric accent"><div class="metric-label">진행 중 · 대기</div><div class="metric-number">$pending</div><div class="metric-hint">보류·검증 통과 제외</div></div>
<div class="metric red"><div class="metric-label">검토 필요한 작업</div><div class="metric-number">$held</div><div class="metric-hint">HOLD 체크포인트</div></div>
</div></section>
<div class="columns"><div>
<section class="panel" aria-labelledby="progress-title" style="margin-top:20px"><div class="panel-header"><h3 id="progress-title">검증된 작업 비율</h3><span>작업별 로컬 상태</span></div><div class="bar-area"><div class="bar-track" role="progressbar" aria-label="VERIFIED 작업 비율" aria-valuenow="$percent" aria-valuemin="0" aria-valuemax="100"><div class="bar-fill" style="width:$percent%"></div></div><div class="bar-labels"><span>검증 완료 <strong>$verified / $total</strong></span><strong>$percent%</strong></div><div class="stages"><div class="stage"><strong>$queued</strong><small>대기 중</small></div><div class="stage"><strong>$active</strong><small>코딩 · 검증</small></div><div class="stage done"><strong>$verified</strong><small>VERIFIED</small></div><div class="stage"><strong>$held</strong><small>HOLD</small></div></div></div></section>
<section class="panel" id="tasks" aria-labelledby="tasks-title" style="margin-top:17px"><div class="panel-header"><h3 id="tasks-title">작업 목록</h3><span>최대 12개 표시 · 식별자만 공개</span></div><div class="table-wrap"><table><caption class="sr-only">현재 저장된 작업 ID와 체크포인트 상태</caption><thead><tr><th scope="col">작업 ID</th><th scope="col">상태</th></tr></thead><tbody>$task_rows</tbody></table></div>$extra</section>
</div><div>
<section class="panel" id="controls" aria-labelledby="controls-title" style="margin-top:20px"><div class="panel-header"><h3 id="controls-title">실행 제어</h3><span>오너 확인 필요</span></div><div class="controls"><p class="control-sub">현재 실행 중인 작업은 안전한 경계에서 종료하도록 요청할 수 있습니다. 재개는 중지 신호만 해제하며 모델을 실행하지 않습니다.</p>
<form method="post" action="/stop"><input type="hidden" name="csrf" value="$csrf"><button class="action stop" type="submit" $stop_disabled>■ 다음 작업부터 중지</button></form>
<form method="post" action="/resume"><input type="hidden" name="csrf" value="$csrf"><button class="action resume" type="submit" $resume_disabled>↻ 중지 신호 해제</button></form>
<small class="action-note">실행은 별도의 승인된 로컬 큐 또는 Windows 예약 작업에서만 진행합니다. 버튼으로 코딩·결제·배포가 시작되지 않습니다.</small></div></section>
<section class="panel" id="safety" aria-labelledby="safety-title" style="margin-top:17px"><div class="panel-header"><h3 id="safety-title">안전·실행 정보</h3><span>읽기 전용 정보</span></div><ul class="risk-list"><li><span>네트워크 노출</span><b>127.0.0.1 한정</b></li><li><span>이 화면의 모델 실행</span><b>사용 안 함</b></li><li><span>현재 모델 실행 여부</span><b class="unknown">확인되지 않음</b></li><li><span>실행 이벤트 기록 수</span><b>$events</b></li><li><span>실사용 최종 인수</span><b class="unknown">별도 승인</b></li></ul></section>
</div></div><footer class="foot"><span>AX Dev Factory · Owner Control · 무료 로컬 실행</span><span>원본·비밀정보 표시 없음 · 자동 새로고침 없음</span></footer>
</main></div></body></html>""")


def render_dashboard(state: dict, csrf: str, *, preview: bool = False) -> str:
    """Render only bounded task IDs/statuses; never expose settings or source code."""
    counts = state.get("counts", {})
    values = {key: max(0, int(counts.get(key, 0))) for key in STATES}
    total = sum(values.values())
    verified, held = values["VERIFIED"], values["HOLD"]
    percent = round(100 * verified / total) if total else 0
    tasks = state.get("tasks", {})
    if not isinstance(tasks, dict):
        tasks = {}
    rows = []
    for task_id, status in sorted(tasks.items(), key=lambda item: str(item[0]))[:12]:
        label = TITLES.get(status, "상태 미확인")
        cls = status.lower() if status in STATES else "unknown"
        rows.append("<tr><td>" + escape(str(task_id), quote=True) +
                    "</td><td><span class='status " + cls + "'>" +
                    escape(label) + "</span></td></tr>")
    if not rows:
        rows = ["<tr><td class='empty' colspan='2'>등록된 작업이 없습니다. 승인된 로컬 큐 설정을 확인하세요.</td></tr>"]
    paused = bool(state.get("stop_requested"))
    # A static product preview is never an operational control surface.
    disabled = "disabled aria-disabled='true'" if preview else ""
    return PAGE.substitute(
        css=STYLES,
        mode="제품 미리보기 · 합성 데이터" if preview else "127.0.0.1 · 로컬 연결",
        refresh_href="#overview" if preview else "/",
        refresh_label="미리보기" if preview else "새로고침",
        queue_status="PAUSED" if paused else "ELIGIBLE",
        paused_class="paused" if paused else "",
        total=total, verified=verified, pending=total - verified - held, held=held,
        percent=percent, queued=values["QUEUED"],
        active=sum(values[key] for key in ("CODING", "IMPLEMENTED", "REVIEW", "PREPARED")),
        task_rows="".join(rows),
        extra=("<p class='control-sub' style='padding:0 23px'>외 " + str(len(tasks) - 12) +
               "개 작업은 로컬 CLI로 확인하세요.</p>") if len(tasks) > 12 else "",
        csrf=escape(csrf if not preview else "preview-disabled", quote=True),
        stop_disabled="disabled aria-disabled='true'" if paused or preview else disabled,
        resume_disabled="disabled aria-disabled='true'" if not paused or preview else disabled,
        events=max(0, int(state.get("events_recorded", 0))),
    )
