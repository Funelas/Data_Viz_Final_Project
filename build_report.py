from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_report():
    doc = Document()
    
    # --- 1. Title Page ---
    title = doc.add_heading('Integrated DRRM Business Intelligence Dashboard', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    course = doc.add_paragraph('Course: Business Intelligence / Data Visualization')
    course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    group = doc.add_paragraph('Group Members: Funelas, Rivera, Torculas')
    group.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    date = doc.add_paragraph('Submission Date: May 2025')
    date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_page_break()
    
    # --- 2. Introduction and BI context ---
    doc.add_heading('1. Introduction and BI Context', level=1)
    doc.add_paragraph(
        "This project is about the Disaster Risk Reduction and Management (DRRM) in Biñan City, Laguna. "
        "Biñan is near Laguna de Bay so it gets flooded easily. "
        "The problem we are trying to solve is the lack of centralized monitoring for incidents, "
        "evacuation centers, and rescue teams."
    )
    doc.add_paragraph(
        "The people who will use this dashboard are the DRRMO Officers and City Planners. "
        "Our dashboard is an Operational and Tactical BI Dashboard. It is operational because it helps the DRRMO monitor "
        "the daily incidents and team availability. It is tactical because it helps them decide where to send resources "
        "like identifying which evacuation centers still have space. This type of dashboard is appropriate because emergency response needs direct and fast metrics, "
        "not just long-term planning."
    )
    
    # --- 3. Data used in the system ---
    doc.add_heading('2. Data Used in the System', level=1)
    doc.add_paragraph("We created our datasets to match the actual barangays and population of Biñan City.")
    
    table1 = doc.add_table(rows=1, cols=3)
    table1.style = 'Table Grid'
    hdr_cells = table1.rows[0].cells
    hdr_cells[0].text = 'Dataset'
    hdr_cells[1].text = 'Key Fields'
    hdr_cells[2].text = 'Used For'
    
    data1 = [
        ('barangays1.csv', 'Barangay, HazardType, HazardLevel, Population', 'Hazard context and Risk Score calculation'),
        ('facilities1.csv', 'Type, Capacity, Barangay', 'Checking evacuation capacity across the city'),
        ('rescue_teams1.csv', 'BaseBarangay, Specialty, Availability', 'Team readiness analysis'),
        ('incidents1.csv', 'DateTime, Type, Severity, NumAffected', 'Trend analysis, mapping, and KPIs')
    ]
    for row in data1:
        row_cells = table1.add_row().cells
        row_cells[0].text = row[0]
        row_cells[1].text = row[1]
        row_cells[2].text = row[2]
        
    # --- 4. Data dictionary, dimensions, and measures ---
    doc.add_heading('3. Data Dictionary, Dimensions, and Measures', level=1)
    doc.add_paragraph("The dashboard uses different fields grouped into Dimensions and Measures:")
    
    table2 = doc.add_table(rows=1, cols=4)
    table2.style = 'Table Grid'
    hdr_cells2 = table2.rows[0].cells
    hdr_cells2[0].text = 'Field'
    hdr_cells2[1].text = 'Data Type'
    hdr_cells2[2].text = 'Classification'
    hdr_cells2[3].text = 'Used In'
    
    data2 = [
        ('Month', 'Text', 'Dimension', 'Time filter, Trend Line Chart'),
        ('Barangay', 'Text', 'Dimension', 'Grouping, Risk Ranking, Map'),
        ('Severity', 'Category', 'Dimension', 'Severity filter, Map colors'),
        ('NumAffected', 'Integer', 'Measure (Additive)', 'Total Affected KPI, Impact analysis'),
        ('Capacity', 'Integer', 'Measure (Additive)', 'Total Capacity KPI, Facility chart'),
        ('RiskScore', 'Float', 'Measure (Non-additive)', 'Finding priority areas')
    ]
    for row in data2:
        row_cells = table2.add_row().cells
        row_cells[0].text = row[0]
        row_cells[1].text = row[1]
        row_cells[2].text = row[2]
        row_cells[3].text = row[3]

    # --- 5. Data processing and ETL ---
    doc.add_heading('4. Data Processing and ETL', level=1)
    doc.add_paragraph(
        "We did the data cleaning (ETL) using Pandas in our Jupyter Notebook. "
        "First, we changed the 'DateTime' column into proper Datetime objects and got the 'Month' "
        "so we can use it as a time dimension. When we checked the data, we found some missing values in 'NumAffected'. "
        "We fixed this by replacing the blank values with the median of NumAffected for that specific Incident Type. "
        "Lastly, we created a new metric called 'Risk Score'. We did this by giving Hazard Levels a weight number "
        "(Critical=4, High=3, Medium=2, Low=1) and multiplying it by the Population divided by 1000."
    )
    
    # --- 6. KPIs and metrics ---
    doc.add_heading('5. KPIs and Metrics', level=1)
    doc.add_paragraph("We implemented exactly 10 strategic KPIs at the top of our dashboard to monitor city-wide performance:")
    
    table3 = doc.add_table(rows=1, cols=3)
    table3.style = 'Table Grid'
    hdr_cells3 = table3.rows[0].cells
    hdr_cells3[0].text = 'KPI / Metric'
    hdr_cells3[1].text = 'Source Field'
    hdr_cells3[2].text = 'Supports What Decision?'
    
    data3 = [
        ('Total Incidents', 'Count of incidents1.csv', 'Monitors the overall operational load'),
        ('Total Affected', 'NumAffected', 'Checks the impact severity of disasters'),
        ('Available Teams', 'OnDuty', 'Checks the readiness for dispatches'),
        ('Total Capacity', 'Capacity', 'Checks if current resources are enough'),
        ('Highest Risk Brgy', 'Derived RiskScore', 'Prioritizes mitigation focus'),
        ('Evac Centers', 'Type == EvacuationSite', 'Monitors shelter availability'),
        ('Water Rescue Teams', 'Specialty == WaterRescue', 'Evaluates flood response capability'),
        ('Critical Events', 'Severity == Critical', 'Flags high-priority emergencies'),
        ('Avg Brgy Population', 'Population', 'Context for resource distribution'),
        ('Total Barangays', 'Count of barangays.csv', 'Scopes the city-wide coverage')
    ]
    for row in data3:
        row_cells = table3.add_row().cells
        row_cells[0].text = row[0]
        row_cells[1].text = row[1]
        row_cells[2].text = row[2]
        
    # --- 7. Dashboard design and visuals ---
    doc.add_heading('6. Dashboard Design and Explanation of Visuals', level=1)
    doc.add_paragraph("The dashboard includes strategic summary tables and visualizations:")
    doc.add_paragraph("1. Resource Summary Tables: Provides raw counts of facilities per barangay and teams per specialty for detailed monitoring.")
    doc.add_paragraph("2. Incident Trend Over Time (Line Chart): Uses Month and Incident Count. It answers 'Are incidents increasing?' and helps the DRRMO prepare.")
    doc.add_paragraph("2. Incident Composition by Type (Horizontal Bar): Uses Incident Type. It answers 'What hazards are most frequent?' so they know what training the rescue teams need.")
    doc.add_paragraph("3. Top 10 High-Risk Barangays (Bar Chart): Uses Barangay and RiskScore. Answers 'Where should we focus our mitigation efforts?'")
    doc.add_paragraph("4. Total Facility Capacity (Bar Chart): Uses Barangay and Capacity. It shows which areas have good evacuation centers and which ones need more.")
    doc.add_paragraph("5. Incident Severity Breakdown (Pie Chart): Shows the proportion of Critical vs Low incidents so the threat level is clear at a glance.")
    doc.add_paragraph("6. Interactive Folium Map: Shows where the incidents and facilities are on the map using color-coded severity markers (scaled by size) and custom icons for Schools, Command Centers, and Hospitals.")
    
    # --- 8. Operational Data Entry ---
    doc.add_heading('7. Operational Data Entry and Real-time Logging', level=1)
    doc.add_paragraph(
        "To make the dashboard useful for daily operations, we added a Data Entry section. "
        "DRRMO staff can use the interactive forms to register new Facilities (like a new School or Fire Station) "
        "and log new Incidents in real-time. These records are immediately appended to our datasets, and a "
        "receipt is generated to confirm the entry."
    )

    # --- 9. Interaction and analytical navigation ---
    doc.add_heading('8. Interaction and Analytical Navigation (OLAP)', level=1)
    doc.add_paragraph(
        "Our dashboard uses Slice and Dice OLAP techniques using ipywidgets. The user can filter by "
        "Month, Incident Type, and Severity. When these filters are changed, the data table (Details on Demand) "
        "and the Folium Map will update right away."
    )
    doc.add_paragraph(
        "Slice: Filtering to see only the 'Flood' incidents.\n"
        "Dice: Filtering to see 'Flood' incidents that are 'Critical' severity during 'April'.\n"
        "Drill-down: Users can see the big KPI number like 250 incidents, then use the map or table to drill-down and see "
        "the exact street and details of a specific incident.\n"
        "Roll-up: We rolled up the daily incidents into a 'Month' dimension to see the monthly trends easily."
    )
    
    # --- 10. DRRM insights and recommendations ---
    doc.add_heading('9. DRRM Insights and Recommendations', level=1)
    doc.add_paragraph(
        "Based on our dashboard, the Barangays near Laguna de Bay like Malaban, Casile, and De La Paz are always the highest "
        "in Risk Score because they have a lot of people and 'Critical' flood hazard levels. Flood is also the most common incident. "
        "Recommendation: The DRRMO should place Water Rescue teams directly in Malaban and Casile instead of keeping them in the main office. "
        "Also, the evacuation centers in these barangays need to be made bigger because they can get full very fast."
    )
    
    # --- 11. Limitations and future improvements ---
    doc.add_heading('10. Limitations and Future Improvements', level=1)
    doc.add_paragraph(
        "One limitation is that we are using simulated data for Biñan City, but we designed the coordinates "
        "and barangays to be as accurate as possible to act like a real GPS system. For future improvements, "
        "we could integrate real-time weather feeds and a live SMS alert system for citizens."
    )

    doc.save('DRRMFinalReport_Funelas_Rivera_Torculas.docx')

if __name__ == "__main__":
    create_report()
