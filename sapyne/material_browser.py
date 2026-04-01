"""Interactive material browser for notebook workflows.

This module provides a small ipywidgets-based browser for inspecting the
material libraries loaded into a notebook. It keeps notebook cells short and
concentrates the display logic in one reusable place.
"""

from IPython.display import HTML, display

BROWSER_COLUMNS = ["ID", "Name", "125", "250", "500", "1000", "2000", "4000"]
ABSORPTION_COLUMNS = ["125", "250", "500", "1000", "2000", "4000"]
LEFT_ALIGNED_COLUMNS = ["ID", "Name"]


def prepare_material_browser_table(table, search_text=""):
    """Prepare a filtered material table for browser display.

    Parameters
    ----------
    table : pandas.DataFrame
        Source material library.
    search_text : str, optional
        Case-insensitive free-text filter applied across visible columns.
    Returns
    -------
    pandas.DataFrame
        Filtered table containing only the columns relevant for browsing.
    """
    browser_table = table.copy()
    visible_columns = [col for col in BROWSER_COLUMNS if col in browser_table.columns]
    if visible_columns:
        browser_table = browser_table.loc[:, visible_columns]

    if search_text:
        mask = (
            browser_table.astype(str)
            .apply(lambda col: col.str.contains(search_text, case=False, na=False))
            .any(axis=1)
        )
        browser_table = browser_table.loc[mask]

    present_absorption_columns = [
        col for col in ABSORPTION_COLUMNS if col in browser_table.columns
    ]
    if present_absorption_columns:
        browser_table.loc[:, present_absorption_columns] = browser_table.loc[
            :, present_absorption_columns
        ].astype(float)

    return browser_table.reset_index(drop=True)


def render_material_browser(
    libraries,
    library_key,
    search_text="",
):
    """Render one filtered material table as HTML.

    Parameters
    ----------
    libraries : dict[str, pandas.DataFrame]
        Mapping of library names to material tables.
    library_key : str
        Selected library name.
    search_text : str, optional
        Case-insensitive free-text filter.
    Returns
    -------
    IPython.display.HTML
        HTML block containing a compact summary and formatted table.
    """
    browser_table = prepare_material_browser_table(
        libraries[library_key],
        search_text=search_text.strip(),
    )

    summary_html = (
        f"<p style='margin:0 0 0.35rem 0; font-size:0.9rem;'><strong>Knihovna:</strong> {library_key} "
        f"| <strong>Počet položek:</strong> {len(browser_table)}</p>"
    )

    if browser_table.empty:
        return HTML(
            summary_html
            + "<p style='margin:0; font-size:0.9rem;'>Žádné položky neodpovídají filtru.</p>"
        )

    present_absorption_columns = [
        col for col in ABSORPTION_COLUMNS if col in browser_table.columns
    ]
    formatters = {col: lambda value: f"{value:.2f}" for col in present_absorption_columns}
    header_styles = []
    for index, column_name in enumerate(browser_table.columns):
        alignment = "left" if column_name in LEFT_ALIGNED_COLUMNS else "right"
        header_styles.append(
            {
                "selector": f"th.col_heading.level0.col{index}",
                "props": [("text-align", alignment)],
            }
        )

    styled = browser_table.style.hide(axis="index")
    styled = styled.format(formatters)
    styled = styled.set_table_attributes(
        'style="width:100%; font-size:0.84rem; border-collapse:collapse; line-height:1.15;"'
    )
    styled = styled.set_properties(
        **{
            "text-align": "right",
            "padding": "0.18rem 0.35rem",
            "white-space": "nowrap",
        }
    )
    present_left_aligned_columns = [
        col for col in LEFT_ALIGNED_COLUMNS if col in browser_table.columns
    ]
    if present_left_aligned_columns:
        styled = styled.set_properties(
            subset=present_left_aligned_columns,
            **{
                "text-align": "left",
            },
        )
    if "Name" in browser_table.columns:
        styled = styled.set_properties(
            subset=["Name"],
            **{
                "white-space": "normal",
                "min-width": "18rem",
            },
        )
    styled = styled.set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    ("padding", "0.2rem 0.35rem"),
                    ("font-size", "0.8rem"),
                    ("border-bottom", "1px solid #bbb"),
                ],
            },
            {
                "selector": "td",
                "props": [("border-bottom", "1px solid #eee")],
            },
        ]
        + header_styles
    )

    return HTML(summary_html + styled.to_html())
def display_material_browser(libraries, default_library="basic"):
    """Display an interactive material browser in a notebook.

    Parameters
    ----------
    libraries : dict[str, pandas.DataFrame]
        Mapping of library names to material tables.
    default_library : str, optional
        Initially selected library key.

    Returns
    -------
    tuple
        ``(controls, output, library_dropdown, search_box)`` for optional reuse.
    """
    import ipywidgets as widgets

    if default_library not in libraries:
        default_library = sorted(libraries.keys())[0]

    library_dropdown = widgets.Dropdown(
        options=sorted(libraries.keys()),
        value=default_library,
        description="Knihovna:",
        layout=widgets.Layout(width="280px"),
    )

    search_box = widgets.Text(
        value="",
        placeholder="Filtr podle ID nebo názvu",
        description="Filtr:",
        layout=widgets.Layout(width="360px"),
    )

    browser_output = widgets.Output()

    def update_material_browser(*_):
        with browser_output:
            browser_output.clear_output()
            display(
                render_material_browser(
                    libraries,
                    library_dropdown.value,
                    search_box.value,
                )
            )

    library_dropdown.observe(update_material_browser, names="value")
    search_box.observe(update_material_browser, names="value")

    controls = widgets.HBox([library_dropdown, search_box])
    display(controls, browser_output)
    update_material_browser()
    return controls, browser_output, library_dropdown, search_box