"""Korean buyer-facing GUI headings, with unchanged internal data keys."""
from __future__ import annotations

import unittest

from worknova_desk.gui import COLUMN_LABELS


class KoreanGuiHeadings(unittest.TestCase):
    def test_all_business_table_columns_have_korean_titles(self):
        table_columns = (
            ('name', 'id'),
            ('revision', 'status', 'total_krw', 'id'),
            ('status', 'scope', 'id'),
            ('title', 'status', 'amount_krw', 'id'),
        )
        for columns in table_columns:
            for key in columns:
                with self.subTest(column=key):
                    self.assertIn(key, COLUMN_LABELS)
                    self.assertNotEqual(COLUMN_LABELS[key], key)
                    self.assertTrue(any('가' <= ch <= '힣' for ch in COLUMN_LABELS[key]))

    def test_internal_primary_key_names_remain_stable(self):
        self.assertEqual(set(COLUMN_LABELS),
                         {'name', 'id', 'revision', 'status', 'total_krw',
                          'scope', 'title', 'amount_krw'})


if __name__ == '__main__':
    unittest.main()
