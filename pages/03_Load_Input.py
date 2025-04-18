import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append('..')
from Loads import NeumanBC
from StructuralElements import Node, Member

# Initialize session state for loads if not exists
if 'loads' not in st.session_state:
    st.session_state.loads = []

# Initialize load counter for auto-numbering
if 'load_counter' not in st.session_state:
    st.session_state.load_counter = 1

# Initialize state for currently editing load
if 'editing_load_index' not in st.session_state:
    st.session_state.editing_load_index = None

# Ensure nodes and members are initialized
if 'nodes' not in st.session_state:
    st.session_state.nodes = {}

if 'members' not in st.session_state:
    st.session_state.members = {}

# Load nodes if available but not in session
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

# Load members if available but not in session
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

# Function to save loads to file
def save_loads():
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Convert load objects to serializable format
    loads_data = []
    for i, load in enumerate(st.session_state.loads):
        # Get member ID for serialization
        member_id = next(m_id for m_id, member in st.session_state.members.items() 
                     if member.Beam_Number == load.MemberNo + 1)
        
        load_data = {
            "load_id": f"L{i+1}",
            "type": load.type,
            "magnitude": load.Magnitude,
            "distance1": load.Distance1,
            "distance2": load.Distance2 if hasattr(load, 'Distance2') and load.Distance2 is not None else None,
            "assigned_to": load.AssignedTo,
            "member_id": member_id
        }
        loads_data.append(load_data)
    
    with open('data/loads.json', 'w') as f:
        json.dump(loads_data, f)
    st.success("Loads saved successfully!")

# Function to load loads from file
def load_loads():
    if os.path.exists('data/loads.json'):
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
        
        st.success("Loads loaded successfully!")
    else:
        st.error("No saved loads found!")

# Main layout
st.title("Load Input")

# Check if members exist
if not st.session_state.members:
    st.warning("No members found. Please create members in the Member Input page first.")
    st.stop()

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Add/Edit Load")
    
    # Check if we're editing a load
    editing_existing = False
    current_load = None
    
    if st.session_state.editing_load_index is not None and 0 <= st.session_state.editing_load_index < len(st.session_state.loads):
        editing_existing = True
        current_load = st.session_state.loads[st.session_state.editing_load_index]
        load_id_display = f"L{st.session_state.editing_load_index + 1}"
        st.info(f"Editing Load: {load_id_display}")
        
        # Get member ID for the current load
        current_member_id = next(m_id for m_id, member in st.session_state.members.items() 
                             if member.Beam_Number == current_load.MemberNo + 1)
    else:
        load_id_display = f"L{st.session_state.load_counter}"
        current_member_id = None
    
    # Load ID display (auto-generated)
    st.write(f"Load ID: {load_id_display}")
    
    # Member selection
    member_ids = list(st.session_state.members.keys())
    member_id = st.selectbox(
        "Select Member", 
        member_ids,
        index=member_ids.index(current_member_id) if current_member_id in member_ids else 0
    )
    
    # Load type selection (PL or UDL from NeumanBC class)
    load_type_options = ["PL", "UDL"]
    default_type_index = 0
    if current_load and current_load.type in load_type_options:
        default_type_index = load_type_options.index(current_load.type)
    
    load_type = st.selectbox(
        "Load Type", 
        load_type_options, 
        index=default_type_index,
        help="PL = Point Load, UDL = Uniformly Distributed Load"
    )
    
    # Load magnitude
    magnitude = st.number_input(
        "Magnitude (N for PL, N/m for UDL)", 
        value=current_load.Magnitude if current_load else 1000.0
    )
    
    # Get member length for reference
    selected_member = st.session_state.members[member_id]
    member_length = selected_member.length()
    st.write(f"Member Length: {member_length:.4f} m")
    
    # Distance inputs based on load type
    distance1 = st.slider(
        "Distance 1 (m)", 
        0.0, member_length, 
        value=current_load.Distance1 if current_load else member_length/3, 
        step=0.01,
        help="Distance from start of member"
    )
    
    if load_type == "UDL":
        distance2 = st.slider(
            "Distance 2 (m)", 
            distance1, member_length, 
            value=current_load.Distance2 if current_load and hasattr(current_load, 'Distance2') else min(distance1 + member_length/3, member_length), 
            step=0.01,
            help="End point of UDL, must be > Distance 1"
        )
    else:
        distance2 = None
    
    # Button to add/update load
    if st.button("Add/Update Load"):
        # Create load using NeumanBC class
        members_list = list(st.session_state.members.values())
        assigned_to = f"Member {selected_member.Beam_Number}"
        
        kwargs = {
            "type": load_type,
            "Magnitude": magnitude,
            "Distance1": distance1,
            "AssignedTo": assigned_to,
            "Members": members_list
        }
        
        if load_type == "UDL" and distance2 is not None:
            kwargs["Distance2"] = distance2
        
        try:
            load = NeumanBC(**kwargs)
            
            if editing_existing:
                # Replace the existing load
                st.session_state.loads[st.session_state.editing_load_index] = load
                st.success(f"Load {load_id_display} updated!")
            else:
                # Add new load
                st.session_state.loads.append(load)
                st.session_state.load_counter += 1
                st.success(f"Load added successfully to {assigned_to}!")
            
            # Reset editing state
            st.session_state.editing_load_index = None
            st.rerun()
        except Exception as e:
            st.error(f"Error creating load: {str(e)}")
    
    # Button to delete load
    if st.button("Delete Load"):
        if editing_existing:
            # Remove the load being edited
            st.session_state.loads.pop(st.session_state.editing_load_index)
            st.success(f"Load {load_id_display} deleted!")
            
            # Reset editing state
            st.session_state.editing_load_index = None
            st.rerun()
        else:
            st.error("Select a load to delete first!")
    
    # Button to cancel editing
    if editing_existing and st.button("Cancel Editing"):
        st.session_state.editing_load_index = None
        st.rerun()
    
    # Button to clear all loads
    if st.button("Clear All Loads"):
        st.session_state.loads = []
        st.session_state.load_counter = 1
        st.session_state.editing_load_index = None
        st.success("All loads cleared!")
    
    # Save and load buttons
    col_save, col_load = st.columns(2)
    
    with col_save:
        if st.button("Save Loads"):
            save_loads()
    
    with col_load:
        if st.button("Load Loads"):
            load_loads()

with col2:
    st.subheader("Loads Table")
    
    if st.session_state.loads:
        # Convert loads to DataFrame for display
        load_data = []
        for i, load in enumerate(st.session_state.loads):
            # Find the member ID for display
            member_id = next(m_id for m_id, member in st.session_state.members.items() 
                         if member.Beam_Number == load.MemberNo + 1)
            
            data = {
                "Load ID": f"L{i+1}",
                "Type": "Point Load" if load.type == "PL" else "Uniform Load",
                "Member": member_id,
                "Magnitude": f"{load.Magnitude} {'N' if load.type == 'PL' else 'N/m'}",
                "Distance 1 (m)": f"{load.Distance1:.2f}"
            }
            
            if load.type == "UDL":
                data["Distance 2 (m)"] = f"{load.Distance2:.2f}"
            else:
                data["Distance 2 (m)"] = "N/A"
            
            load_data.append(data)
        
        df = pd.DataFrame(load_data)
        st.dataframe(df, use_container_width=True)
        
        # Add load selection for editing
        st.subheader("Edit Load")
        
        # Create a list of load IDs for selection
        load_ids = [f"L{i+1}" for i in range(len(st.session_state.loads))]
        
        load_to_edit = st.selectbox(
            "Select a load to edit",
            options=load_ids,
            help="Choose a load to populate the edit form"
        )
        
        if st.button("Load Data for Editing"):
            # Extract the index from the load ID (format: L{index+1})
            load_index = int(load_to_edit[1:]) - 1
            
            # Set the currently editing load
            st.session_state.editing_load_index = load_index
            st.rerun()
    else:
        st.info("No loads have been created yet. Add loads using the form on the left.")

# Visualization
st.subheader("Structure and Load Visualization")

if st.session_state.nodes and st.session_state.members:
    # Create 2D plot using Plotly
    fig = go.Figure()
    
    # Add nodes
    for node_id, node in st.session_state.nodes.items():
        fig.add_trace(go.Scatter(
            x=[node.xcoordinate],
            y=[node.ycoordinate],
            mode='markers+text',
            marker=dict(
                size=8,
                color='blue',
                symbol='circle'
            ),
            text=[node_id],
            textposition="top center",
            name=node_id
        ))
    
    # Add members as lines
    for member_id, member in st.session_state.members.items():
        start_node = member.Start_Node
        end_node = member.End_Node
        
        fig.add_trace(go.Scatter(
            x=[start_node.xcoordinate, end_node.xcoordinate],
            y=[start_node.ycoordinate, end_node.ycoordinate],
            mode='lines',
            line=dict(color='red', width=3),
            name=member_id
        ))
    
    # Add loads
    for i, load in enumerate(st.session_state.loads):
        # Find the member this load is applied to
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
    
    # Update layout for 2D visualization
    fig.update_layout(
        title="2D Structure and Load View",
        xaxis_title="X Coordinate (m)",
        yaxis_title="Y Coordinate (m)",
        showlegend=True,
        margin=dict(l=20, r=20, t=60, b=20),
        height=600,
    )
    
    # Make sure axes are equally scaled
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Make sure to create nodes and members before adding loads.") 