from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


@dataclass
class TestCaseResult:
    name: str
    classname: str
    status: str
    duration_seconds: str
    details: str


@dataclass
class SuiteReport:
    name: str
    tests: int
    failures: int
    errors: int
    skipped: int
    time_seconds: str
    testcases: list[TestCaseResult]

    @property
    def passed(self) -> int:
        return self.tests - self.failures - self.errors - self.skipped


def _status_and_details(testcase: ET.Element) -> tuple[str, str]:
    failure = testcase.find("failure")
    if failure is not None:
        message = failure.attrib.get("message", "") or (failure.text or "")
        return "FAILED", " ".join(message.strip().split())[:180]

    error = testcase.find("error")
    if error is not None:
        message = error.attrib.get("message", "") or (error.text or "")
        return "ERROR", " ".join(message.strip().split())[:180]

    skipped = testcase.find("skipped")
    if skipped is not None:
        message = skipped.attrib.get("message", "") or (skipped.text or "")
        msg = " ".join(message.strip().split())[:180]
        return "SKIPPED", msg or "Skipped"

    return "PASSED", ""


def _parse_suite(suite: ET.Element, default_name: str) -> SuiteReport:
    testcases: list[TestCaseResult] = []
    for testcase in suite.findall("testcase"):
        status, details = _status_and_details(testcase)
        testcases.append(
            TestCaseResult(
                name=testcase.attrib.get("name", "unknown"),
                classname=testcase.attrib.get("classname", ""),
                status=status,
                duration_seconds=testcase.attrib.get("time", "0"),
                details=details,
            )
        )

    tests = int(suite.attrib.get("tests", str(len(testcases))))
    failures = int(suite.attrib.get("failures", "0"))
    errors = int(suite.attrib.get("errors", "0"))
    skipped = int(suite.attrib.get("skipped", "0"))

    return SuiteReport(
        name=suite.attrib.get("name", default_name),
        tests=tests,
        failures=failures,
        errors=errors,
        skipped=skipped,
        time_seconds=suite.attrib.get("time", "0"),
        testcases=testcases,
    )


def parse_junit(path: Path, default_name: str) -> list[SuiteReport]:
    root = ET.parse(path).getroot()

    if root.tag == "testsuite":
        return [_parse_suite(root, default_name)]

    if root.tag == "testsuites":
        suites = root.findall("testsuite")
        if not suites:
            return [SuiteReport(default_name, 0, 0, 0, 0, "0", [])]
        return [_parse_suite(suite, default_name) for suite in suites]

    return [SuiteReport(default_name, 0, 0, 0, 0, "0", [])]


def _summary_table_data(suite: SuiteReport) -> list[list[str]]:
    return [
        ["Tests", str(suite.tests)],
        ["Passed", str(suite.passed)],
        ["Failures", str(suite.failures)],
        ["Errors", str(suite.errors)],
        ["Skipped", str(suite.skipped)],
        ["Duration (s)", suite.time_seconds],
    ]


def _status_color(status: str) -> str:
    if status == "PASSED":
        return "#2e7d32"
    if status in {"FAILED", "ERROR"}:
        return "#c62828"
    return "#6a1b9a"


def write_pdf(path: Path, title: str, suites: list[SuiteReport]) -> None:
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph("Generated from JUnit XML", styles["Normal"]))
    story.append(Spacer(1, 12))

    for suite in suites:
        story.append(Paragraph(f"Suite: {suite.name}", styles["Heading2"]))

        summary = Table(_summary_table_data(suite), colWidths=[120, 120])
        summary.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2f4f7")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(summary)
        story.append(Spacer(1, 10))

        testcase_rows: list[list[Paragraph]] = [
            [
                Paragraph("Test Name", styles["Heading5"]),
                Paragraph("Class", styles["Heading5"]),
                Paragraph("Result", styles["Heading5"]),
                Paragraph("Duration (s)", styles["Heading5"]),
                Paragraph("Details", styles["Heading5"]),
            ]
        ]

        if suite.testcases:
            for case in suite.testcases:
                testcase_rows.append(
                    [
                        Paragraph(case.name, styles["BodyText"]),
                        Paragraph(case.classname or "-", styles["BodyText"]),
                        Paragraph(
                            f'<font color="{_status_color(case.status)}"><b>{case.status}</b></font>',
                            styles["BodyText"],
                        ),
                        Paragraph(case.duration_seconds, styles["BodyText"]),
                        Paragraph(case.details or "-", styles["BodyText"]),
                    ]
                )
        else:
            testcase_rows.append(
                [
                    Paragraph("No test cases found", styles["BodyText"]),
                    Paragraph("-", styles["BodyText"]),
                    Paragraph("-", styles["BodyText"]),
                    Paragraph("-", styles["BodyText"]),
                    Paragraph("-", styles["BodyText"]),
                ]
            )

        table = Table(testcase_rows, colWidths=[130, 120, 65, 60, 165], repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dfe7fd")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafafa")]),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 16))

    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    doc.build(story)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PDF test summaries from JUnit XML reports.")
    parser.add_argument("--ui-junit", required=True, type=Path)
    parser.add_argument("--api-junit", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    ui_suites = parse_junit(args.ui_junit, "ui")
    api_suites = parse_junit(args.api_junit, "api")

    write_pdf(args.out_dir / "ui-summary.pdf", "UI Test Report", ui_suites)
    write_pdf(args.out_dir / "api-summary.pdf", "API Test Report", api_suites)
    write_pdf(args.out_dir / "combined-summary.pdf", "Combined Test Report", ui_suites + api_suites)


if __name__ == "__main__":
    main()
