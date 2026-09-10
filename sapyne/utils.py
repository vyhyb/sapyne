"""Utility helpers for report generation, table export, and library loading.

This module contains convenience functions used by notebooks and scripts for:

- loading predefined material libraries,
- normalizing DataFrame tables for display/export,
- rendering LaTeX snippets and full documents via Jinja2 templates,
- compiling LaTeX documents with ``latexmk`` or ``pdflatex``.
"""

from pathlib import Path
import locale
import shutil
import subprocess

import pandas as pd
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .room import BANDS

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
DEFAULT_LIBRARY_FILES = {
    "basic": "basic.csv",
    "rigips": "rigips.csv",
    "novatop": "novatop.csv",
    "ecophon": "ecophon.csv",
    "ecophon_objects": "ecophon_objects.csv",
    "heraklith": "heraklith.csv",
    "objects": "objects.csv",
    "mappy": "mappy.csv",
    "literature": "literature.csv",
}

def latex_escape(value):
    """Escape text for safe usage in LaTeX.

    Parameters
    ----------
    value : Any
        Value to escape. ``None`` is converted to an empty string.

    Returns
    -------
    str
        Escaped text suitable for insertion into LaTeX source.
    """
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    text = "" if value is None else str(value)
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def load_material_libraries(library_dir="sapyne/library", library_files=None):
    """Load a set of material library CSV files into pandas DataFrames.

    Parameters
    ----------
    library_dir : str or pathlib.Path, optional
        Base directory containing CSV library files.
    library_files : dict[str, str] or None, optional
        Mapping ``{key: filename}``. When ``None``, ``DEFAULT_LIBRARY_FILES``
        is used.

    Returns
    -------
    dict[str, pandas.DataFrame]
        Loaded libraries keyed by names from ``library_files``.
    """
    library_dir = Path(library_dir)
    library_files = DEFAULT_LIBRARY_FILES if library_files is None else library_files

    libraries = {}
    for key, filename in library_files.items():
        libraries[key] = pd.read_csv(library_dir / filename)
    return libraries


def clean_table_for_export(
    table,
    rename_columns=None,
    drop_columns=None,
    first_columns=None,
    integer_columns=None,
    decimals=2,
    decimal_comma=True,
):
    """Prepare a table for HTML/LaTeX export.

    The function supports common cleanup steps: dropping/renaming columns,
    reordering selected columns, converting numeric fields, rounding, integer
    formatting, and optional decimal comma conversion.

    Parameters
    ----------
    table : pandas.DataFrame
        Input table.
    rename_columns : dict[str, str] or None, optional
        Column rename mapping.
    drop_columns : list[str] or None, optional
        Columns to drop. Missing columns are ignored.
    first_columns : list[str] or None, optional
        Columns to place at the beginning in the given order.
    integer_columns : list[str] or None, optional
        Numeric columns rendered as integer strings.
    decimals : int, optional
        Number of decimal places for non-integer numeric columns.
    decimal_comma : bool, optional
        If ``True``, replace decimal point with comma in formatted values.

    Returns
    -------
    pandas.DataFrame
        Cleaned table formatted as strings for export.
    """
    cleaned = table.copy()

    if drop_columns:
        cleaned = cleaned.drop(columns=drop_columns, errors="ignore")

    if rename_columns:
        cleaned = cleaned.rename(columns=rename_columns)

    if first_columns:
        ordered_front = [
            column for column in first_columns if column in cleaned.columns
        ]
        ordered_rest = [
            column for column in cleaned.columns if column not in ordered_front
        ]
        cleaned = cleaned[ordered_front + ordered_rest]

    if cleaned.empty:
        return cleaned.astype(str).reset_index(drop=True)

    integer_columns = [] if integer_columns is None else list(integer_columns)
    integer_set = set(integer_columns)
    non_numeric_columns = set()
    if "Název" in cleaned.columns:
        non_numeric_columns.add("Název")
    if "Name" in cleaned.columns:
        non_numeric_columns.add("Name")

    numeric_columns = [
        column for column in cleaned.columns if column not in non_numeric_columns
    ]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    for column in integer_columns:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce").fillna(0)

    for column in numeric_columns:
        if column in integer_set:
            cleaned[column] = cleaned[column].map(
                lambda value: "" if pd.isna(value) else str(int(round(value)))
            )
            continue

        cleaned[column] = cleaned[column].round(decimals)
        cleaned[column] = cleaned[column].map(
            lambda value: "" if pd.isna(value) else f"{value:.{decimals}f}"
        )
        if decimal_comma:
            cleaned[column] = cleaned[column].astype(str).str.replace(".", ",", regex=False)

    return cleaned.reset_index(drop=True)


def _format_table_environment(latex_tab):
    """Convert basic LaTeX table blocks to centered ``table``/``tabularx``.

    Parameters
    ----------
    latex_tab : str
        LaTeX string containing table markup.

    Returns
    -------
    str
        Updated LaTeX table string.
    """
    latex_tab = latex_tab.replace(r"\begin{table}", "\\begin{table}[H]\n\\centering", 1)
    latex_tab = latex_tab.replace(r"\begin{tabular}", r"\begin{tabularx}{\textwidth}")
    latex_tab = latex_tab.replace(r"\end{tabular}", r"\end{tabularx}")
    return latex_tab


def _export_latex_table_from_template(
    table,
    filename,
    label,
    caption,
    column_format=None,
    caption_spacing="0.4em",
    row_lines=True,
    preserve_latex=False,
):
    """Render and save a LaTeX table using the dedicated Jinja2 template.

    Parameters
    ----------
    table : pandas.DataFrame
        Input table to render.
    filename : str
        Output file path without extension.
    label : str
        LaTeX label key (without surrounding ``\\label{}``).
    caption : str
        LaTeX table caption text.
    column_format : str or None, optional
        ``tabularx`` column format string. Defaults to ``X`` plus right-aligned
        numeric columns.
    caption_spacing : str, optional
        Vertical spacing inserted after caption (e.g. ``"0.5em"``).
    row_lines : bool, optional
        Template flag for row separators.
    preserve_latex : bool, optional
        If ``True``, cells that look like LaTeX snippets are not escaped.

    Returns
    -------
    str
        Rendered LaTeX table string.
    """
    table_latex = table.copy()
    headers = [latex_escape(str(c)) for c in table_latex.columns]

    rows = []
    for row in table_latex.itertuples(index=False):
        converted = []
        for value in row:
            if pd.isna(value):
                converted.append("")
                continue

            cell = str(value)
            if preserve_latex and ("$" in cell or "\\" in cell):
                converted.append(cell)
            else:
                converted.append(latex_escape(cell))
        rows.append(converted)

    if column_format is None:
        column_format = "X" + "r" * (len(headers) - 1)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("table_export.tex.j2")

    latex_tab = template.render(
        caption=caption if preserve_latex else latex_escape(caption),
        label=label,
        caption_spacing=caption_spacing,
        column_format=column_format,
        headers=headers,
        rows=rows,
        row_lines=row_lines,
    )

    tex_file = f"{filename}.tex"
    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(latex_tab)
    return latex_tab


def render_latex_report(template_path, output_path, context):
    """Render a Jinja2 LaTeX report template to a ``.tex`` file.

    Parameters
    ----------
    template_path : str or pathlib.Path
        Path to the Jinja2 LaTeX template.
    output_path : str or pathlib.Path
        Destination path for rendered LaTeX source.
    context : dict
        Template context variables.

    Returns
    -------
    str
        Rendered LaTeX source content.
    """
    template_path = Path(template_path)
    output_path = Path(output_path)

    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["latex_escape"] = latex_escape

    rendered = env.get_template(template_path.name).render(**context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return rendered


def compile_latex_document(tex_path, working_directory=None, engine="latexmk"):
    """Compile a LaTeX document and return execution metadata.

    Parameters
    ----------
    tex_path : str or pathlib.Path
        Path to ``.tex`` file to compile.
    working_directory : str or pathlib.Path or None, optional
        Directory where compilation is executed. Defaults to the directory of
        ``tex_path``.
    engine : {"latexmk", "pdflatex"}, optional
        Preferred compilation engine. If unavailable, falls back to
        ``pdflatex`` when possible.

    Returns
    -------
    dict[str, str]
        Dictionary containing command string, output PDF path, and captured
        stdout/stderr.

    Raises
    ------
    FileNotFoundError
        If no supported LaTeX compiler is available.
    RuntimeError
        If compilation fails.
    """
    tex_path = Path(tex_path).resolve()
    work_dir = (
        Path(working_directory).resolve() if working_directory else tex_path.parent
    )
    output_encoding = locale.getpreferredencoding(False) or "utf-8"

    # Remove stale aux files so previous failed label state does not poison next run.
    for ext in ["aux", "out", "toc", "log", "fls", "fdb_latexmk"]:
        sidecar = work_dir / f"{tex_path.stem}.{ext}"
        if sidecar.exists():
            sidecar.unlink()

    if engine == "latexmk" and shutil.which("latexmk"):
        command = [
            "latexmk",
            "-pdf",
            "-g",
            "-interaction=nonstopmode",
            "-halt-on-error",
            tex_path.name,
        ]
    elif shutil.which("pdflatex"):
        command = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            tex_path.name,
        ]
    else:
        raise FileNotFoundError("No LaTeX compiler found. Install latexmk or pdflatex.")

    runs = 1 if command[0] == "latexmk" else 2
    completed = None
    for _ in range(runs):
        completed = subprocess.run(
            command,
            cwd=work_dir,
            check=False,
            capture_output=True,
            text=True,
            encoding=output_encoding,
            errors="replace",
        )
        if completed.returncode != 0:
            message = completed.stdout + "\n" + completed.stderr
            raise RuntimeError(message.strip())

    return {
        "command": " ".join(command),
        "pdf_path": str(work_dir / f"{tex_path.stem}.pdf"),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def export_latex_tabularx(
    table,
    filename="table_results",
    label="tab:plochy",
    caption="Výčet pohltivých ploch.",
):
    """Export a general table to LaTeX using the shared table template.

    Parameters
    ----------
    table : pandas.DataFrame
        Table to export.
    filename : str, optional
        Output file path without extension.
    label : str, optional
        LaTeX label key.
    caption : str, optional
        LaTeX caption text.

    Returns
    -------
    str
        Rendered LaTeX table string.
    """
    return _export_latex_table_from_template(
        table=table,
        filename=filename,
        label=label,
        caption=caption,
        column_format="X" + "r" * (len(table.columns) - 1),
        caption_spacing="0.5em",
        row_lines=True,
    )


def export_latex_t60_table(
    filename, alpha_mean, t60, t_opt, t_min, t_max, label="", caption="", bands=None
):
    """Build and export the reverberation summary table to LaTeX.

    Parameters
    ----------
    filename : str
        Output file base name.
    alpha_mean : array-like
        Mean absorption coefficient values by band.
    t60 : pandas.Series
        Calculated reverberation time by band.
    t_opt : float
        Target reverberation time.
    t_min : array-like
        Minimum acceptable reverberation values by band.
    t_max : array-like
        Maximum acceptable reverberation values by band.
    label : str, optional
        LaTeX label key.
    caption : str, optional
        LaTeX caption text.
    bands : list[str] or None, optional
        Frequency bands. Defaults to ``BANDS``.

    Returns
    -------
    str
        Rendered LaTeX table string.
    """
    bands = BANDS if bands is None else bands
    table = pd.DataFrame(
        {
            "Název": [
                r"$\alpha_\mathrm{str}$",
                r"$T_\mathrm{E}$",
                r"$T_\mathrm{max}/T_\mathrm{opt}$",
                r"$T_\mathrm{E}/T_{\mathrm{opt}}$",
                r"$T_{\mathrm{min}}/T_{\mathrm{opt}}$",
            ],
        }
    )
    for i in range(len(bands)):
        table[bands[i]] = [
            alpha_mean[i],
            t60.iloc[i],
            t_max[i] / t_opt,
            t60.iloc[i] / t_opt,
            t_min[i] / t_opt,
        ]

    table = table.round(2)

    # convert all the values to strings
    for col in table.columns:
        if col != "Název" and table[col].dtype in ["float64", "int64"]:
            table[col] = table[col].apply(lambda x: f"{x:.2f}".replace(".", ","))

    latex_tab = _export_latex_table_from_template(
        table=table,
        filename=f"{filename}_t60_results",
        label=label,
        caption=caption,
        column_format="X" + "r" * (table.shape[1] - 1),
        caption_spacing="0.5em",
        row_lines=True,
        preserve_latex=True,
    )

    tex_file = f"{filename}_t60_results.tex"

    print(f"Uloženo do: {tex_file}")
    print("Pozn.: v preambuli LaTeX použijte \\usepackage{tabularx}.")
    return latex_tab


def export_latex_absorption_table(
    filename,
    absorption,
    absorption_to_volume_ratio,
    req_abs_volume_ratio,
    label="",
    caption="",
    bands=None,
):
    """Build and export the absorption summary table to LaTeX.

    Parameters
    ----------
    filename : str
        Output file base name.
    absorption : array-like
        Total absorption values by band.
    absorption_to_volume_ratio : array-like
        Ratio ``A/V`` values by band.
    req_abs_volume_ratio : array-like
        Required ``A/V`` values by band.
    label : str, optional
        LaTeX label key.
    caption : str, optional
        LaTeX caption text.
    bands : list[str] or None, optional
        Frequency bands. Defaults to ``BANDS``.

    Returns
    -------
    str
        Rendered LaTeX table string.
    """
    bands = BANDS if bands is None else bands
    table = pd.DataFrame(
        {
            "Název": [r"$A$", r"$A/V$", r"$(A/V)_\mathrm{req}$"],
        }
    )
    for i in range(len(bands)):
        table[bands[i]] = [
            absorption[i],
            absorption_to_volume_ratio[i],
            req_abs_volume_ratio[i],
        ]
    table = table.round(2)

    # convert all the values to strings
    for col in table.columns:
        if col != "Název" and table[col].dtype in ["float64", "int64"]:
            table[col] = table[col].apply(lambda x: f"{x:.2f}".replace(".", ","))
    latex_tab = _export_latex_table_from_template(
        table=table,
        filename=f"{filename}_absorption_results",
        label=label,
        caption=caption,
        column_format="X" + "r" * (table.shape[1] - 1),
        caption_spacing="0.5em",
        row_lines=True,
        preserve_latex=True,
    )
    tex_file = f"{filename}_absorption_results.tex"
    print(f"Uloženo do: {tex_file}")
    print("Pozn.: v preambuli LaTeX použijte \\usepackage{tabularx}.")
    return latex_tab


def export_latex_room_requirements_table(
    room_type_name,
    room_type_simple,
    required_absorption_volume_ratio,
    height,
    volume,
    filename="table_requirements",
    label="tab:pozadavky",
    caption="Zatřídění místnosti akustické požadavky dle \\citet{2023_CSN730527}",
):
    """Build and export the room requirements table to LaTeX.

    Parameters
    ----------
    room_type_name : str
        Human-readable room type name.
    room_type_simple : RoomTypeSimple
        Room type object with category and absorption dependency.
    height : float
        Light height of the room in meters.
    volume : float
        Room volume in cubic meters.
    filename : str, optional
        Output file base name. Default: "table_requirements".
    label : str, optional
        LaTeX label key. Default: "tab:pozadavky".
    caption : str, optional
        LaTeX caption text.

    Returns
    -------
    str
        Rendered LaTeX table string.
    """
    from .standard2023 import ABS_DEPENDENCY_LATEX
    
    category = room_type_simple.category_str
    abs_requirement_latex = ABS_DEPENDENCY_LATEX[category](height)
    
    # Build simple key-value table
    table = pd.DataFrame({
        "Property": [
            "Typ místnosti",
            r"Kategorie dle Tabulky \ref{tab:csn730527}",
            r"Světlá výška místnosti $h$",
            "Objem místnosti",
            r"Požadavek: Minimální hodnota $A/V$",
        ],
        "Value": [
            room_type_name,
            f"Kategorie {category}",
            f"{height:.1f} m",
            f"{volume:.1f} $\\mathrm{{m^3}}$",
            abs_requirement_latex[:-1] + f" = {required_absorption_volume_ratio:.2f} \\mathrm{{m^{-1}}}$",
        ],
    })
    
    latex_tab = _export_latex_table_from_template(
        table=table,
        filename=filename,
        label=label,
        caption=caption,
        column_format="l X",
        caption_spacing="0.5em",
        row_lines=False,
        preserve_latex=True,
    )
    print(f"Uloženo do: {filename}.tex")
    print("Pozn.: v preambuli LaTeX použijte \\usepackage{tabularx}.")
    return latex_tab
