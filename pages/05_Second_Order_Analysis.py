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
from SecondOrderResponse import SecondOrderMemberResponse, SecondOrderGlobalResponse

# Initialize session state for analysis results if not exists
if 'second_order_analysis_results' not in st.session_state:
    st.session_state.second_order_analysis_results = {}

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

# Function to create SecondOrderMemberResponse instance with data from session state
def get_second_order_member_response():
    # Extract required data in the format expected by SecondOrderMemberResponse
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
    
    # Create and return the SecondOrderMemberResponse instance
    return SecondOrderMemberResponse(Points=points, Members=members, Loads=loads)

# Function to create SecondOrderGlobalResponse instance with data from session state
def get_second_order_global_response():
    # Extract required data in the format expected by SecondOrderGlobalResponse
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
    
    # Create and return the SecondOrderGlobalResponse instance
    return SecondOrderGlobalResponse(Points=points, Members=members, Loads=loads)

# Function to convert matplotlib figure to Streamlit compatible
def plt_to_streamlit():
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    st.image(buf)
    plt.close()

# Main layout
st.title("Second Order Analysis")

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

# Create tabs for different analysis functions
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Member Displacement", 
    "Member Forces", 
    "Bending Moment Diagram", 
    "Shear Force Diagram",
    "Deflection",
    "Buckling Analysis"
])

# Tab 1: Member Displacement
with tab1:
    st.header("Second Order Member Displacement Analysis")
    
    member_ids = list(st.session_state.members.keys())
    selected_member_id = st.selectbox("Select Member", member_ids, key="displacement_member_2nd")
    selected_member = st.session_state.members[selected_member_id]
    
    iteration_steps = st.slider("Iteration Steps", 1, 10, 5, 1, 
                               help="Number of iterations for second order analysis")
    
    if st.button("Calculate Displacement", key="btn_displacement_2nd"):
        try:
            # Create second order member response object
            member_response = get_second_order_member_response()
            
            # Calculate displacement
            displacement = member_response.MemberDisplacement(selected_member.Beam_Number)
            
            # Store in session state
            st.session_state.second_order_analysis_results["displacement"] = displacement
            
            # Display results
            st.success(f"Second Order Displacement calculated for Member {selected_member_id}")
            
            # Create DataFrame for display
            df = pd.DataFrame({
                "DOF": ["Horizontal Start", "Vertical Start", "Rotation Start", 
                        "Horizontal End", "Vertical End", "Rotation End"],
                "Displacement": displacement
            })
            
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error calculating second order displacement: {str(e)}")

# Tab 2: Member Forces
with tab2:
    st.header("Second Order Member Forces Analysis")
    
    force_tab1, force_tab2 = st.tabs(["Local Forces", "Global Forces"])
    
    with force_tab1:
        member_ids = list(st.session_state.members.keys())
        selected_member_id = st.selectbox("Select Member", member_ids, key="local_force_member_2nd")
        selected_member = st.session_state.members[selected_member_id]
        
        if st.button("Calculate Local Forces", key="btn_local_force_2nd"):
            try:
                # Create second order member response object
                member_response = get_second_order_member_response()
                
                # Calculate forces
                forces = member_response.MemberForceLocal(selected_member.Beam_Number)
                
                # Store in session state
                st.session_state.second_order_analysis_results["local_forces"] = forces
                
                # Display results
                st.success(f"Second Order Local forces calculated for Member {selected_member_id}")
                
                # Create DataFrame for display
                df = pd.DataFrame({
                    "Force Component": ["Axial Force Start", "Shear Force Start", "Moment Start", 
                                       "Axial Force End", "Shear Force End", "Moment End"],
                    "Value": forces
                })
                
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error calculating second order local forces: {str(e)}")
    
    with force_tab2:
        member_ids = list(st.session_state.members.keys())
        selected_member_id = st.selectbox("Select Member", member_ids, key="global_force_member_2nd")
        selected_member = st.session_state.members[selected_member_id]
        
        if st.button("Calculate Global Forces", key="btn_global_force_2nd"):
            try:
                # Create second order member response object
                member_response = get_second_order_member_response()
                
                # Calculate forces
                forces = member_response.MemberForceGlobal(selected_member.Beam_Number)
                
                # Store in session state
                st.session_state.second_order_analysis_results["global_forces"] = forces
                
                # Display results
                st.success(f"Second Order Global forces calculated for Member {selected_member_id}")
                
                # Create DataFrame for display
                df = pd.DataFrame({
                    "Force Component": ["Fx Start", "Fy Start", "Mz Start", 
                                       "Fx End", "Fy End", "Mz End"],
                    "Value": forces
                })
                
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error calculating second order global forces: {str(e)}")

# Tab 3: Bending Moment Diagram
with tab3:
    st.header("Second Order Bending Moment Diagram")
    
    bmd_tab1, bmd_tab2 = st.tabs(["Individual Member BMD", "Global Structure BMD"])
    
    with bmd_tab1:
        member_ids = list(st.session_state.members.keys())
        selected_member_id = st.selectbox("Select Member", member_ids, key="bmd_member_2nd")
        selected_member = st.session_state.members[selected_member_id]
        
        if st.button("Plot Bending Moment Diagram", key="btn_bmd_2nd"):
            try:
                # Create second order member response object
                member_response = get_second_order_member_response()
                
                # Generate plot
                fig = plt.figure(figsize=(10, 6))
                member_response.PlotMemberBMD(selected_member.Beam_Number)
                
                # Convert plot to Streamlit
                plt_to_streamlit()
                
                # Also get the numeric data
                moments = member_response.MemberBMD(selected_member.Beam_Number)
                positions = member_response.MemberAmplitude(selected_member.Beam_Number)
                
                # Store in session state
                st.session_state.second_order_analysis_results["bmd"] = {
                    "moments": moments,
                    "positions": positions
                }
                
                # Display numerical data in a table if desired
                if st.checkbox("Show Numerical Data", key="show_bmd_data_2nd"):
                    data = pd.DataFrame({
                        "Position (m)": positions,
                        "Moment (Nm)": moments
                    })
                    st.dataframe(data, use_container_width=True)
            except Exception as e:
                st.error(f"Error plotting second order bending moment diagram: {str(e)}")
    
    with bmd_tab2:
        # Dynamic scale factor control with slider and fine adjustment
        col1, col2 = st.columns([3, 1])
        with col1:
            scale_factor = st.slider("Scale Factor", min_value=0.01, max_value=10.0, value=0.5, step=0.01, key="bmd_scale_2nd")
        with col2:
            fine_adjust = st.number_input("Fine Adjust", min_value=0.001, max_value=50.0, value=scale_factor, step=0.001, key="bmd_fine_adjust_2nd")
            if fine_adjust != scale_factor:
                scale_factor = fine_adjust
        
        show_structure = st.checkbox("Show Structure", value=True, key="bmd_show_structure_2nd")
        
        if st.button("Plot Global Bending Moment Diagram", key="btn_global_bmd_2nd"):
            try:
                # Create second order member response object
                member_response = get_second_order_member_response()
                
                # Generate plot
                member_response.PlotGlobalBMD(scale_factor=scale_factor, show_structure=show_structure)
                
                # Convert plot to Streamlit
                plt_to_streamlit()
            except Exception as e:
                st.error(f"Error plotting second order global bending moment diagram: {str(e)}")

# Tab 4: Shear Force Diagram
with tab4:
    st.header("Second Order Shear Force Diagram")
    
    sfd_tab1, sfd_tab2 = st.tabs(["Individual Member SFD", "Global Structure SFD"])
    
    with sfd_tab1:
        member_ids = list(st.session_state.members.keys())
        selected_member_id = st.selectbox("Select Member", member_ids, key="sfd_member_2nd")
        selected_member = st.session_state.members[selected_member_id]
        
        if st.button("Plot Shear Force Diagram", key="btn_sfd_2nd"):
            try:
                # Create second order member response object
                member_response = get_second_order_member_response()
                
                # Generate plot
                fig = plt.figure(figsize=(10, 6))
                member_response.PlotMemberSFD(selected_member.Beam_Number)
                
                # Convert plot to Streamlit
                plt_to_streamlit()
                
                # Also get the numeric data
                shear_forces = member_response.MemberSFD(selected_member.Beam_Number)
                positions = member_response.MemberAmplitude(selected_member.Beam_Number)
                
                # Store in session state
                st.session_state.second_order_analysis_results["sfd"] = {
                    "shear_forces": shear_forces,
                    "positions": positions
                }
                
                # Display numerical data in a table if desired
                if st.checkbox("Show Numerical Data", key="show_sfd_data_2nd"):
                    data = pd.DataFrame({
                        "Position (m)": positions[:len(shear_forces)],
                        "Shear Force (N)": shear_forces
                    })
                    st.dataframe(data, use_container_width=True)
            except Exception as e:
                st.error(f"Error plotting second order shear force diagram: {str(e)}")
    
    with sfd_tab2:
        # Dynamic scale factor control with slider and fine adjustment
        col1, col2 = st.columns([3, 1])
        with col1:
            scale_factor = st.slider("Scale Factor", min_value=0.01, max_value=10.0, value=0.5, step=0.01, key="sfd_scale_2nd")
        with col2:
            fine_adjust = st.number_input("Fine Adjust", min_value=0.001, max_value=50.0, value=scale_factor, step=0.001, key="sfd_fine_adjust_2nd")
            if fine_adjust != scale_factor:
                scale_factor = fine_adjust
        
        show_structure = st.checkbox("Show Structure", value=True, key="sfd_show_structure_2nd")
        
        if st.button("Plot Global Shear Force Diagram", key="btn_global_sfd_2nd"):
            try:
                # Create second order member response object
                member_response = get_second_order_member_response()
                
                # Generate plot
                member_response.PlotGlobalSFD(scale_factor=scale_factor, show_structure=show_structure)
                
                # Convert plot to Streamlit
                plt_to_streamlit()
            except Exception as e:
                st.error(f"Error plotting second order global shear force diagram: {str(e)}")

# Tab 5: Deflection
with tab5:
    st.header("Second Order Deflection Analysis")
    
    deflection_tab1, deflection_tab2 = st.tabs(["Individual Member Deflection", "Global Structure Deflection"])
    
    with deflection_tab1:
        member_ids = list(st.session_state.members.keys())
        selected_member_id = st.selectbox("Select Member", member_ids, key="deflection_member_2nd")
        selected_member = st.session_state.members[selected_member_id]
        
        if st.button("Plot Member Deflection", key="btn_deflection_2nd"):
            try:
                # Create second order member response object
                member_response = get_second_order_member_response()
                
                # Generate plot
                fig = plt.figure(figsize=(10, 6))
                member_response.PlotMemberDeflection(selected_member.Beam_Number)
                
                # Convert plot to Streamlit
                plt_to_streamlit()
                
                # Also get the numeric data if available in session state
                try:
                    deflections = member_response.MemberDeflection(selected_member.Beam_Number)
                    positions = member_response.DeflectionPosition
                    
                    # Store in session state
                    st.session_state.second_order_analysis_results["deflection"] = {
                        "deflections": deflections,
                        "positions": positions
                    }
                    
                    # Display numerical data in a table if desired
                    if st.checkbox("Show Numerical Data", key="show_deflection_data_2nd"):
                        data = pd.DataFrame({
                            "Position (m)": positions,
                            "Deflection (m)": deflections
                        })
                        st.dataframe(data, use_container_width=True)
                except Exception:
                    st.info("Numerical data for deflection not available")
            except Exception as e:
                st.error(f"Error plotting second order member deflection: {str(e)}")
    
    with deflection_tab2:
        # Dynamic scale factor control with slider and fine adjustment
        col1, col2 = st.columns([3, 1])
        with col1:
            scale_factor = st.slider("Scale Factor", min_value=0.1, max_value=100.0, value=10.0, step=0.1, key="deflection_scale_2nd")
        with col2:
            fine_adjust = st.number_input("Fine Adjust", min_value=0.1, max_value=500.0, value=scale_factor, step=0.1, key="deflection_fine_adjust_2nd")
            if fine_adjust != scale_factor:
                scale_factor = fine_adjust
        
        show_structure = st.checkbox("Show Structure", value=True, key="deflection_show_structure_2nd")
        
        if st.button("Plot Global Deflection", key="btn_global_deflection_2nd"):
            try:
                # Create second order member response object
                member_response = get_second_order_member_response()
                
                # Generate plot
                member_response.PlotGlobalDeflection(scale_factor=scale_factor, show_structure=show_structure)
                
                # Convert plot to Streamlit
                plt_to_streamlit()
            except Exception as e:
                st.error(f"Error plotting second order global deflection: {str(e)}")

# Tab 6: Buckling Analysis
with tab6:
    st.header("Buckling Analysis")
    
    buckling_tab1, buckling_tab2 = st.tabs(["Buckling Eigenload", "Eigen Mode Visualization"])
    
    with buckling_tab1:
        solver_options = ["Default", "eigs", "eigsh"]
        solver = st.selectbox("Solver Method", solver_options, 
                             index=0, key="buckling_solver",
                             help="Choose the solver method for eigenvalue analysis")
        
        solver_param = False if solver == "Default" else solver
        
        if st.button("Calculate Buckling Eigenload", key="btn_buckling_eigenload"):
            try:
                # Create second order global response object
                global_response = get_second_order_global_response()
                
                # Calculate buckling eigenload
                critical_load, eigenvalues, eigenmodes = global_response.BucklingEigenLoad(Solver=solver_param)
                
                # Store in session state
                st.session_state.second_order_analysis_results["buckling"] = {
                    "critical_load": critical_load,
                    "eigenvalues": eigenvalues,
                    "eigenmodes": eigenmodes
                }
                
                # Display results
                st.success(f"Buckling analysis completed")
                
                # Create DataFrame for display
                st.subheader("Critical Load")
                st.write(f"**Critical Buckling Load Factor: {critical_load:.4f}**")
                
                st.subheader("Eigenvalues")
                eigenvalue_data = []
                for i, eigenvalue in enumerate(eigenvalues[:10]):  # Show first 10 eigenvalues
                    eigenvalue_data.append({
                        "Mode": i+1,
                        "Eigenvalue": eigenvalue
                    })
                
                df = pd.DataFrame(eigenvalue_data)
                st.dataframe(df, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error calculating buckling eigenload: {str(e)}")
    
    with buckling_tab2:
        eigen_mode = st.slider("Eigen Mode Number", 1, 10, 1, 1, key="eigen_mode_number")
        
        # Dynamic scale factor control with slider and fine adjustment
        col1, col2 = st.columns([3, 1])
        with col1:
            scale_factor = st.slider("Scale Factor", min_value=0.1, max_value=100.0, value=10.0, step=0.1, key="eigen_mode_scale")
        with col2:
            fine_adjust = st.number_input("Fine Adjust", min_value=0.01, max_value=1000.0, value=scale_factor, step=0.01, key="eigen_mode_fine_adjust")
            if fine_adjust != scale_factor:
                scale_factor = fine_adjust
        
        show_structure = st.checkbox("Show Structure", value=True, key="eigen_mode_show_structure")
        
        solver_options = ["Default", "eigs", "eigsh"]
        solver = st.selectbox("Solver Method", solver_options, 
                             index=0, key="eigen_mode_solver",
                             help="Choose the solver method for eigenvalue analysis")
        
        solver_param = False if solver == "Default" else solver
        
        if st.button("Plot Eigen Mode", key="btn_plot_eigenmode"):
            try:
                # Create second order global response object
                global_response = get_second_order_global_response()
                
                # Generate plot
                global_response.PlotEigenMode(EigenModeNo=eigen_mode, 
                                             scale_factor=scale_factor, 
                                             Solver=solver_param,
                                             show_structure=show_structure)
                
                # Convert plot to Streamlit
                plt_to_streamlit()
                
                # Get individual member eigenmode if desired
                if st.checkbox("Show Individual Member Eigenmode", key="show_member_eigenmode"):
                    member_ids = list(st.session_state.members.keys())
                    selected_member_id = st.selectbox("Select Member", member_ids, key="eigenmode_member")
                    selected_member = st.session_state.members[selected_member_id]
                    
                    # Calculate eigenmode for selected member
                    eigenmode = global_response.MemberEigenMode(selected_member.Beam_Number, 
                                                              scale_factor=scale_factor,
                                                              EigenModeNo=eigen_mode)
                    positions = global_response.DeflectionPosition
                    
                    # Display numerical data
                    data = pd.DataFrame({
                        "Position (m)": positions,
                        "Eigenmode": eigenmode
                    })
                    st.dataframe(data, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error plotting eigen mode: {str(e)}")

# Structure visualization at the bottom
st.header("Structural Visualization")

if st.session_state.nodes and st.session_state.members:
    # Create 2D plot using Plotly
    fig = go.Figure()
    
    # Add nodes
    node_x = []
    node_y = []
    node_texts = []
    
    for node_id, node in st.session_state.nodes.items():
        node_x.append(node.xcoordinate)
        node_y.append(node.ycoordinate)
        node_texts.append(node_id)
    
    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=10,
            color='blue',
            symbol='circle'
        ),
        text=node_texts,
        textposition="top center",
        name='Nodes'
    ))
    
    # Add members
    for member_id, member in st.session_state.members.items():
        start_node = member.Start_Node
        end_node = member.End_Node
        
        fig.add_trace(go.Scatter(
            x=[start_node.xcoordinate, end_node.xcoordinate],
            y=[start_node.ycoordinate, end_node.ycoordinate],
            mode='lines+text',
            line=dict(
                color='gray',
                width=3
            ),
            text=[None, member_id],
            textposition="middle center",
            name=f'Member {member_id}'
        ))
    
    # Add loads
    for i, load in enumerate(st.session_state.loads):
        member = next(member for member in st.session_state.members.values() 
                   if member.Beam_Number == load.MemberNo + 1)
        start_node = member.Start_Node
        end_node = member.End_Node
        
        # Calculate direction vector of the member
        dx = end_node.xcoordinate - start_node.xcoordinate
        dy = end_node.ycoordinate - start_node.ycoordinate
        length = member.length()
        
        # Unit normal vector (perpendicular to member)
        nx = -dy / length
        ny = dx / length
        
        if load.type == "PL":
            # Point load - calculate position along member
            t = load.Distance1 / length
            x_pos = start_node.xcoordinate + t * dx
            y_pos = start_node.ycoordinate + t * dy
            
            # Draw arrow for point load
            arrow_length = 0.5  # Adjust based on your scale
            arrow_x = [x_pos, x_pos + nx * arrow_length]
            arrow_y = [y_pos, y_pos + ny * arrow_length]
            
            fig.add_trace(go.Scatter(
                x=arrow_x,
                y=arrow_y,
                mode='lines+markers',
                marker=dict(
                    size=8,
                    color='red',
                    symbol='arrow-down'
                ),
                line=dict(
                    color='red',
                    width=2
                ),
                name=f'Point Load {i+1}: {load.Magnitude} N'
            ))
            
        elif load.type == "UDL":
            # Calculate start and end positions of UDL
            t1 = load.Distance1 / length
            t2 = load.Distance2 / length
            
            x_start = start_node.xcoordinate + t1 * dx
            y_start = start_node.ycoordinate + t1 * dy
            x_end = start_node.xcoordinate + t2 * dx
            y_end = start_node.ycoordinate + t2 * dy
            
            # Create multiple arrows for UDL
            num_arrows = 5
            arrow_length = 0.3  # Adjust based on your scale
            
            for j in range(num_arrows):
                t = t1 + j * (t2 - t1) / (num_arrows - 1)
                x_pos = start_node.xcoordinate + t * dx
                y_pos = start_node.ycoordinate + t * dy
                
                arrow_x = [x_pos, x_pos + nx * arrow_length]
                arrow_y = [y_pos, y_pos + ny * arrow_length]
                
                fig.add_trace(go.Scatter(
                    x=arrow_x,
                    y=arrow_y,
                    mode='lines',
                    line=dict(
                        color='purple',
                        width=2
                    ),
                    showlegend=j==0,
                    name=f'UDL {i+1}: {load.Magnitude} N/m'
                ))
            
            # Add a line to indicate the UDL span
            fig.add_trace(go.Scatter(
                x=[x_start + nx * arrow_length, x_end + nx * arrow_length],
                y=[y_start + ny * arrow_length, y_end + ny * arrow_length],
                mode='lines',
                line=dict(
                    color='purple',
                    width=2
                ),
                showlegend=False
            ))
    
    # Add support visualizations
    for node_id, node in st.session_state.nodes.items():
        support = node.support_condition
        
        if support == "Fixed Support":
            # Draw a fixed support symbol (rectangle)
            fig.add_trace(go.Scatter(
                x=[node.xcoordinate],
                y=[node.ycoordinate],
                mode='markers',
                marker=dict(
                    size=12,
                    color='green',
                    symbol='square'
                ),
                name=f'Fixed Support at {node_id}'
            ))
        elif support == "Hinged Support" or support == "Hinged Joint Support":
            # Draw a hinged support symbol (triangle)
            fig.add_trace(go.Scatter(
                x=[node.xcoordinate],
                y=[node.ycoordinate],
                mode='markers',
                marker=dict(
                    size=12,
                    color='orange',
                    symbol='triangle-down'
                ),
                name=f'Hinged Support at {node_id}'
            ))
        elif "Roller" in support:
            # Draw a roller support symbol (circle)
            fig.add_trace(go.Scatter(
                x=[node.xcoordinate],
                y=[node.ycoordinate],
                mode='markers',
                marker=dict(
                    size=12,
                    color='red',
                    symbol='circle'
                ),
                name=f'Roller at {node_id}'
            ))
    
    # Update layout for better visualization
    fig.update_layout(
        xaxis=dict(
            title='X (m)',
            scaleanchor="y",
            scaleratio=1
        ),
        yaxis=dict(
            title='Y (m)'
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        height=400,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Add nodes and members to see the visualization.") 