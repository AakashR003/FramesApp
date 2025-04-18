import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import io
import matplotlib.pyplot as plt
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append('..')
from StructuralElements import Node, Member
from Loads import NeumanBC
from FirstOrderResponse import FirstOrderMemberResponse
from SecondOrderResponse import SecondOrderMemberResponse
from Comparision import Comparision

# Initialize session state if not exists
if 'comparison_results' not in st.session_state:
    st.session_state.comparison_results = {}

# Ensure nodes, members, and loads are initialized
if 'nodes' not in st.session_state:
    st.session_state.nodes = {}

if 'members' not in st.session_state:
    st.session_state.members = {}

if 'loads' not in st.session_state:
    st.session_state.loads = []

# Load data from files if available but not in session state
def load_data_if_needed():
    # Load nodes if needed
    if len(st.session_state.nodes) == 0 and os.path.exists('data/nodes.json'):
        with open('data/nodes.json', 'r') as f:
            nodes_data = json.load(f)
            # Recreate Node objects
            st.session_state.nodes = {}
            for node_id, node_data in nodes_data.items():
                node = Node(
                    node_data["node_number"],
                    node_data["xcoordinate"],
                    node_data["ycoordinate"],
                    node_data["support_condition"]
                )
                st.session_state.nodes[node_id] = node
    
    # Load members if needed
    if len(st.session_state.members) == 0 and os.path.exists('data/members.json'):
        with open('data/members.json', 'r') as f:
            members_data = json.load(f)
            # Recreate Member objects
            st.session_state.members = {}
            for member_id, member_data in members_data.items():
                start_node = st.session_state.nodes[member_data["start_node_id"]]
                end_node = st.session_state.nodes[member_data["end_node_id"]]
                
                member = Member(
                    member_data["beam_number"],
                    start_node,
                    end_node,
                    member_data["area"],
                    member_data["youngs_modulus"],
                    member_data["moment_of_inertia"],
                    member_data["density"]
                )
                st.session_state.members[member_id] = member
    
    # Load loads if needed
    if len(st.session_state.loads) == 0 and os.path.exists('data/loads.json'):
        with open('data/loads.json', 'r') as f:
            loads_data = json.load(f)
            
            # Recreate load objects
            st.session_state.loads = []
            members_list = list(st.session_state.members.values())
            
            for load_data in loads_data:
                # Create load using NeumanBC class
                kwargs = {
                    "type": load_data["type"],
                    "Magnitude": load_data["magnitude"],
                    "Distance1": load_data["distance1"],
                    "AssignedTo": load_data["assigned_to"],
                    "Members": members_list
                }
                
                if load_data["distance2"] is not None:
                    kwargs["Distance2"] = load_data["distance2"]
                
                load = NeumanBC(**kwargs)
                st.session_state.loads.append(load)

# Function to create response models
def get_comparison_models():
    # Extract required data in the format expected by response models
    points = list(st.session_state.nodes.values())
    members = list(st.session_state.members.values())
    loads = st.session_state.loads
    
    # Check if finite element division is enabled (from settings page)
    if st.session_state.get('use_finite_elements', False):
        from FiniteElementDivisor import divide_into_finite_elements
        
        num_elements = st.session_state.get('num_finite_elements', 1)
        if num_elements > 1:
            # Only import when needed to avoid circular imports
            points, members, loads = divide_into_finite_elements(points, members, loads, num_elements)
    
    # Create the analysis models
    first_order_model = FirstOrderMemberResponse(Points=points, Members=members, Loads=loads)
    second_order_model = SecondOrderMemberResponse(Points=points, Members=members, Loads=loads)
    
    # Create and return the Comparison instance
    return Comparision(MainModel=first_order_model, Model2=second_order_model)

# Function to convert matplotlib figure to Streamlit compatible
def plt_to_streamlit():
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    st.image(buf)
    plt.close()

# Main layout
st.title("First Order vs Second Order Analysis Comparison")

# Display finite element settings status from settings page
use_fe = st.session_state.get('use_finite_elements', False)
num_elements = st.session_state.get('num_finite_elements', 1)

if use_fe and num_elements > 1:
    st.info(f"Using Finite Element Division with {num_elements} elements per member. You can adjust these settings in the Settings page.")
else:
    st.info("Finite Element Division is disabled. You can enable it in the Settings page.")

# Load data if needed
load_data_if_needed()

# Check if we have the necessary data
if not st.session_state.nodes or not st.session_state.members:
    st.warning("You need to create nodes and members first. Please go to the Node Input and Member Input pages.")
    st.stop()

if not st.session_state.loads:
    st.warning("You need to create loads first. Please go to the Load Input page.")
    st.stop()

# Create tabs for different comparison visualizations
tab1, tab2, tab3 = st.tabs([
    "Bending Moment Diagram Comparison", 
    "Shear Force Diagram Comparison", 
    "Deflection Comparison"
])

# Tab 1: BMD Comparison
with tab1:
    st.header("Bending Moment Diagram Comparison")
    st.markdown("Compare the bending moment diagrams from first-order and second-order analysis.")
    
    # Dynamic scale factor control with slider and fine adjustment
    col1, col2 = st.columns([3, 1])
    with col1:
        scale_factor = st.slider("Scale Factor for BMD", min_value=0.01, max_value=20.0, value=1.0, step=0.01, key="bmd_scale")
    with col2:
        fine_adjust = st.number_input("Fine Adjust", min_value=0.001, max_value=50.0, value=scale_factor, step=0.001, key="bmd_fine_adjust")
        if fine_adjust != scale_factor:
            scale_factor = fine_adjust
    
    # Option to show structure
    show_structure = st.checkbox("Show Structure", value=True, key="show_structure_bmd")
    
    if st.button("Generate BMD Comparison", key="btn_bmd_comparison"):
        try:
            # Create comparison object
            comparison_model = get_comparison_models()
            
            # Generate and display plot
            comparison_model.PlotGlobalBMDComparison(scale_factor=scale_factor, show_structure=show_structure)
            plt_to_streamlit()
            
            # Add legend explanation
            st.write("Legend:")
            st.markdown("- **Green line**: First Order Analysis BMD")
            st.markdown("- **Red line**: Second Order Analysis BMD")
            
        except Exception as e:
            st.error(f"Error generating BMD comparison: {str(e)}")

# Tab 2: SFD Comparison
with tab2:
    st.header("Shear Force Diagram Comparison")
    st.markdown("Compare the shear force diagrams from first-order and second-order analysis.")
    
    # Dynamic scale factor control with slider and fine adjustment
    col1, col2 = st.columns([3, 1])
    with col1:
        scale_factor = st.slider("Scale Factor for SFD", min_value=0.01, max_value=20.0, value=1.0, step=0.01, key="sfd_scale")
    with col2:
        fine_adjust = st.number_input("Fine Adjust", min_value=0.001, max_value=50.0, value=scale_factor, step=0.001, key="sfd_fine_adjust")
        if fine_adjust != scale_factor:
            scale_factor = fine_adjust
    
    # Option to show structure
    show_structure = st.checkbox("Show Structure", value=True, key="show_structure_sfd")
    
    if st.button("Generate SFD Comparison", key="btn_sfd_comparison"):
        try:
            # Create comparison object
            comparison_model = get_comparison_models()
            
            # Generate and display plot
            comparison_model.PlotGlobalSFDComparison(scale_factor=scale_factor, show_structure=show_structure)
            plt_to_streamlit()
            
            # Add legend explanation
            st.write("Legend:")
            st.markdown("- **Green line**: First Order Analysis SFD")
            st.markdown("- **Red line**: Second Order Analysis SFD")
            
        except Exception as e:
            st.error(f"Error generating SFD comparison: {str(e)}")

# Tab 3: Deflection Comparison
with tab3:
    st.header("Deflection Comparison")
    st.markdown("Compare the deflection diagrams from first-order and second-order analysis.")
    
    # Dynamic scale factor control with slider and fine adjustment
    col1, col2 = st.columns([3, 1])
    with col1:
        scale_factor = st.slider("Scale Factor for Deflection", min_value=0.1, max_value=100.0, value=10.0, step=0.1, key="defl_scale")
    with col2:
        fine_adjust = st.number_input("Fine Adjust", min_value=0.1, max_value=500.0, value=scale_factor, step=0.1, key="defl_fine_adjust")
        if fine_adjust != scale_factor:
            scale_factor = fine_adjust
    
    # Option to show structure
    show_structure = st.checkbox("Show Structure", value=True, key="show_structure_defl")
    
    if st.button("Generate Deflection Comparison", key="btn_defl_comparison"):
        try:
            # Create comparison object
            comparison_model = get_comparison_models()
            
            # Generate and display plot
            comparison_model.PlotGlobalDeflectionComparison(scale_factor=scale_factor, show_structure=show_structure)
            plt_to_streamlit()
            
            # Add legend explanation
            st.write("Legend:")
            st.markdown("- **Green line**: First Order Analysis Deflection")
            st.markdown("- **Red line**: Second Order Analysis Deflection")
            
        except Exception as e:
            st.error(f"Error generating deflection comparison: {str(e)}") 