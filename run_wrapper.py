import sys
import frappe

# Init frappe environment
frappe.init(site="gameplan.localhost", sites_path="/home/frappe/frappe-bench/sites")
frappe.connect()

# Add the directory to path so we can import the module correctly
sys.path.insert(0, "/workspace/gameplan/gameplan")

# Import and run our DocType generator
import install_phase1
install_phase1.execute()
