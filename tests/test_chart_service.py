from unittest import TestCase

from app import chart_service
from app.model.wakatime.wakatime_item_dto import WakatimeItemDto


class ChartServiceTest(TestCase):

    chart_service = chart_service

    def test_should_group_projects(self):
        test_data: list[WakatimeItemDto] = _get_test_data()
        test_group: dict[str, set[str]] | None = {
            "Other": {"HTTP Request", "YAML", "Markdown", "SQL"},
        }
        expected: list[WakatimeItemDto] = [
            WakatimeItemDto(
                total_seconds=38576.259,
                name="Java",
                percent=39.35,
                digital="10:42",
                decimal="10.70",
                text="10 hrs 42 mins",
                minutes=42,
                hours=10,
            ),
            WakatimeItemDto(
                total_seconds=17150,
                name="Python",
                percent=17.5,
                digital="4:45",
                decimal="4.75",
                text="4 hrs 45 mins",
                minutes=45,
                hours=4,
            ),
            WakatimeItemDto(
                total_seconds=16847.673,
                name="Other",
                percent=17.24,
                digital="4:39",
                decimal="4.65",
                text="4 hrs 39 mins",
                minutes=39,
                hours=4,
            ),
            WakatimeItemDto(
                total_seconds=10638.081,
                name="Vue.js",
                percent=10.85,
                digital="2:57",
                decimal="2.95",
                text="2 hrs 57 mins",
                minutes=57,
                hours=2,
            ),
            WakatimeItemDto(
                total_seconds=2348,
                name="Lua",
                percent=2.4,
                digital="0:39",
                decimal="0.65",
                text="39 mins",
                minutes=39,
                hours=0,
            ),
        ]

        actual: list[WakatimeItemDto] = chart_service._group(test_data, test_group)  # type: ignore[all]

        self.assertEqual(actual, expected)

    def test_should_not_group_projects(self):
        test_data = _get_test_data()
        expected = test_data

        actual = chart_service._group(test_data, None)

        self.assertEqual(expected, actual)


def _get_test_data() -> list[WakatimeItemDto]:
    test_data: list[WakatimeItemDto] = [
        WakatimeItemDto(
            total_seconds=38576.259,
            name="Java",
            percent=39.35,
            digital="10:42",
            decimal="10.70",
            text="10 hrs 42 mins",
            minutes=42,
            hours=10,
        ),
        WakatimeItemDto(
            total_seconds=17150,
            name="Python",
            percent=17.5,
            digital="4:45",
            decimal="4.75",
            text="4 hrs 45 mins",
            minutes=45,
            hours=4,
        ),
        WakatimeItemDto(
            total_seconds=10638.081,
            name="Vue.js",
            percent=10.85,
            digital="2:57",
            decimal="2.95",
            text="2 hrs 57 mins",
            minutes=57,
            hours=2,
        ),
        WakatimeItemDto(
            total_seconds=5746.943,
            name="HTTP Request",
            percent=5.86,
            digital="1:35",
            decimal="1.58",
            text="1 hrs 35 mins",
            minutes=35,
            hours=1,
        ),
        WakatimeItemDto(
            total_seconds=4533.516,
            name="YAML",
            percent=4.68,
            digital="1:15",
            decimal="1.25",
            text="1 hrs 15 mins",
            minutes=15,
            hours=1,
        ),
        WakatimeItemDto(
            total_seconds=4326.793,
            name="Markdown",
            percent=4.41,
            digital="1:12",
            decimal="1.20",
            text="1 hrs 12 mins",
            minutes=12,
            hours=1,
        ),
        WakatimeItemDto(
            total_seconds=2348,
            name="Lua",
            percent=2.4,
            digital="0:39",
            decimal="0.65",
            text="39 mins",
            minutes=39,
            hours=0,
        ),
        WakatimeItemDto(
            total_seconds=2240.421,
            name="SQL",
            percent=2.29,
            digital="0:37",
            decimal="0.62",
            text="37 mins",
            minutes=37,
            hours=0,
        ),
    ]
    return test_data
