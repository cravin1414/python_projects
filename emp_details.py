from fpdf import FPDF

# Sample employee data
employees = [
    {"ID": 1, "Name": "Alice Johnson", "Department": "HR", "Position": "Manager", "Salary": 70000},
    {"ID": 2, "Name": "Bob Smith", "Department": "Engineering", "Position": "Software Engineer", "Salary": 85000},
    {"ID": 3, "Name": "Charlie Davis", "Department": "Marketing", "Position": "Executive", "Salary": 60000},
    {"ID": 4, "Name": "Dana Lee", "Department": "Sales", "Position": "Sales Representative", "Salary": 55000},
    {"ID": 5, "Name": "Ethan Brown", "Department": "Finance", "Position": "Analyst", "Salary": 65000}
]

# Create PDF report
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Employee Report", ln=True, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def employee_table(self, data):
        self.set_font("Arial", "B", 10)
        self.cell(20, 10, "ID", 1)
        self.cell(40, 10, "Name", 1)
        self.cell(40, 10, "Department", 1)
        self.cell(50, 10, "Position", 1)
        self.cell(30, 10, "Salary", 1)
        self.ln()

        self.set_font("Arial", "", 10)
        for emp in data:
            self.cell(20, 10, str(emp["ID"]), 1)
            self.cell(40, 10, emp["Name"], 1)
            self.cell(40, 10, emp["Department"], 1)
            self.cell(50, 10, emp["Position"], 1)
            self.cell(30, 10, f"${emp['Salary']:,}", 1)
            self.ln()

pdf = PDF()
pdf.add_page()
pdf.employee_table(employees)

# Save the PDF
pdf.output("Employee_Report.pdf")
