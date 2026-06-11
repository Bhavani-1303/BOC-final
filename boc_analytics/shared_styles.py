"""
shared_styles.py — Shared CSS and sidebar branding for all pages.
Centralised so that every page gets consistent dark sidebar, bright table headers,
and the "Bills on Chain" branding title.
"""

import streamlit as st

# ── Common CSS ─────────────────────────────────────────────────────────────────
SHARED_CSS = """
<style>
/* ── Dark Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * {
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] a {
    color: #93C5FD !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stDateInput label {
    color: #CBD5E1 !important;
}
/* ── Sidebar widget inputs — dark background ─────────────────── */
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"],
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {
    background-color: #1E293B !important;
    border-color: #475569 !important;
}
[data-testid="stSidebar"] .stDateInput input,
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {
    background-color: #1E293B !important;
    border-color: #475569 !important;
    color: #FFFFFF !important;
    caret-color: #FFFFFF !important;
}
/* Select/Multiselect — internal search input must be transparent */
[data-testid="stSidebar"] [data-baseweb="select"] input {
    background: transparent !important;
    color: #1E293B !important;
    caret-color: #1E293B !important;
}
/* All text inside sidebar select/input boxes — black for readability */
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] * {
    color: #1E293B !important;
}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] * {
    color: #1E293B !important;
}
/* Dropdown arrow icon stays visible */
[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #64748B !important;
    color: #64748B !important;
}
/* Selected value text in selectbox */
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div > div {
    color: #1E293B !important;
}
/* Placeholder text in multiselect */
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div > div > div {
    color: #94A3B8 !important;
}
/* Multiselect pills/tags — styled with contrast */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #3B82F6 !important;
    color: #FFFFFF !important;
    border: none !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span {
    color: #FFFFFF !important;
}
/* Tag close/remove button */
[data-testid="stSidebar"] [data-baseweb="tag"] [role="presentation"],
[data-testid="stSidebar"] [data-baseweb="tag"] svg {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}
/* Sidebar horizontal rule */
[data-testid="stSidebar"] hr {
    border-color: #334155 !important;
}

/* ── Main Content Inputs — keep them light ────────────────────── */
[data-testid="stAppViewContainer"] .stDateInput input,
[data-testid="stAppViewContainer"] .stTextInput input,
[data-testid="stAppViewContainer"] .stNumberInput input {
    background-color: #FFFFFF !important;
    border-color: #CBD5E1 !important;
    color: #1E293B !important;
    caret-color: #1E293B !important;
}
[data-testid="stAppViewContainer"] .stSelectbox [data-baseweb="select"],
[data-testid="stAppViewContainer"] .stMultiSelect [data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border-color: #CBD5E1 !important;
}
/* Main area select search input — transparent bg with dark text */
[data-testid="stAppViewContainer"] [data-baseweb="select"] input {
    background: transparent !important;
    color: #1E293B !important;
    caret-color: #1E293B !important;
}
/* Main area selected value + placeholder text */
[data-testid="stAppViewContainer"] .stSelectbox [data-baseweb="select"] > div > div,
[data-testid="stAppViewContainer"] .stMultiSelect [data-baseweb="select"] span {
    color: #1E293B !important;
}
/* ── Dropdown popup menus (opened option lists) ──────────────── */
/* Main area popover — light background */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="popover"] ul,
[data-baseweb="menu"] ul {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
}
[data-baseweb="popover"] li,
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] li,
[data-baseweb="menu"] [role="option"] {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
}
[data-baseweb="popover"] li *,
[data-baseweb="menu"] li * {
    color: #1E293B !important;
}
[data-baseweb="popover"] li:hover,
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] [role="option"]:hover {
    background-color: #F1F5F9 !important;
}
/* Sidebar dropdown popover — dark background */
[data-testid="stSidebar"] [data-baseweb="popover"],
[data-testid="stSidebar"] [data-baseweb="menu"],
[data-testid="stSidebar"] [data-baseweb="popover"] ul,
[data-testid="stSidebar"] [data-baseweb="menu"] ul {
    background-color: #1E293B !important;
    border-color: #475569 !important;
}
[data-testid="stSidebar"] [data-baseweb="popover"] li,
[data-testid="stSidebar"] [data-baseweb="popover"] [role="option"],
[data-testid="stSidebar"] [data-baseweb="menu"] li,
[data-testid="stSidebar"] [data-baseweb="menu"] [role="option"] {
    background-color: #1E293B !important;
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] [data-baseweb="popover"] li *,
[data-testid="stSidebar"] [data-baseweb="menu"] li * {
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] [data-baseweb="popover"] li:hover,
[data-testid="stSidebar"] [data-baseweb="popover"] [role="option"]:hover {
    background-color: #334155 !important;
}
/* Fix radio button text in main area */
[data-testid="stAppViewContainer"] .stRadio label span {
    color: #1E293B !important;
}
/* Fix number_input text */
[data-testid="stAppViewContainer"] .stNumberInput input {
    background-color: #FFFFFF !important;
    border-color: #CBD5E1 !important;
    color: #1E293B !important;
}
/* Slider labels in sidebar */
[data-testid="stSidebar"] .stSlider div,
[data-testid="stSidebar"] .stSlider span {
    color: #E2E8F0 !important;
}

/* ── Streamlit Dataframe Table Headers ─────────────────────────── */
/* Make table headers bold and dark black with stronger styling */
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] [role="columnheader"],
.dvn-scroller th,
[data-testid="glideDataEditor"] [role="columnheader"],
[data-testid="stDataFrame"] thead th,
.glideDataEditor [role="columnheader"] {
    font-weight: 800 !important;
    color: #000000 !important;
    background-color: #F1F5F9 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.3px !important;
}
/* Target the glide-data-grid header cells specifically */
.dvn-scroller .gdg-header-cell,
[data-testid="stDataFrame"] .gdg-header-cell {
    font-weight: 800 !important;
    color: #000000 !important;
}
/* Make header text inside canvas-based grids visible */
[data-testid="stDataFrame"] canvas + div [role="columnheader"] {
    font-weight: 800 !important;
    color: #000000 !important;
}

/* ── Remove Table Row Hover Color ──────────────────────────────── */
[data-testid="stDataFrame"] [role="row"]:hover,
[data-testid="stDataFrame"] tr:hover,
.dvn-scroller [role="row"]:hover,
[data-testid="glideDataEditor"] [role="row"]:hover {
    background-color: transparent !important;
}
[data-testid="stDataFrame"] [role="gridcell"]:hover,
.dvn-scroller [role="gridcell"]:hover {
    background-color: transparent !important;
}

/* ── Sidebar Navigation Link Styling ──────────────────────────── */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] li {
    background: transparent;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a span {
    color: #CBD5E1 !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] li[class*="st-emotion-cache"] a[aria-selected="true"] span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* ── BillsOnChain Branding at TOP of sidebar (compact) ────────── */
[data-testid="stSidebar"]::before {
    content: "⛓️ BillsOnChain";
    display: block;
    padding: 0.8rem 1rem 0.2rem 1rem;
    font-size: 1.4rem;
    font-weight: 800;
    color: #FFFFFF !important;
    letter-spacing: -0.2px;
    line-height: 1.2;
}
[data-testid="stSidebar"]::after {
    content: "ANALYTICS";
    display: block;
    padding: 0 1rem 0.5rem 2.6rem;
    font-size: 0.5rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #64748B !important;
    border-bottom: 1px solid #334155;
    margin-bottom: 0.3rem;
}
</style>
"""

# ── Sidebar Branding ───────────────────────────────────────────────────────────
# NOTE: The branding is now done purely via CSS ::before/::after pseudo-elements
# on the sidebar container so it appears ABOVE the auto-generated navigation.
# The inject_sidebar_brand function below is kept for backward compatibility
# but no longer inserts HTML (to avoid duplicate branding).


def inject_shared_styles():
    """Inject the shared CSS into the current page."""
    st.markdown(SHARED_CSS, unsafe_allow_html=True)


def inject_sidebar_brand():
    """No-op — branding is now handled via CSS pseudo-elements at the top of sidebar."""
    pass


def render_searchable_table(df, search_placeholder="Search...", search_columns=None, rows_per_page=15):
    """
    Render a self-contained HTML table with instant search-as-you-type and pagination.
    
    Args:
        df: pandas DataFrame to display.
        search_placeholder: placeholder text for the search input.
        search_columns: list of column names to search in. If None, searches all columns.
        rows_per_page: number of rows per page.
    """
    import streamlit.components.v1 as components
    import json
    import html as html_mod

    if df.empty:
        st.info("No data to display.")
        return

    columns = list(df.columns)
    # Determine which column indices to search
    if search_columns:
        search_indices = [columns.index(c) for c in search_columns if c in columns]
    else:
        search_indices = list(range(len(columns)))

    # Convert dataframe rows to list of lists (all strings for display)
    rows_data = []
    for _, row in df.iterrows():
        rows_data.append([html_mod.escape(str(v)) if v is not None else "" for v in row])

    rows_json = json.dumps(rows_data)
    cols_json = json.dumps([html_mod.escape(str(c)) for c in columns])
    search_idx_json = json.dumps(search_indices)

    # Estimate height: header + search bar + rows + pagination + padding
    estimated_rows = min(rows_per_page, len(df))
    table_height = 110 + (estimated_rows * 40) + 60

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: transparent; color: #1E293B; }}
        .search-container {{
            position: relative;
            margin-bottom: 12px;
        }}
        .search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 14px;
            color: #94A3B8;
            pointer-events: none;
        }}
        .search-input {{
            width: 100%;
            padding: 10px 14px 10px 36px;
            border: 1.5px solid #E2E8F0;
            border-radius: 10px;
            font-size: 0.88rem;
            font-family: 'Inter', sans-serif;
            color: #1E293B;
            background: #FFFFFF;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        .search-input:focus {{
            border-color: #4F46E5;
            box-shadow: 0 0 0 3px rgba(79,70,229,0.10);
        }}
        .search-input::placeholder {{
            color: #94A3B8;
        }}
        .table-wrapper {{
            overflow-x: auto;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}
        th {{
            background: #F8FAFC;
            font-weight: 700;
            color: #1E293B;
            padding: 10px 14px;
            text-align: left;
            border-bottom: 2px solid #E2E8F0;
            white-space: nowrap;
            position: sticky;
            top: 0;
            letter-spacing: 0.2px;
        }}
        td {{
            padding: 9px 14px;
            border-bottom: 1px solid #F1F5F9;
            color: #334155;
            max-width: 260px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        tr:hover td {{
            background: #F8FAFC;
        }}
        .pagination {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 4px 2px 4px;
            font-size: 0.8rem;
            color: #64748B;
        }}
        .page-info {{
            font-weight: 500;
        }}
        .page-btns {{
            display: flex;
            gap: 4px;
            align-items: center;
        }}
        .page-btns button {{
            border: 1px solid #E2E8F0;
            background: #FFFFFF;
            color: #475569;
            border-radius: 6px;
            padding: 5px 12px;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            font-weight: 600;
            transition: all 0.15s;
        }}
        .page-btns button:hover:not(:disabled) {{
            background: #F1F5F9;
            border-color: #CBD5E1;
        }}
        .page-btns button:disabled {{
            opacity: 0.4;
            cursor: default;
        }}
        .page-btns span {{
            padding: 0 6px;
            font-weight: 600;
            color: #1E293B;
        }}
        .no-results {{
            text-align: center;
            padding: 24px;
            color: #94A3B8;
            font-size: 0.9rem;
        }}
        mark {{
            background: #FEF08A;
            color: #1E293B;
            border-radius: 2px;
            padding: 0 1px;
        }}
    </style>
    </head>
    <body>
    <div class="search-container">
        <span class="search-icon">🔍</span>
        <input type="text" class="search-input" id="searchInput"
               placeholder="{html_mod.escape(search_placeholder)}"
               autocomplete="off" />
    </div>
    <div class="table-wrapper">
        <table>
            <thead><tr id="headerRow"></tr></thead>
            <tbody id="tableBody"></tbody>
        </table>
        <div class="no-results" id="noResults" style="display:none;">No matching results found.</div>
    </div>
    <div class="pagination" id="pagination">
        <span class="page-info" id="pageInfo"></span>
        <div class="page-btns">
            <button id="btnPrev" onclick="changePage(-1)">← Prev</button>
            <span id="pageNum"></span>
            <button id="btnNext" onclick="changePage(1)">Next →</button>
        </div>
    </div>

    <script>
        const ALL_ROWS = {rows_json};
        const COLUMNS = {cols_json};
        const SEARCH_INDICES = {search_idx_json};
        const ROWS_PER_PAGE = {rows_per_page};
        let filteredRows = ALL_ROWS.slice();
        let currentPage = 1;

        // Build header
        const headerRow = document.getElementById('headerRow');
        COLUMNS.forEach(c => {{
            const th = document.createElement('th');
            th.textContent = c;
            headerRow.appendChild(th);
        }});

        function highlightMatch(text, query) {{
            if (!query) return text;
            const idx = text.toLowerCase().indexOf(query.toLowerCase());
            if (idx === -1) return text;
            return text.substring(0, idx) + '<mark>' + text.substring(idx, idx + query.length) + '</mark>' + text.substring(idx + query.length);
        }}

        function renderTable() {{
            const tbody = document.getElementById('tableBody');
            const noResults = document.getElementById('noResults');
            const query = document.getElementById('searchInput').value.trim();
            const totalPages = Math.max(1, Math.ceil(filteredRows.length / ROWS_PER_PAGE));
            if (currentPage > totalPages) currentPage = totalPages;
            const start = (currentPage - 1) * ROWS_PER_PAGE;
            const end = Math.min(start + ROWS_PER_PAGE, filteredRows.length);

            tbody.innerHTML = '';
            if (filteredRows.length === 0) {{
                noResults.style.display = 'block';
            }} else {{
                noResults.style.display = 'none';
                for (let i = start; i < end; i++) {{
                    const tr = document.createElement('tr');
                    filteredRows[i].forEach((cell, ci) => {{
                        const td = document.createElement('td');
                        td.title = cell;
                        if (query && SEARCH_INDICES.includes(ci)) {{
                            td.innerHTML = highlightMatch(cell, query);
                        }} else {{
                            td.textContent = cell;
                        }}
                        tr.appendChild(td);
                    }});
                    tbody.appendChild(tr);
                }}
            }}
            // Pagination
            document.getElementById('pageInfo').textContent =
                filteredRows.length > 0
                    ? 'Showing ' + (start+1) + '–' + end + ' of ' + filteredRows.length + ' results'
                    : '';
            document.getElementById('pageNum').textContent = currentPage + ' / ' + totalPages;
            document.getElementById('btnPrev').disabled = currentPage <= 1;
            document.getElementById('btnNext').disabled = currentPage >= totalPages;
        }}

        function doSearch() {{
            const query = document.getElementById('searchInput').value.trim().toLowerCase();
            if (!query) {{
                filteredRows = ALL_ROWS.slice();
            }} else {{
                filteredRows = ALL_ROWS.filter(row =>
                    SEARCH_INDICES.some(ci => row[ci].toLowerCase().includes(query))
                );
            }}
            currentPage = 1;
            renderTable();
        }}

        function changePage(delta) {{
            currentPage += delta;
            renderTable();
        }}

        document.getElementById('searchInput').addEventListener('input', doSearch);
        renderTable();
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=table_height, scrolling=False)
