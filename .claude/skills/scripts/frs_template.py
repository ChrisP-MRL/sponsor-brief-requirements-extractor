#!/usr/bin/env python3
"""
FRS workbook builder.

Creates the PRJ-Functional Requirements Specification workbook from scratch so
the extractor has no dependency on a binary .xlsx template file. The structure,
styling and reference content below reproduce the MinRes template and follow the
BABOK Guide's requirements classification schema (see
.claude/rules/BABOK_requirements.md):

  Sheet "Instructions"                - title, sheet index, general instructions,
                                        the BABOK requirement-type, NFR-category
                                        and quality-characteristic checklists, and
                                        the Compliance / Priority definitions
  Sheet "Functional Requirements"     - capabilities the solution must have, in
                                        terms of behaviour and the information it
                                        will manage
  Sheet "Non-Functional Requirements" - conditions under which the solution must
                                        remain effective, or qualities it must
                                        have, each with a success measure

Only openpyxl is required.
"""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation


# --- Palette -----------------------------------------------------------------
# The template uses theme-colour fills (White, Background 1, Darker 5/15/25%).
# Those resolve to these greys; hardcoding the RGB keeps output identical
# regardless of the workbook theme.
GREY_5 = 'FFF2F2F2'    # header rows, definition table headers
GREY_15 = 'FFD9D9D9'   # Instructions title band
GREY_25 = 'FFBFBFBF'   # Instructions section headings
TAN = 'FFE0CCB1'       # vendor input columns (COMPLIANCE, COMMENTS, Vendor name)
HEADER_RED = 'FFC00000'

THIN = Side(style='thin')
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

COMPLIANCE_OPTIONS = ['Out of the Box', 'Configuration Required',
                      'Customisation Required', 'Road Map', 'Not Supported', '-']
PRIORITY_OPTIONS = ['Must', 'Should', 'Could', "Won't"]

# --- Sheet specifications ----------------------------------------------------
# Each requirements sheet is described by one dict so styling, dropdowns and the
# extractor all work from the same definition rather than from parallel index
# lists. Alignment and fills are resolved from the column *name*, so adding a
# column to a sheet needs no change to style_requirement_row().
#
# Vendor-input columns are filled tan and left blank for manual completion.
VENDOR_INPUT_COLUMNS = ('COMPLIANCE', 'COMMENTS')

FUNCTIONAL_SHEET = {
    'title': 'Functional Requirements',
    'columns': ['CATEGORY', 'SUB-CATEGORY', 'ID', 'DESCRIPTION',
                'MRL Priority', 'COMPLIANCE', 'COMMENTS'],
    'widths': [28.84, 47.53, 6.38, 68.15, 19.0, 25.38, 51.84],
    'header_row': 1,
    'first_data_row': 2,
    'id_prefix': 'FR',
    'vendor_name_cell': False,
}

NON_FUNCTIONAL_SHEET = {
    'title': 'Non-Functional Requirements',
    'columns': ['CATEGORY', 'SUB-CATEGORY', 'ID', 'DESCRIPTION',
                'SUCCESS MEASURE', 'MRL Priority', 'COMPLIANCE', 'COMMENTS'],
    'widths': [26.0, 34.0, 8.0, 62.0, 46.0, 19.0, 25.38, 40.0],
    # Rows 1-2 carry the vendor name band called for in the general instructions
    'header_row': 4,
    'first_data_row': 5,
    'id_prefix': 'NFR',
    'vendor_name_cell': True,
}

REQUIREMENT_SHEETS = (FUNCTIONAL_SHEET, NON_FUNCTIONAL_SHEET)

# Kept for backwards compatibility with earlier callers that imported these
COLUMNS = FUNCTIONAL_SHEET['columns']
COLUMN_WIDTHS = {'A': 28.84, 'B': 47.53, 'C': 6.38, 'D': 68.15,
                 'E': 19.0, 'F': 25.38, 'G': 51.84, 'H': 9.15}
INPUT_COLUMNS = (6, 7)


# --- BABOK reference content -------------------------------------------------
# BABOK classification schema. Business and stakeholder requirements are not
# specified in this workbook; they are listed so the reader can see where the
# two solution-requirement sheets sit and what each sheet must trace back to.
REQUIREMENT_TYPES = [
    ('Business Requirement',
     'A high-level statement of the goal, objective or need the solution addresses'
     ' - the WHY. Recorded in the Sponsor Brief / business case, not in this workbook.'),
    ('Stakeholder Requirement',
     'A business requirement elaborated by a specific stakeholder group, describing'
     ' how that group will interact with the solution. Bridges business and solution'
     ' requirements.'),
    ('Solution Requirement - Functional',
     'A capability the solution must have, expressed in terms of the behaviour and'
     ' the information the solution will manage - the WHAT. Recorded on the'
     " 'Functional Requirements' sheet."),
    ('Solution Requirement - Non-Functional',
     'A condition under which the solution must remain effective, or a quality the'
     ' solution must have - HOW WELL. Measurable, and a constraint on the design of'
     " the solution as a whole. Recorded on the 'Non-Functional Requirements' sheet."),
    ('Transition Requirement',
     'A capability needed only to move from the current state to the future state'
     ' (migration, training, parallel running). Recorded in the implementation plan,'
     ' not in this workbook.'),
]

# BABOK Guide s10.30 non-functional requirement categories. Used as an elicitation
# checklist and as the controlled vocabulary for the CATEGORY column of the
# Non-Functional Requirements sheet.
NFR_CATEGORIES = [
    ('Availability',
     'The degree to which the solution is operable and accessible when required for'
     ' use, usually expressed as a percentage of a stated period.'),
    ('Compatibility',
     'The degree to which the solution operates effectively with other components in'
     ' its environment - other systems, processes, data standards or devices.'),
    ('Compliance',
     'Legislative, regulatory, audit and standing policy obligations the solution must'
     ' satisfy on an ongoing basis. A strong candidate for reuse across initiatives.'),
    ('Business Continuity',
     'The degree to which the business can continue to operate, and the solution can'
     ' be recovered, during and after a disruption.'),
    ('Functionality',
     'The degree to which the solution functions meet the need - suitability, accuracy'
     ' and interoperability. Quality of the function, not the function itself.'),
    ('Maintainability',
     'The ability to change one component of the solution without affecting other'
     ' components.'),
    ('Operability',
     'The ease with which the solution can be operated, monitored and supported in'
     ' its live environment.'),
    ('Performance Efficiency',
     'The time required to perform activities and the responsiveness of the solution'
     ' under a stated load.'),
    ('Portability',
     'The ability of the solution to be executed in different environments.'),
    ('Reliability',
     'The degree to which the solution remains effective and performs consistently'
     ' and predictably when needed.'),
    ('Scalability',
     'The ability of the solution to absorb growth in volume, users or data without'
     ' breaching its other non-functional targets.'),
    ('Security',
     'The protection of trusted information and of solution resources against'
     ' unauthorised access, disclosure or change.'),
    ('Usability',
     'The degree to which the solution can be used by its intended users to achieve'
     ' their goals effectively, efficiently and with satisfaction, including'
     ' accessibility.'),
]

# BABOK's nine characteristics of requirements quality, used for Verify Requirements
QUALITY_CHARACTERISTICS = [
    ('Atomic', 'Self-contained and expressing a single complete thought, so it can be'
               ' traced, prioritised and tested on its own.'),
    ('Complete', 'Carries enough information for its audience to act on it, with no'
                 ' gap left to interpretation.'),
    ('Consistent', 'Does not contradict any other requirement, and uses the same terms'
                   ' for the same things throughout the set.'),
    ('Concise', 'Stated in plain, brief language with no unnecessary elaboration.'),
    ('Feasible', 'Achievable within the known budget, timeline, technology and'
                 ' resourcing.'),
    ('Unambiguous', 'Open to exactly one reading by every stakeholder.'),
    ('Testable', 'Written so that compliance can be objectively demonstrated. For a'
                 ' non-functional requirement this means a stated success measure.'),
    ('Prioritised', 'Ranked against the others so scope can be traded - see the MRL'
                    ' Priority definitions below.'),
    ('Understandable', 'Expressed in language the intended audience uses, without'
                       ' unexplained jargon.'),
]

COMPLIANCE_DEFINITIONS = [
    ('Out of the Box',
     "Functionality delivered 'Out of the Box' with no additional configuration required"),
    ('Configuration Required',
     'Functionality delivered by configuration changes to existing software modules'),
    ('Customisation Required',
     'Requires changes to the core software to deliver functionality - Not on current product roadmap'),
    ('Road Map for Development',
     'Requires changes to the core software to deliver functionality - On current product roadmap'
     ' - indicate software version and planned delivery date in comments'),
    ('Not Supported',
     'Requirement not supported by the product and no plans to do so'),
    ('-', 'No Response provided'),
]

PRIORITY_DEFINITIONS = [
    ('Must',
     'Must be satisfied in the final solution for it to be considered a success'),
    ('Should',
     'A high-priority item that should be included in the solution if it is possible'
     ' - often a critical requirement but one that could be satisfied in other ways if strictly necessary'),
    ('Could',
     'A requirement which is considered desirable but not necessary - to be included'
     ' if time and resources permit (nice to have)'),
    ("Won't",
     'A requirement that stakeholders agree need not be implemented in a given project'
     ' phase, but maybe considered for future phases'),
]

SHEET_INDEX = [
    ('Functional Requirements',
     'Capabilities the solution must have, in terms of the behaviour and the'
     ' information the solution will manage (BABOK functional requirements)'),
    ('Non-Functional Requirements',
     'Conditions under which the solution must remain effective, and qualities it'
     ' must have (availability, compatibility, compliance, maintainability,'
     ' performance, reliability, scalability, security, usability), each with a'
     ' success measure'),
]

GENERAL_INSTRUCTIONS = [
    'Vendor to demonstrate compliance with the Functional Requirements,'
    ' either through use case scenario or demos.',
    'Vendor to submit completed Non-Functional Requirements.'
    ' Please submit supporting documentation as appropriate.',
    'Enter Vendor name on the Non-Functional Requirements sheet.',
    "Enter information in the 'Tan color' cells and submit any supporting"
    " documentation as appropriate.",
    'Each non-functional requirement carries a SUCCESS MEASURE. Respond against the'
    ' measure, not against the description alone - a response that does not address'
    ' the measure cannot be evaluated.',
]


def _fill(rgb):
    return PatternFill(fill_type='solid', fgColor=rgb)


def _build_instructions(ws, project_name):
    """
    Title band, sheet index, general instructions, the BABOK reference checklists
    and the Compliance / Priority definition tables.

    Row positions are walked with a cursor rather than hardcoded, so a table can
    grow without shifting every later block by hand.
    """
    ws.sheet_view.showGridLines = False
    for col, width in (('A', 9.15), ('B', 30.69), ('C', 144.53), ('D', 11.38), ('E', 9.15)):
        ws.column_dimensions[col].width = width

    # Title band across A1:C4
    for row in range(1, 5):
        for col in range(1, 4):
            ws.cell(row=row, column=col).fill = _fill(GREY_15)
    ws['C2'] = 'ANNEXURE A - Requirements Specifications'
    ws['C2'].font = Font(name='Calibri', size=14, bold=True)
    ws['C3'] = project_name
    ws['C3'].font = Font(name='Calibri', size=14, bold=True)
    ws.row_dimensions[2].height = 18.45
    ws.row_dimensions[3].height = 18.45

    def section_heading(row, text):
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
        cell = ws.cell(row=row, column=2, value=text)
        cell.font = Font(name='Calibri', size=11, bold=True)
        cell.fill = _fill(GREY_25)
        cell.alignment = Alignment(horizontal='left')
        for col in (2, 3):
            ws.cell(row=row, column=col).border = BOX
        return row + 1

    def table_row(row, left, right, bold_left=True, fill=None, wrap=True):
        for col, value in ((2, left), (3, right)):
            cell = ws.cell(row=row, column=col, value=value)
            cell.font = Font(name='Calibri', size=11,
                             bold=bold_left if col == 2 else False)
            cell.alignment = Alignment(wrap_text=wrap, vertical='center')
            cell.border = BOX
            if fill:
                cell.fill = _fill(fill)
        return row + 1

    def full_width_row(row, text):
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
        cell = ws.cell(row=row, column=2, value=text)
        cell.font = Font(name='Calibri', size=11)
        cell.alignment = Alignment(horizontal='left', vertical='center',
                                   wrap_text=True)
        for col in (2, 3):
            ws.cell(row=row, column=col).border = BOX
        return row + 1

    cursor = 6
    first_content_row = cursor

    cursor = section_heading(cursor, 'SHEETS IN THIS DOCUMENT')
    for sheet, purpose in SHEET_INDEX:
        cursor = table_row(cursor, sheet, purpose, bold_left=False)

    cursor += 1
    cursor = section_heading(cursor, 'GENERAL INSTRUCTIONS')
    for text in GENERAL_INSTRUCTIONS:
        cursor = full_width_row(cursor, text)

    cursor += 1
    cursor = section_heading(cursor, 'REQUIREMENT TYPES (BABOK CLASSIFICATION SCHEMA)')
    cursor = table_row(cursor, 'Requirement Type', 'Definition', fill=GREY_5)
    for term, definition in REQUIREMENT_TYPES:
        cursor = table_row(cursor, term, definition)

    cursor += 1
    cursor = section_heading(
        cursor, 'NON-FUNCTIONAL REQUIREMENT CATEGORIES (BABOK s10.30)')
    cursor = full_width_row(
        cursor,
        'Use this list as an elicitation checklist - work down it and record what'
        ' the category demands of this solution, or record that it does not apply.'
        ' It is also the controlled vocabulary for the CATEGORY column of the'
        ' Non-Functional Requirements sheet.')
    cursor = table_row(cursor, 'Category', 'Definition', fill=GREY_5)
    for term, definition in NFR_CATEGORIES:
        cursor = table_row(cursor, term, definition)

    cursor += 1
    cursor = section_heading(cursor, 'REQUIREMENT QUALITY CHARACTERISTICS (BABOK)')
    cursor = table_row(cursor, 'Characteristic', 'Test to apply', fill=GREY_5)
    for term, definition in QUALITY_CHARACTERISTICS:
        cursor = table_row(cursor, term, definition)

    cursor += 1
    cursor = section_heading(cursor, 'DEFINITIONS')
    cursor = table_row(cursor, 'Compliance', 'Definition', fill=GREY_5)
    for term, definition in COMPLIANCE_DEFINITIONS:
        cursor = table_row(cursor, term, definition)

    cursor += 1
    cursor = table_row(cursor, 'Priority', 'Definition', fill=GREY_5)
    for term, definition in PRIORITY_DEFINITIONS:
        cursor = table_row(cursor, term, definition)

    for row in range(first_content_row, cursor):
        if ws.row_dimensions[row].height is None:
            ws.row_dimensions[row].height = 14.6


def _build_requirements_sheet(ws, sheet):
    """
    Header row, column widths, the vendor name band (where the sheet has one) and
    the two vendor-input dropdowns, for either requirements sheet.
    """
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 70
    for index, width in enumerate(sheet['widths'], start=1):
        ws.column_dimensions[ws.cell(row=1, column=index).column_letter].width = width

    if sheet['vendor_name_cell']:
        label = ws.cell(row=1, column=1, value='Vendor Name:')
        label.font = Font(name='Calibri', size=12, bold=True)
        label.alignment = Alignment(horizontal='left', vertical='center')
        label.border = BOX
        entry = ws.cell(row=1, column=2)
        entry.fill = _fill(TAN)
        entry.border = BOX
        ws.row_dimensions[1].height = 20.0

    header_row = sheet['header_row']
    ws.row_dimensions[header_row].height = 23.15
    for index, title in enumerate(sheet['columns'], start=1):
        cell = ws.cell(row=header_row, column=index, value=title)
        cell.font = Font(name='Calibri', size=12, bold=True, color=HEADER_RED)
        cell.fill = _fill(GREY_5)
        cell.border = BOX
        cell.alignment = Alignment(horizontal='center', vertical='center',
                                   wrap_text=True)

    # Freeze the header so long requirement sets stay readable
    ws.freeze_panes = ws.cell(row=sheet['first_data_row'], column=1)

    # Dropdowns are added over the first data row only; the extractor stretches
    # each range to the last populated row once it knows the requirement count.
    first = sheet['first_data_row']
    for column_name, options in (('COMPLIANCE', COMPLIANCE_OPTIONS),
                                 ('MRL Priority', PRIORITY_OPTIONS)):
        letter = ws.cell(
            row=first,
            column=sheet['columns'].index(column_name) + 1).column_letter
        validation = DataValidation(
            type='list', allow_blank=True,
            formula1='"{}"'.format(','.join(options)))
        ws.add_data_validation(validation)
        validation.add(f'{letter}{first}:{letter}{first}')


def style_requirement_row(ws, row, sheet=FUNCTIONAL_SHEET):
    """
    Apply the template's data-row styling to a single requirements row.

    Every cell is ruled on all four sides. CATEGORY is bold; CATEGORY and
    SUB-CATEGORY wrap and align top-left; ID and MRL Priority centre; DESCRIPTION
    and SUCCESS MEASURE wrap and align top. COMPLIANCE and COMMENTS carry the tan
    vendor-input fill. Alignment is chosen by column name, so the same function
    styles both the Functional and Non-Functional sheets.
    """
    for index, name in enumerate(sheet['columns'], start=1):
        cell = ws.cell(row=row, column=index)
        cell.font = Font(name='Calibri', size=11, bold=(name == 'CATEGORY'))
        cell.border = BOX
        if name in ('CATEGORY', 'SUB-CATEGORY'):
            cell.alignment = Alignment(wrap_text=True, vertical='top',
                                       horizontal='left')
        elif name == 'ID':
            cell.alignment = Alignment(wrap_text=True, vertical='center',
                                       horizontal='center')
        elif name in ('DESCRIPTION', 'SUCCESS MEASURE'):
            cell.alignment = Alignment(wrap_text=True, vertical='top')
        elif name == 'MRL Priority':
            cell.alignment = Alignment(vertical='center', horizontal='center')
        else:
            cell.alignment = Alignment(vertical='center', wrap_text=True)
        if name in VENDOR_INPUT_COLUMNS:
            cell.fill = _fill(TAN)


def create_workbook(project_name='<Project Name>'):
    """Build and return a fresh FRS workbook with all three sheets in place."""
    wb = Workbook()
    instructions = wb.active
    instructions.title = 'Instructions'
    _build_instructions(instructions, project_name)

    for sheet in REQUIREMENT_SHEETS:
        _build_requirements_sheet(wb.create_sheet(sheet['title']), sheet)

    wb.active = wb.index(wb[FUNCTIONAL_SHEET['title']])
    return wb


def create_template_file(path, project_name='<Project Name>'):
    """Write a blank FRS workbook to path. Useful for inspecting the layout."""
    wb = create_workbook(project_name)
    wb.save(path)
    return path


if __name__ == '__main__':
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else 'FRS_template.xlsx'
    print(f"Wrote blank FRS workbook: {create_template_file(target)}")
