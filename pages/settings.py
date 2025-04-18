import streamlit as st
import sys
sys.path.append('..')
from config import config

st.title("Analysis Settings")

# Initialize session state for settings
if 'use_finite_elements' not in st.session_state:
    st.session_state.use_finite_elements = False
    
if 'num_finite_elements' not in st.session_state:
    st.session_state.num_finite_elements = config.get_FEDivision()  # Get initial value from config

# Create a form for analysis settings
with st.form("analysis_settings"):
    st.subheader("Finite Element Divisor Settings")
    
    # FEDivision setting from config.py (used in calculations)
    fedivision = st.slider("FE Division (Number of Divisions for Visuvalization)", 
                           min_value=5, 
                           max_value=1000, 
                           value=config.get_FEDivision(),
                           step=5,
                           help="Controls the number of divisions used for load calculations and BMD plotting for Visualization. Higher values give more accurate results.")
    
    st.markdown("---")
    
    # Option to enable/disable finite element division for visualization
    st.subheader("Finite Element Creator Settings")
    use_fe = st.checkbox("Use Finite Element Division for Analysis", 
                         value=st.session_state.use_finite_elements,
                         help="Enable this to divide each member into multiple elements for Analysis")
    
    # Number of elements per member for visualization
    num_elements = st.slider("Number of Elements per Member for Visualization", 
                            min_value=2, 
                            max_value=50, 
                            value=st.session_state.num_finite_elements,
                            step=1,
                            help="Controls the number of elements used for visualization. More elements provide smoother diagrams.")
    
    # Explanation of the settings
    with st.expander("About Finite Element Settings"):
        st.write("""
        This application has two different finite element settings:
        
        **1. FE Division:** Controls the number of divisions used for internal calculations in loads and stress analysis. 
        This affects accuracy of all numerical results. The default is 20 divisions.
        
        **2. Visualization Elements:** Creates new members by dividing existing members for Detialled analysis(Used in second Order Buckling calculation). 
        This affects the Buckling value accurary and Second Order Results.
        
        For most purposes, you can leave the FE Division at the default value and adjust the FE Creator 
        elements based on your preference for accuracy of Second Order Results.
        """)
    
    # Submit button
    submitted = st.form_submit_button("Save Settings")
    
    if submitted:
        # Update session state with new values
        st.session_state.use_finite_elements = use_fe
        st.session_state.num_finite_elements = num_elements
        
        # Update config object when settings are saved
        config.set_FEDivision(fedivision)
        
        st.success(f"Settings saved successfully! FE Division set to {fedivision}")

# Display current settings
st.subheader("Current Settings")
st.write(f"**FE Division (Calculation):** {config.get_FEDivision()} divisions")
st.write(f"**Finite Element Division (Visualization):** {'Enabled' if st.session_state.use_finite_elements else 'Disabled'}")
if st.session_state.use_finite_elements:
    st.write(f"**Elements per Member (Visualization):** {st.session_state.num_finite_elements}")

# Additional information about the analysis
st.subheader("Analysis Information")
st.write("""
This structural analysis application uses a simplified finite element method for analyzing frame structures.
The analysis provides:

- Member internal forces and moments
- Nodal displacements and reactions
- Stress and strain distributions along members

For complex structures, increasing the Finite Element Creator can provide more accurate numerical results.
""")

# Performance considerations
st.info("""
**Performance Note:** Using a large number of Finite Element Creator (>50) may increase computation time.
Start with the default value and increase as needed for more accurate results.
""") 