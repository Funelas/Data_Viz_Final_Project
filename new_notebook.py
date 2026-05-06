import nbformat as nbf

nb = nbf.v4.new_notebook()

dashboard_code = '''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import folium
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import warnings

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

# ==========================
# LOAD DATA
# ==========================
df_brgy = pd.read_csv("barangays.csv")
df_fac = pd.read_csv("facilities.csv")
df_teams = pd.read_csv("rescue_teams.csv")
df_incidents = pd.read_csv("incidents.csv")

df_incidents['DateTime'] = pd.to_datetime(df_incidents['DateTime'])
df_incidents['Month'] = df_incidents['DateTime'].dt.to_period('M').astype(str)
df_incidents['NumAffected'] = df_incidents.groupby('Type')['NumAffected'].transform(lambda x: x.fillna(x.median()))

hazard_weights = {'Low':1,'Medium':2,'High':3,'Critical':4}
df_brgy['HazardWeight'] = df_brgy['HazardLevel'].map(hazard_weights)
df_brgy['RiskScore'] = (df_brgy['HazardWeight'] * (df_brgy['Population']/1000)).round(2)

# ==========================
# KPI CARDS
# ==========================
def render_kpis():
    total_incidents = len(df_incidents)
    total_affected = int(df_incidents['NumAffected'].sum())
    available_teams = len(df_teams[df_teams['Status'] == 'Available'])
    total_capacity = df_fac['Capacity'].sum()
    highest_risk_brgy = df_brgy.sort_values(by='RiskScore', ascending=False).iloc[0]['Barangay']
    total_evac_centers = len(df_fac[df_fac['Capacity']*0.9 > df_fac['Occupants']])
    water_rescue_teams = len(df_teams[df_teams['Specialty'] == 'Water Rescue'])
    critical_incidents = len(df_incidents[df_incidents['Severity'] == 'Critical'])
    total_occupants = int(df_fac['Occupants'].sum())
    occ_pct = round((total_occupants / df_fac['Capacity'].sum()) * 100, 1)
    facilities_needing_resupply = len(df_fac[df_fac['ResourcesAvailable'] < 30])

    kpis = [
        {"icon": "\\U0001f6a8", "label": "Total Incidents",     "value": total_incidents,            "color": "#e53e3e", "bg": "#fff5f5", "badge": "Operational", "badge_color": "#e53e3e"},
        {"icon": "\\U0001f465", "label": "Total Affected",       "value": total_affected,             "color": "#dd6b20", "bg": "#fffaf0", "badge": "Impact",       "badge_color": "#dd6b20"},
        {"icon": "\\U0001f7e2", "label": "Available Teams",      "value": available_teams,            "color": "#276749", "bg": "#f0fff4", "badge": "Readiness",    "badge_color": "#276749"},
        {"icon": "\\U0001f3e5", "label": "Total Capacity",       "value": total_capacity,             "color": "#2b6cb0", "bg": "#ebf8ff", "badge": "Resources",    "badge_color": "#2b6cb0"},
        {"icon": "\\u26a0",     "label": "Critical Incidents",   "value": critical_incidents,         "color": "#822727", "bg": "#fff5f5", "badge": "Critical",     "badge_color": "#822727"},
        {"icon": "\\U0001f3e0", "label": "Evac Centers",         "value": total_evac_centers,         "color": "#276749", "bg": "#f0fff4", "badge": "Active",       "badge_color": "#276749"},
        {"icon": "\\U0001f30a", "label": "Water Rescue Teams",   "value": water_rescue_teams,         "color": "#2c5282", "bg": "#ebf8ff", "badge": "Specialized",  "badge_color": "#2c5282"},
        {"icon": "\\U0001f4cd", "label": "Highest Risk Brgy",    "value": highest_risk_brgy,          "color": "#744210", "bg": "#fffff0", "badge": "Priority",     "badge_color": "#744210"},
        {"icon": "\\U0001f4ca", "label": "Occupants / Capacity", "value": f"{occ_pct}%",             "color": "#553c9a", "bg": "#faf5ff", "badge": "Occupancy",    "badge_color": "#553c9a"},
        {"icon": "\\U0001f6a6", "label": "Need Resupply",        "value": facilities_needing_resupply,"color": "#234e52", "bg": "#e6fffa", "badge": "Resources",    "badge_color": "#234e52"},
    ]

    cards_html = ""
    for kpi in kpis:
        cards_html += (
            '<div style="background:' + kpi['bg'] + '; border-radius:12px; padding:16px 20px; width:180px;'
            ' box-shadow:0 2px 8px rgba(0,0,0,0.08); display:flex; flex-direction:column; gap:8px;'
            ' border-left:5px solid ' + kpi['color'] + ';">' +
            '<div style="display:flex; align-items:center; gap:10px;">'
            '<span style="font-size:26px;">' + kpi['icon'] + '</span>'
            '<div>'
            '<div style="font-size:22px; font-weight:800; color:' + kpi['color'] + '; line-height:1.1;">' + str(kpi['value']) + '</div>'
            '<div style="font-size:12px; color:#4a5568; font-weight:500; margin-top:2px;">' + kpi['label'] + '</div>'
            '</div></div>'
            '<div style="align-self:flex-start; background:' + kpi['color'] + '18; color:' + kpi['badge_color'] + ';'
            ' font-size:10px; font-weight:700; padding:3px 8px; border-radius:20px; letter-spacing:0.5px;">' + kpi['badge'] + '</div>'
            '</div>'
        )

    display(HTML(
        '<div style="font-family:Segoe UI,sans-serif; background:#f7fafc; padding:24px; border-radius:16px;">'
        '<div style="margin-bottom:20px;">'
        '<h2 style="margin:0; color:#1a202c; font-size:20px;">\\U0001f4cb DRRM Strategic Performance Indicators</h2>'
        '<p style="margin:4px 0 0; color:#718096; font-size:13px;">Bi\\u00f1an City DRRMO \\u2014 Operational Dashboard</p>'
        '</div>'
        '<div style="display:flex; flex-wrap:wrap; gap:16px; justify-content:center">'
        + cards_html +
        '</div></div>'
    ))

# ==========================
# CHARTS
# ==========================
def render_charts():
    fig = plt.figure(figsize=(18, 28))
    gs = fig.add_gridspec(4, 2, height_ratios=[1, 1, 1.5, 1.5], hspace=0.5, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, 0])
    df_incidents.groupby('Month').size().plot(kind='line', marker='o', color='blue', ax=ax1)
    ax1.set_title('Monthly Incident Trend (Resource Prediction)')
    ax1.set_ylabel('Count')

    ax2 = fig.add_subplot(gs[0, 1])
    df_incidents['Type'].value_counts().plot(kind='barh', color='orange', ax=ax2)
    ax2.set_title('Incident Types (Training Focus)')

    ax3 = fig.add_subplot(gs[1, 0])
    top_risk = df_brgy.sort_values(by='RiskScore', ascending=False).head(10)
    sns.barplot(data=top_risk, x='RiskScore', y='Barangay', palette='Reds_r', ax=ax3)
    ax3.set_title('Top 10 High-Risk Barangays (Mitigation Priority)')

    ax4 = fig.add_subplot(gs[1, 1])
    pop_affected = df_incidents.groupby('Barangay')['NumAffected'].sum()
    cap_per_brgy = df_fac.groupby('Barangay')['Capacity'].sum()
    gap_df = pd.DataFrame({'Population Affected': pop_affected, 'Facility Capacity': cap_per_brgy}).fillna(0)
    gap_df = gap_df.sort_values('Population Affected', ascending=False).head(10)
    x = range(len(gap_df))
    width = 0.4
    ax4.barh([i + width/2 for i in x], gap_df['Population Affected'], height=width, color='#d93025', label='Population Affected')
    ax4.barh([i - width/2 for i in x], gap_df['Facility Capacity'], height=width, color='#1e8e3e', label='Facility Capacity')
    ax4.set_yticks(ticks=x)
    ax4.set_yticklabels(gap_df.index)
    ax4.set_title('Gap Analysis: Affected vs Capacity (by Barangay)')
    ax4.legend()

    ax5 = fig.add_subplot(gs[2, :])
    resupply_df = df_fac[['Name', 'ResourcesAvailable']].sort_values('ResourcesAvailable').head(10)
    colors_resupply = ['#e53e3e' if v < 30 else '#f9ab00' if v < 60 else '#1e8e3e' for v in resupply_df['ResourcesAvailable']]
    ax5.barh(resupply_df['Name'], resupply_df['ResourcesAvailable'], color=colors_resupply)
    ax5.axvline(x=30, color='red', linestyle='--', linewidth=1.5, label='30% Resupply Threshold')
    ax5.set_xlabel('Resources Available (%)')
    ax5.set_title('Facility Resource Levels (Red = Needs Resupply)')
    ax5.legend(loc='lower right')
    ax5.set_xlim(0, 110)

    ax6 = fig.add_subplot(gs[3, :])
    sev_counts = df_incidents['Severity'].value_counts()
    color_map = {'Low': '#28a745', 'Moderate': '#fd7e14', 'High': '#dc3545', 'Critical': '#8b0000'}
    colors = [color_map.get(x, 'gray') for x in sev_counts.index]
    patches, texts, autotexts = ax6.pie(sev_counts, autopct='%1.1f%%', colors=colors, labels=sev_counts.index, startangle=90, radius=1.0)
    plt.setp(autotexts, size=11, weight="bold", color="white")
    plt.setp(texts, size=11, weight="bold")
    ax6.set_title('Incident Severity Breakdown (Threat Level)')
    ax6.set_ylabel('')

    plt.tight_layout()
    plt.show()

# ==========================
# INTERACTIVE OLAP FILTERS
# ==========================
sorted_brgys = sorted(list(df_incidents['Barangay'].unique()))
severity_levels = ["Low", "Moderate", "High", "Critical"]
all_periods = sorted(df_incidents['Month'].unique())

date_range_filter = widgets.SelectionRangeSlider(
    options=all_periods, index=(0, len(all_periods)-1),
    description='Date Range:', continuous_update=True, readout=False,
    layout=widgets.Layout(width='600px')
)
date_range_label = widgets.HTML(
    value=f\'<div style="text-align:center; width:600px;"><b>Start:</b> {all_periods[0]} &nbsp;&nbsp;&nbsp; <b>End:</b> {all_periods[-1]}</div>\',
    layout=widgets.Layout(width='600px', margin='4px 0 10px 0')
)

def update_date_label(change):
    date_range_label.value = f\'<div style="text-align:center; width:600px;"><b>Start:</b> {date_range_filter.value[0]} &nbsp;&nbsp;&nbsp; <b>End:</b> {date_range_filter.value[1]}</div>\'

date_range_filter.observe(update_date_label, names='value')

type_filter = widgets.Dropdown(options=['All'] + list(df_incidents['Type'].unique()), description='Incident Type:')
severity_filter = widgets.Dropdown(options=['All'] + severity_levels, description='Severity:')
brgy_filter = widgets.Dropdown(options=['All'] + sorted_brgys, description='Barangay:')
fac_type_filter = widgets.Dropdown(options=['All'] + list(df_fac['Type'].unique()), description='Facility:')

export_button = widgets.Button(description="Export to CSV", button_style='success', icon='download')
output_table = widgets.Output()
output_map = widgets.Output()
export_status = widgets.Output()

def get_filtered_data():
    filtered_df = df_incidents.copy()
    start_period, end_period = date_range_filter.value[0], date_range_filter.value[1]
    filtered_df = filtered_df[
        (filtered_df['Month'] >= start_period) &
        (filtered_df['Month'] <= end_period)
    ]
    if type_filter.value != 'All':
        filtered_df = filtered_df[filtered_df['Type'] == type_filter.value]
    if severity_filter.value != 'All':
        filtered_df = filtered_df[filtered_df['Severity'] == severity_filter.value]
    if brgy_filter.value != 'All':
        filtered_df = filtered_df[filtered_df['Barangay'] == brgy_filter.value]
    return filtered_df

def update_dashboard(change=None):
    output_table.clear_output()
    output_map.clear_output()
    export_status.clear_output()

    filtered_df = get_filtered_data()

    with output_table:
        display(HTML(f"<h3>Filtered Records: {len(filtered_df)} incidents</h3>"))

        def color_severity(val):
            color, bg = '', ''
            if val == 'Low': color, bg = 'green', '#e8f5e9'
            elif val == 'Moderate': color, bg = 'orange', '#fff3e0'
            elif val == 'High': color, bg = 'red', '#ffebee'
            elif val == 'Critical': color, bg = 'white', 'darkred'
            return f'color: {color}; background-color: {bg}; font-weight: bold;'

        if not filtered_df.empty:
            display(filtered_df.head(10).style.applymap(color_severity, subset=['Severity']))
        else:
            display(filtered_df.head(10))

    with output_map:
        if len(filtered_df) > 0:
            center_lat = filtered_df['Latitude'].mean()
            center_lon = filtered_df['Longitude'].mean()
        else:
            center_lat, center_lon = 14.3333, 121.0833

        m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

        sev_styles = {
            'Low':      {'color': '#28a745', 'radius': 7},
            'Moderate': {'color': '#fd7e14', 'radius': 10},
            'High':     {'color': '#dc3545', 'radius': 14},
            'Critical': {'color': '#8b0000', 'radius': 18}
        }

        for idx, row in filtered_df.iterrows():
            style = sev_styles.get(row['Severity'], {'color': 'gray', 'radius': 7})
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=style['radius'],
                color=style['color'],
                fill=True,
                fill_color=style['color'],
                fill_opacity=0.4,
                weight=1.5,
                popup=f"<b>{row['Type']}</b><br>Severity: <b>{row['Severity']}</b><br>Affected: {row['NumAffected']}"
            ).add_to(m)

        for idx, row in df_fac.iterrows():
            if brgy_filter.value != 'All' and row['Barangay'] != brgy_filter.value:
                continue
            fac_type = row.get('Type', '')
            if fac_type_filter.value != 'All' and fac_type != fac_type_filter.value:
                continue
            icon_prefix = 'glyphicon'
            if fac_type == 'Hospital':
                icon_name, color = 'plus', 'red'
            elif fac_type == 'Evacuation Site':
                icon_name, color = 'home', 'green'
            elif fac_type == 'Fire Station':
                icon_name, color = 'fire', 'darkred'
            elif fac_type == 'School':
                icon_name, color, icon_prefix = 'building', 'orange', 'fa'
            elif fac_type == 'Command Center':
                icon_name, color, icon_prefix = 'building', 'blue', 'fa'
            elif fac_type == 'Health Care Center':
                icon_name, color, icon_prefix = 'heart', 'red', 'fa'
            else:
                icon_name, color = 'info-sign', 'green'
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                icon=folium.Icon(color=color, icon=icon_name, prefix=icon_prefix),
                popup=f"{row['Name']} ({fac_type} | Cap: {row['Capacity']})"
            ).add_to(m)

        display(m)

def export_data(b):
    with export_status:
        export_status.clear_output()
        filtered_df = get_filtered_data()
        filename = f"DRRMO_Export_{brgy_filter.value}.csv".replace(' ', '_')
        filtered_df.to_csv(filename, index=False)
        print(f"✅ Successfully exported {len(filtered_df)} records to {filename}")

date_range_filter.observe(update_dashboard, names='value')
type_filter.observe(update_dashboard, names='value')
severity_filter.observe(update_dashboard, names='value')
brgy_filter.observe(update_dashboard, names='value')
fac_type_filter.observe(update_dashboard, names='value')
export_button.on_click(export_data)

filter_style = {'description_width': '110px'}
filter_layout = widgets.Layout(width='300px')
date_range_filter.style = filter_style
type_filter.style, type_filter.layout = filter_style, filter_layout
severity_filter.style, severity_filter.layout = filter_style, filter_layout
brgy_filter.style, brgy_filter.layout = filter_style, filter_layout
fac_type_filter.style, fac_type_filter.layout = filter_style, filter_layout
export_button.layout = widgets.Layout(width='300px', margin='10px 0 0 0')

# ==========================
# DATA ENTRY
# ==========================
fac_types = ["Evacuation Site", "School", "Command Center", "Hospital", "Health Care Center", "Fire Station"]
style = {'description_width': '80px'}
layout = widgets.Layout(width='280px', margin='0 10px 10px 0')

fac_name_in = widgets.Text(description="Name:", style=style, layout=layout)
fac_brgy_in = widgets.Dropdown(options=sorted_brgys, description="Barangay:", style=style, layout=layout)
fac_type_in = widgets.Dropdown(options=fac_types, description="Type:", style=style, layout=layout)
fac_cap_in = widgets.IntText(description="Capacity:", style=style, layout=layout)
fac_occ_in = widgets.IntText(value=0, description="Occupants:", style=style, layout=layout)
fac_res_in = widgets.BoundedIntText(value=100, min=0, max=100, description="Resources %:", style=style, layout=layout)
fac_lat_in = widgets.FloatText(value=14.3333, description="Latitude:", style=style, layout=layout)
fac_lon_in = widgets.FloatText(value=121.0833, description="Longitude:", style=style, layout=layout)
btn_add_fac = widgets.Button(description="Add Facility", button_style='primary', layout=widgets.Layout(width='280px', margin='10px 0 0 0'))

inc_date_in = widgets.DatePicker(description="Date:", style=style, layout=layout)
inc_brgy_in = widgets.Dropdown(options=sorted_brgys, description="Barangay:", style=style, layout=layout)
inc_type_in = widgets.Dropdown(options=["Flood", "Medical Emergency", "Fire", "Traffic Accident", "Structural Collapse"], description="Type:", style=style, layout=layout)
inc_sev_in = widgets.Dropdown(options=severity_levels, description="Severity:", style=style, layout=layout)
inc_aff_in = widgets.IntText(description="Affected:", style=style, layout=layout)
inc_lat_in = widgets.FloatText(value=14.3333, description="Latitude:", style=style, layout=layout)
inc_lon_in = widgets.FloatText(value=121.0833, description="Longitude:", style=style, layout=layout)
btn_add_inc = widgets.Button(description="Add Incident", button_style='danger', layout=widgets.Layout(width='280px', margin='10px 0 0 0'))

out_receipt = widgets.Output()

def add_facility(b):
    global df_fac
    with out_receipt:
        out_receipt.clear_output()
        cap = fac_cap_in.value
        occ = fac_occ_in.value
        if occ >= cap:
            print(f"❌ Occupants ({occ}) must be lower than Capacity ({cap}). Please fix and try again.")
            return
        new_fac = {col: None for col in df_fac.columns}
        new_fac.update({
            'FacilityID': f"F{len(df_fac)+1:03d}",
            'Name': fac_name_in.value,
            'Barangay': fac_brgy_in.value,
            'Type': fac_type_in.value,
            'Capacity': cap,
            'Occupants': occ,
            'ResourcesAvailable': fac_res_in.value,
            'Latitude': fac_lat_in.value,
            'Longitude': fac_lon_in.value
        })
        with open('./this/facilities.csv', 'rb+') as _f:
            _f.seek(-1, 2)
            if _f.read(1) != b'\n':
                _f.write(b'\n')
        pd.DataFrame([new_fac])[df_fac.columns].to_csv('./this/facilities.csv', mode='a', header=False, index=False, lineterminator='\n')
        df_fac = pd.read_csv('./this/facilities.csv')
        print(f"✅ RECEIPT: Added Facility '{new_fac['Name']}' ({new_fac['Type']}) to {new_fac['Barangay']}.")
    update_dashboard()

def add_incident(b):
    global df_incidents
    with out_receipt:
        out_receipt.clear_output()
        dt_str = inc_date_in.value.strftime("%Y-%m-%d 12:00:00") if inc_date_in.value else "2026-05-01 12:00:00"
        new_inc = {
            'IncidentID': f"I{len(df_incidents)+1:03d}",
            'DateTime': dt_str,
            'Barangay': inc_brgy_in.value,
            'Type': inc_type_in.value,
            'Severity': inc_sev_in.value,
            'NumAffected': inc_aff_in.value,
            'Latitude': inc_lat_in.value,
            'Longitude': inc_lon_in.value
        }
        with open('./this/incidents.csv', 'rb+') as _f:
            _f.seek(-1, 2)
            if _f.read(1) != b'\n':
                _f.write(b'\n')
        pd.DataFrame([new_inc]).to_csv('./this/incidents.csv', mode='a', header=False, index=False, lineterminator='\n')
        df_incidents = pd.read_csv('./this/incidents.csv')
        df_incidents['DateTime'] = pd.to_datetime(df_incidents['DateTime'])
        df_incidents['Month'] = df_incidents['DateTime'].dt.to_period('M').astype(str)
        print(f"🚨 RECEIPT: Logged new {new_inc['Severity']} {new_inc['Type']} incident at {new_inc['Barangay']} affecting {new_inc['NumAffected']} people.")
    update_dashboard()

btn_add_fac.on_click(add_facility)
btn_add_inc.on_click(add_incident)

# ==========================
# DISPLAY EVERYTHING
# ==========================
display(HTML("<h1>Integrated DRRM Dashboard</h1>"))

render_kpis()
render_charts()

filter_box = widgets.VBox([
    widgets.HTML("<h3>Interactive OLAP Filters</h3>"),
    date_range_filter,
    date_range_label,
    widgets.HBox([type_filter, severity_filter]),
    widgets.HBox([brgy_filter, fac_type_filter]),
    export_button
], layout=widgets.Layout(padding='15px', border='2px solid #4CAF50', margin='0 0 20px 0', border_radius='10px'))

display(filter_box)
display(export_status)
display(output_table)
display(output_map)

fac_box = widgets.VBox([
    widgets.HTML("<h3>Add New Facility</h3>"),
    widgets.HBox([fac_name_in, fac_brgy_in, fac_type_in]),
    widgets.HBox([fac_cap_in, fac_lat_in, fac_lon_in]),
    widgets.HBox([fac_occ_in, fac_res_in]),
    btn_add_fac
], layout=widgets.Layout(padding='15px', border='1px solid #ccc', margin='0 0 20px 0', border_radius='5px'))

inc_box = widgets.VBox([
    widgets.HTML("<h3>Log New Incident</h3>"),
    widgets.HBox([inc_date_in, inc_brgy_in, inc_type_in]),
    widgets.HBox([inc_sev_in, inc_aff_in, inc_lat_in, inc_lon_in]),
    btn_add_inc
], layout=widgets.Layout(padding='15px', border='1px solid #ccc', margin='0 0 20px 0', border_radius='5px'))

display(fac_box)
display(inc_box)
display(out_receipt)

update_dashboard()
'''

nb.cells = [
    nbf.v4.new_code_cell(dashboard_code)
]

with open("DRRM_Demo_OneCell.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Demo notebook created successfully!")
