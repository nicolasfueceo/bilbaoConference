import streamlit as st
from frontend.utils.api_utils import get_rules, add_rule, delete_rule


def exclusion_list():
    st.title("Exclusion List")
    st.subheader("Manage content exclusions (e.g., banned words, topics)")

    # Fetch and display the current rules from the backend
    rules_data = get_rules()
    if "error" in rules_data:
        st.error(f"Error fetching rules: {rules_data['error']}")
    else:
        st.write("Current Exclusion Rules:")
        for rule in rules_data.get("rules", []):
            st.write(f"{rule['content']}")
            # Add delete button for each rule
            if st.button(f"Delete Rule", key=f"delete_{rule['id']}"):
                delete_result = delete_rule(rule['id'])
                if "error" in delete_result:
                    st.error(f"Error deleting rule: {delete_result['error']}")
                else:
                    st.success(f"Rule {rule['id']} deleted successfully!")
                    st.rerun()  # Reload the page to reflect changes

    # Add a new exclusion rule
    new_rule = st.text_input("Enter a new exclusion rule")
    if st.button("Add Rule", key="add_rule"):
        if new_rule:
            result = add_rule(new_rule)
            if "error" in result:
                st.error(f"Error adding rule: {result['error']}")
            else:
                st.success(f"Rule added successfully! Rule ID: {result['id']}")
                st.rerun()  # Reload the page to reflect changes
        else:
            st.error("Please enter a rule.")
