"""Owner UI renderer safety and accessible-state tests, no network/AI calls."""
import unittest

from owner_dashboard_view import render_dashboard


class DashboardViewTests(unittest.TestCase):
    def sample(self, **overrides):
        result = {
            "counts": {"QUEUED": 2, "VERIFIED": 3, "HOLD": 1, "CODING": 1},
            "tasks": {"TASK-001": "VERIFIED", "TASK-002": "HOLD"},
            "events_recorded": 19,
            "stop_requested": False,
        }
        result.update(overrides)
        return result

    def test_live_metrics_and_refresh(self):
        page = render_dashboard(self.sample(), "synthetic-csrf")
        self.assertIn('<html lang="ko">', page)
        self.assertIn('aria-valuenow="43"', page)
        self.assertIn('<div class="metric-number">7</div>', page)
        self.assertIn('127.0.0.1 · 로컬 연결', page)
        self.assertIn('href="/" aria-label="새로고침"', page)
        self.assertIn('method="post" action="/stop"', page)
        self.assertIn('method="post" action="/resume"', page)
        self.assertIn('value="synthetic-csrf"', page)
        self.assertIn('공식 검증 완료율과 별개', page)

    def test_escape_task_ids_and_token(self):
        page = render_dashboard(self.sample(tasks={'<script>x</script>': 'VERIFIED'}), '" onfocus="evil')
        self.assertNotIn('<script>x</script>', page)
        self.assertIn('&lt;script&gt;x&lt;/script&gt;', page)
        self.assertIn('value="&quot; onfocus=&quot;evil"', page)

    def test_paused_disables_stop_and_allows_resume(self):
        page = render_dashboard(self.sample(stop_requested=True), 's')
        self.assertIn('PAUSED', page)
        self.assertIn('type="submit" disabled aria-disabled=\'true\'>■ 다음 작업부터 중지', page)
        self.assertIn('type="submit" >↻ 중지 신호 해제', page)

    def test_preview_is_offline_and_non_operational(self):
        page = render_dashboard(self.sample(), 'real-token', preview=True)
        self.assertNotIn('real-token', page)
        self.assertIn('제품 미리보기 · 합성 데이터', page)
        self.assertIn('href="#overview" aria-label="미리보기"', page)
        self.assertEqual(page.count("disabled aria-disabled='true'"), 2)

    def test_empty_queue_and_unknown_model_state(self):
        page = render_dashboard({'counts': {}, 'tasks': {}, 'events_recorded': 0}, 'x')
        self.assertIn('aria-valuenow="0"', page)
        self.assertIn('등록된 작업이 없습니다', page)
        self.assertIn('확인되지 않음', page)


if __name__ == '__main__':
    unittest.main()
