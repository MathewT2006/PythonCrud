import streamlit as st
import psycopg2
import pandas as pd

# Database connection details
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "mydb"  # Replace with your database name
DB_USER = "mathew"        # Replace with your PostgreSQL username
DB_PASS = "YahBoi123"        # Replace with your PostgreSQL password

# Function to connect to the PostgreSQL database
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg2.OperationalError as e:
        st.error(f"Unable to connect to the database. Please check your connection details and ensure the database is running. Error: {e}")
        return None

# Function to read all employees from the database
def read_employees():
    """Reads all employee data from the 'employee' table."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM employee ORDER BY id DESC")
            employees = cur.fetchall()
            columns = [desc[0] for desc in cur.description] # Get column names
        conn.close()
        return employees, columns
    return [], []

#Adding new employee
def add_employee(name, department, salary):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO employee (name, department, salary) VALUES (%s, %s, %s)",
                    (name, department, salary)
                )
                conn.commit()
                st.success("Employee added successfully!")
            except psycopg2.Error as e:
                st.error(f"Error adding employee: {e}")
            finally:
                conn.close()

#Deleteing employees
def delete_employee(emp_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            try:
                cur.execute("DELETE FROM employee WHERE id = %s", (emp_id,))
                conn.commit()
                if cur.rowcount > 0:
                    st.success("Successfully deleted employee with id: " + str(emp_id))
                else:
                    st.warning("No employee found with the given ID: "  + str(emp_id))
            except psycopg2.Error as e:
                st.error(f"Error deleting employee: {e}")
            finally:
                conn.close()


# Main Streamlit App
st.set_page_config(page_title="Employee Data", layout="wide")

def main():
    """Main function for the Streamlit application."""
    st.title("Employee Data Viewer")
    st.markdown("---")


    col1, col2 = st.columns(2)

    with col1:
        st.header("Add New Employee")
        with st.form(key="add_form", clear_on_submit=True):
            new_name = st.text_input("Name")
            new_department = st.text_input("Department")
            new_salary = st.number_input("Salary", min_value=0, format="%.2f")

            submit_button = st.form_submit_button(label="Add Employee")
            
            if submit_button:
                if new_name and new_department and new_salary is not None:
                    add_employee(new_name, new_department, new_salary)
                    st.rerun()
                else:
                    st.error("Please fill in all fields to add a new employee.")

    with col2:
        st.header("Delete Employee")
        with st.form(key="delete_form", clear_on_submit=True):
            del_id = st.number_input("Employee ID to Delete", min_value=1, step=1)

            delete_button = st.form_submit_button(label="Delete Employee")
        
            if delete_button:
                delete_employee(del_id)
                st.rerun()


    st.markdown("---")
    employees, columns = read_employees()

    if employees:
        # Convert the list of tuples to a DataFrame for better display
        df = pd.DataFrame(employees, columns=columns)
        st.subheader("Current Employee List")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No employee data found. Please check your database connection and the 'employees' table.")

if __name__ == "__main__":
    main()
