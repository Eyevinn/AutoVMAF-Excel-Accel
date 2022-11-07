#!/usr/bin/env python3

import json

from openpyxl import Workbook
from openpyxl.chart import Reference, LineChart
from openpyxl.utils import get_column_letter
from openpyxl.utils.units import pixels_to_EMU
from openpyxl.styles import PatternFill, Border, Side
from openpyxl.formatting.rule import CellIsRule

with open('jobnames.txt', encoding="utf-8") as f:
    jobnames = [line.rstrip() for line in f]

COLORS = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
          '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe',
          '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000',
          '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080',
          '#ffffff', '#000000']

wb = Workbook()

redFill = PatternFill(start_color='ff9494',
                      end_color='ff9494',
                      fill_type='solid')

orangeFill = PatternFill(start_color='ffcf94',
                         end_color='ffcf94',
                         fill_type='solid')

greenFill = PatternFill(start_color='d3eeb4',
                        end_color='d3eeb4',
                        fill_type='solid')

border_style = Side(border_style="medium", color="336a15")
border = Border(top=border_style, bottom=border_style,
                left=border_style, right=border_style)


for jobname in jobnames:
    with open(f"./results/{jobname}.json", encoding="utf-8") as f:
        the_file = json.load(f)
    jobname_trunc = jobname[:31]
    heights = []
    bitrates = []
    resolutions = []

    with open(f"./results/{jobname}_ladder.json", encoding="utf-8") as f:
        the_ladder = json.load(f)

    for model in the_file["result"][jobname]:
        results = the_file["result"][jobname][model]

        if len(results) > 0:
            r = []
            for entry in results:
                e = {}
                res, bitrate = entry.split("_")[:2]
                e["res"] = res
                width, height = res.split("x")
                e["width"] = int(width)
                e["height"] = int(height)
                e["bitrate"] = int(bitrate)
                e["model"] = model
                e["score"] = float(results[entry])
                e["jobname"] = jobname
                heights.append(int(height))
                bitrates.append(int(bitrate))
                resolutions.append(res)
                r.append(e)

            scores = sorted(r, key=lambda i: (i["height"], i["bitrate"]))
            heights = sorted(list(set(heights)))
            bitrates = sorted(list(set(bitrates)))
            resolutions = sorted(
                list(set(resolutions)), key=lambda x: int(x.split("x")[1])
            )

    if wb.sheetnames[0] == "Sheet":
        wb.remove(wb.active)

    ws = wb.create_sheet(jobname_trunc)

    table = [["Kbit/s"] + resolutions]

    for b in bitrates:
        row = [b/1000]
        for h in heights:
            matches = [
                item
                for item in scores
                if (item["bitrate"] == b and item["height"] == h)
            ]

            if len(matches) > 0 and matches[0]["bitrate"] == b:
                row.append(matches[0]["score"])
            else:
                row.append("")
        table.append(row)

    for row in table:
        ws.append(row)

    COLUMN_LIST = [get_column_letter(cell.column) for cell in ws[1]]
    RANGE_STRING = f'{jobname_trunc}!A1:{COLUMN_LIST[-1]}{str(len(table))}'
    OFFSET = 10
    ws.move_range(RANGE_STRING, rows=0, cols=OFFSET)

    MIN_COL = 2 + OFFSET
    MIN_ROW = 1
    MAX_COL = len(resolutions) + 1+OFFSET
    MAX_ROW = len(table)

    values = Reference(
        ws, min_col=MIN_COL, min_row=MIN_ROW, max_col=MAX_COL, max_row=MAX_ROW
    )

    OFFSET_COL = chr(ord('A') + OFFSET)
    RANGE_STRING = f'{jobname_trunc}!{OFFSET_COL}2:{OFFSET_COL}{str(len(table))}'
    X_VALUES = Reference(ws, range_string=RANGE_STRING)

    chart = LineChart()
    chart.add_data(values, titles_from_data=True)
    chart.set_categories(X_VALUES)

    # cosmetics
    chart.title = jobname
    chart.height = 17
    chart.width = 25
    chart.style = 2
    chart.legend.position = "b"
    chart.x_axis.title = "Bitrate in Kbit/s"
    chart.y_axis.title = "VMAF Score"
    chart.y_axis.scaling.min = 0
    chart.y_axis.scaling.max = 100

    for i, line in enumerate(chart.series):
        line.graphicalProperties.line.width = pixels_to_EMU(4)
        line.graphicalProperties.line.solidFill = COLORS[i][1:]
        line.marker.graphicalProperties.solidFill = COLORS[i][1:]
        line.marker.symbol = "diamond"
        line.marker.size = 4

    ws.add_chart(chart, "A1")
    ACTIVE_COLUMN_LIST = [get_column_letter(cell.column) for cell in ws[1]]

    for letter in ACTIVE_COLUMN_LIST:
        ws.column_dimensions[letter].width = 12

    NEW_START_COL = chr(ord('A') + OFFSET + 1)
    DATA_RANGE = f'{NEW_START_COL}2:{ACTIVE_COLUMN_LIST[-1]}{str(len(table))}'

    ws.conditional_formatting.add(DATA_RANGE,
                                  CellIsRule(
                                      operator='between',
                                      formula=[93.0, 94.0],
                                      stopIfTrue=True,
                                      fill=orangeFill))
    ws.conditional_formatting.add(DATA_RANGE,
                                  CellIsRule(
                                      operator='between',
                                      formula=[0.1, 20],
                                      stopIfTrue=True,
                                      fill=orangeFill))
    ws.conditional_formatting.add(DATA_RANGE,
                                  CellIsRule(
                                      operator='greaterThanOrEqual',
                                      formula=[94.0],
                                      stopIfTrue=True,
                                      fill=redFill))

    autoladder = [["Auto-Ladder", "", ""]]

    for ladder in the_ladder:
        w = ladder["resolution"]["width"]
        h = ladder["resolution"]["height"]

        row = [f'{w}x{h}', ladder["bitrate"]/1000, ladder["vmaf"]]
        autoladder.append(row)

    scores = [s[2] for s in autoladder]

    for row in ws.rows:
        for cell in row:
            if cell.value is not (None or "") and cell.value in scores:
                cell.fill = greenFill
                cell.border = border

    for row in autoladder:
        ws.append(row)


wb.save("vmaf.xlsx")

print("File generated")
