import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append('..')
from StructuralElements import Member

# Initialize session state for members if not exists
if 'members' not in st.session_state:
    st.session_state.members = {}

# Initialize member counter for auto-numbering
if 'member_counter' not in st.session_state:
    st.session_state.member_counter = 1

# Initialize state for currently editing member
if 'editing_member_id' not in st.session_state:
    st.session_state.editing_member_id = None

# Ensure nodes are initialized
if 'nodes' not in st.session_state:
    st.session_state.nodes = {}

# Load nodes if available but not in session
if len(st.session_state.nodes) == 0 and os.path.exists('data/nodes.json'):
    with open('data/nodes.json', 'r') as f:
        nodes_data = json.load(f)
        from StructuralElements import Node
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

# Function to save members to file
def save_members():
    if not os.path.exists('data'):
        os.makedirs('data')
    # Save only serializable data
    members_data = {}
    for member_id, member_obj in st.session_state.members.items():
        # Get node IDs for serialization
        start_node_id = next(node_id for node_id, node in st.session_state.nodes.items() 
                         if node.node_number == member_obj.Start_Node.node_number)
        end_node_id = next(node_id for node_id, node in st.session_state.nodes.items() 
                         if node.node_number == member_obj.End_Node.node_number)
        
        members_data[member_id] = {
            "beam_number": member_obj.Beam_Number,
            "start_node_id": start_node_id,
            "end_node_id": end_node_id,
            "area": member_obj.area,
            "youngs_modulus": member_obj.youngs_modulus,
            "moment_of_inertia": member_obj.moment_of_inertia,
            "density": member_obj.Density
        }
    with open('data/members.json', 'w') as f:
        json.dump(members_data, f)
    st.success("Members saved successfully!")

# Function to load members from file
def load_members():
    if os.path.exists('data/members.json'):
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
        st.success("Members loaded successfully!")
    else:
        st.error("No saved members found!")

# Main layout
st.title("Member Input")

# Check if nodes exist
if not st.session_state.nodes:
    st.warning("No nodes found. Please create nodes in the Node Input page first.")
    st.stop()

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Add/Edit Member")
    
    # Check if we're editing a member
    editing_existing = False
    current_member = None
    
    if st.session_state.editing_member_id and st.session_state.editing_member_id in st.session_state.members:
        editing_existing = True
        current_member = st.session_state.members[st.session_state.editing_member_id]
        member_id_default = st.session_state.editing_member_id
        st.info(f"Editing Member: {member_id_default}")
        
        # Get node IDs for the current member
        current_start_node_id = next(node_id for node_id, node in st.session_state.nodes.items() 
                                if node.node_number == current_member.Start_Node.node_number)
        current_end_node_id = next(node_id for node_id, node in st.session_state.nodes.items() 
                               if node.node_number == current_member.End_Node.node_number)
    else:
        member_id_default = f"M{st.session_state.member_counter}"
        current_start_node_id = None
        current_end_node_id = None
    
    # Member ID - Non-editable when editing, number input when creating new
    if editing_existing:
        st.text_input("Member ID", value=member_id_default, disabled=True)
        member_id = member_id_default
    else:
        member_prefix = "M"
        member_number = st.number_input("Member Number", value=st.session_state.member_counter, min_value=1, step=1, format="%d")
        member_id = f"{member_prefix}{member_number}"
        st.write(f"Member ID: {member_id}")
    
    # Node selection
    node_ids = list(st.session_state.nodes.keys())
    
    # Start and end nodes with current values if editing
    if editing_existing:
        # When editing, display the nodes without allowing changes
        st.text_input("Start Node", value=current_start_node_id, disabled=True)
        start_node_id = current_start_node_id
        
        st.text_input("End Node", value=current_end_node_id, disabled=True)
        end_node_id = current_end_node_id
    else:
        # When creating new, allow selection from dropdown
        start_node_id = st.selectbox(
            "Start Node", 
            node_ids,
            index=0,
            key="start_node"
        )
        
        end_node_id = st.selectbox(
            "End Node", 
            node_ids,
            index=min(1, len(node_ids)-1) if len(node_ids) > 1 else 0,
            key="end_node"
        )
    
    # Material properties with current values if editing
    st.subheader("Member Properties")
    
    # Convert values to float to avoid issues
    current_area = float(current_member.area) if current_member else 0.09
    current_youngs = float(current_member.youngs_modulus) if current_member else 200000000.0
    current_moi = float(current_member.moment_of_inertia) if current_member else 0.000675
    current_density = float(current_member.Density) if current_member else 7850.0
    
    area = st.number_input(
        "Cross-sectional Area (m²)", 
        value=current_area, 
        format="%.5f"
    )
    
    elastic_modulus = st.number_input(
        "Elastic Modulus (Pa)", 
        value=current_youngs, 
        format="%.1f"
    )
    
    moment_of_inertia = st.number_input(
        "Moment of Inertia (m⁴)", 
        value=current_moi, 
        format="%.6f"
    )
    
    density = st.number_input(
        "Density (kg/m³)", 
        value=current_density, 
        format="%.1f"
    )
    
    # Calculate length for display (informational only)
    if start_node_id in st.session_state.nodes and end_node_id in st.session_state.nodes:
        start_node = st.session_state.nodes[start_node_id]
        end_node = st.session_state.nodes[end_node_id]
        length = np.sqrt((end_node.xcoordinate - start_node.xcoordinate)**2 + 
                         (end_node.ycoordinate - start_node.ycoordinate)**2)
        st.write(f"Member Length: {length:.4f} m")
    
    # Button to add/update member
    if st.button("Add/Update Member"):
        if start_node_id == end_node_id:
            st.error("Start and end nodes cannot be the same!")
        else:
            # Get the actual node objects
            start_node = st.session_state.nodes[start_node_id]
            end_node = st.session_state.nodes[end_node_id]
            
            # Create member using the Member class
            beam_number = current_member.Beam_Number if current_member else st.session_state.member_counter
            member = Member(
                beam_number,
                start_node,
                end_node,
                area,
                elastic_modulus,
                moment_of_inertia,
                density
            )
            
            # Add to session state
            st.session_state.members[member_id] = member
            
            # Increment counter for next member if this is a new member
            if not editing_existing and member_id == f"M{st.session_state.member_counter}":
                st.session_state.member_counter += 1
                
            st.success(f"Member {member_id} {'updated' if editing_existing else 'added'}!")
            
            # Reset editing state
            st.session_state.editing_member_id = None
            st.rerun()
    
    # Button to delete member
    if st.button("Delete Member"):
        if member_id in st.session_state.members:
            del st.session_state.members[member_id]
            st.success(f"Member {member_id} deleted!")
            
            # Reset editing state if we were editing this member
            if st.session_state.editing_member_id == member_id:
                st.session_state.editing_member_id = None
                st.rerun()
        else:
            st.error(f"Member {member_id} not found!")
    
    # Button to cancel editing
    if editing_existing and st.button("Cancel Editing"):
        st.session_state.editing_member_id = None
        st.rerun()
    
    # Save and load buttons
    col_save, col_load = st.columns(2)
    
    with col_save:
        if st.button("Save Members"):
            save_members()
    
    with col_load:
        if st.button("Load Members"):
            load_members()

with col2:
    st.subheader("Members Table")
    
    if st.session_state.members:
        # Convert members to DataFrame for display
        member_data = []
        for member_id, member in st.session_state.members.items():
            # Get node IDs for display
            start_node_id = next(node_id for node_id, node in st.session_state.nodes.items() 
                             if node.node_number == member.Start_Node.node_number)
            end_node_id = next(node_id for node_id, node in st.session_state.nodes.items() 
                             if node.node_number == member.End_Node.node_number)
            
            member_data.append({
                "Member ID": member_id,
                "Beam Number": member.Beam_Number,
                "From Node": start_node_id,
                "To Node": end_node_id,
                "Length (m)": f"{member.length():.3f}",
                "Area (m²)": f"{member.area:.5f}",
                "E (Pa)": f"{member.youngs_modulus:.1f}",
                "I (m⁴)": f"{member.moment_of_inertia:.6f}"
            })
        
        df = pd.DataFrame(member_data)
        st.dataframe(df, use_container_width=True)
        
        # Add member selection for editing
        st.subheader("Edit Member")
        member_to_edit = st.selectbox(
            "Select a member to edit",
            options=list(st.session_state.members.keys()),
            help="Choose a member to populate the edit form"
        )
        
        if st.button("Load Member Data for Editing"):
            # Set the currently editing member
            st.session_state.editing_member_id = member_to_edit
            
            # Clear any session state values that might interfere with loading properties
            for key in list(st.session_state.keys()):
                if key in ["start_node", "end_node"] or key.startswith('_'):
                    del st.session_state[key]
                    
            # Force a rerun to reload the page with the member data
            st.rerun()
    else:
        st.info("No members have been created yet. Add members using the form on the left.")

# Visualization
st.subheader("Structural Visualization")

if st.session_state.nodes:
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
    
    # Update layout for 2D visualization
    fig.update_layout(
        title="2D Structure View",
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
    st.info("No nodes have been created yet. Create nodes in the Node Input page first.") 