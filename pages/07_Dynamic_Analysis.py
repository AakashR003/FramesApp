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
from DynamicResponse import DynamicGlobalResponse

# Initialize session state for dynamic analysis results if not exists
if 'dynamic_analysis_results' not in st.session_state:
    st.session_state.dynamic_analysis_results = {}

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

# Function to create DynamicGlobalResponse instance with data from session state
def get_dynamic_response():
    # Extract required data in the format expected by DynamicGlobalResponse
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
    
    # Create and return the DynamicGlobalResponse instance
    return DynamicGlobalResponse(Points=points, Members=members, Loads=loads)

# Function to convert matplotlib figure to Streamlit compatible
def plt_to_streamlit():
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    st.image(buf)
    plt.close()

# Main layout
st.title("Dynamic Analysis")

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

# Create tabs for different analysis functions
tab1, tab2 = st.tabs([
    "Eigenfrequency Analysis", 
    "Eigenmode Visualization"
])

# Tab 1: Eigenfrequency Analysis
with tab1:
    st.header("Eigenfrequency Analysis")
    st.markdown("Calculate the natural frequencies of the structure.")
    
    if st.button("Calculate Eigenfrequencies", key="btn_eigenfreq"):
        try:
            # Create dynamic response object
            dynamic_response = get_dynamic_response()
            
            # Calculate eigenfrequencies
            min_freq, all_freqs, eigenmodes = dynamic_response.EigenFrequency()
            
            # Store in session state
            st.session_state.dynamic_analysis_results["eigenfrequencies"] = all_freqs
            st.session_state.dynamic_analysis_results["eigenmodes"] = eigenmodes
            
            # Display results
            st.success(f"Eigenfrequencies calculated successfully!")
            
            # Create DataFrame for display - limit to first 10 frequencies
            display_freqs = all_freqs[:10] if len(all_freqs) > 10 else all_freqs
            df = pd.DataFrame({
                "Mode Number": list(range(1, len(display_freqs) + 1)),
                "Frequency (Hz)": display_freqs
            })
            
            st.dataframe(df, use_container_width=True)
            
            # Plot the frequencies as a bar chart
            st.markdown("### Frequency Spectrum")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(list(range(1, len(display_freqs) + 1)), display_freqs)
            ax.set_xlabel("Mode Number")
            ax.set_ylabel("Frequency (Hz)")
            ax.set_title("Eigenfrequencies of the Structure")
            ax.grid(True, linestyle='--', alpha=0.7)
            plt_to_streamlit()
            
        except Exception as e:
            st.error(f"Error calculating eigenfrequencies: {str(e)}")

# Tab 2: Eigenmode Visualization
with tab2:
    st.header("Eigenmode Visualization")
    st.markdown("Visualize the eigenmodes (natural vibration patterns) of the structure.")
    
    # Check if eigenfrequencies have been calculated
    if "eigenfrequencies" not in st.session_state.dynamic_analysis_results:
        st.warning("Please calculate eigenfrequencies first in the Eigenfrequency Analysis tab.")
    else:
        # Mode selection
        all_freqs = st.session_state.dynamic_analysis_results["eigenfrequencies"]
        max_modes = min(10, len(all_freqs))  # Limit to 10 modes for UI simplicity
        
        mode_number = st.slider("Select Eigenmode Number", min_value=1, max_value=max_modes, value=1, step=1)
        
        # Dynamic scale factor control with slider and fine adjustment
        col1, col2 = st.columns([3, 1])
        with col1:
            scale_factor = st.slider("Scale Factor", min_value=0.1, max_value=200.0, value=20.0, step=0.1)
        with col2:
            fine_adjust = st.number_input("Fine Adjust", min_value=0.01, max_value=1000.0, value=scale_factor, step=0.01)
            if fine_adjust != scale_factor:
                scale_factor = fine_adjust
        
        # Option to show structure
        show_structure = st.checkbox("Show Original Structure", value=True)
        
        if st.button("Visualize Eigenmode", key="btn_eigenmode"):
            try:
                # Create dynamic response object
                dynamic_response = get_dynamic_response()
                
                # Plot eigenmode
                dynamic_response.PlotDynamicEigenMode(
                    EigenModeNo=mode_number,
                    scale_factor=scale_factor,
                    show_structure=show_structure
                )
                
                # Convert matplotlib figure to Streamlit
                plt_to_streamlit()
                
                # Display frequency of this mode
                st.info(f"Mode {mode_number} frequency: {all_freqs[mode_number-1]} Hz")
                
                # Add explanation
                st.markdown("""
                **Understanding Eigenmodes:**
                - Eigenmodes represent the natural vibration patterns of the structure.
                - Each mode has a corresponding natural frequency.
                - In an earthquake or dynamic loading, these modes can be excited.
                - Lower modes (especially the first few) typically contribute most to structural response.
                """)
                
            except Exception as e:
                st.error(f"Error visualizing eigenmode: {str(e)}") 