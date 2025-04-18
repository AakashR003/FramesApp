import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append('..')
from StructuralElements import Node

# Initialize session state for nodes if not exists
if 'nodes' not in st.session_state:
    st.session_state.nodes = {}
    
# Initialize node counter for auto-numbering
if 'node_counter' not in st.session_state:
    st.session_state.node_counter = 1

# Initialize state for currently editing node
if 'editing_node_id' not in st.session_state:
    st.session_state.editing_node_id = None

# Function to save nodes to file
def save_nodes():
    if not os.path.exists('data'):
        os.makedirs('data')
    # Save only serializable data
    nodes_data = {}
    for node_id, node_obj in st.session_state.nodes.items():
        nodes_data[node_id] = {
            "node_number": node_obj.node_number,
            "xcoordinate": node_obj.xcoordinate,
            "ycoordinate": node_obj.ycoordinate,
            "support_condition": node_obj.support_condition,
            "dof_x": node_obj.dof_x,
            "dof_y": node_obj.dof_y,
            "dof_tita": node_obj.dof_tita
        }
    with open('data/nodes.json', 'w') as f:
        json.dump(nodes_data, f)
    st.success("Nodes saved successfully!")

# Function to load nodes from file
def load_nodes():
    if os.path.exists('data/nodes.json'):
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
        st.success("Nodes loaded successfully!")
    else:
        st.error("No saved nodes found!")

# Function to set the editing node ID
def set_editing_node(node_id):
    st.session_state.editing_node_id = node_id

# Main layout
st.title("Node Input")

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Add/Edit Node")
    
    # Check if we're editing a node
    editing_existing = False
    current_node = None
    
    if st.session_state.editing_node_id and st.session_state.editing_node_id in st.session_state.nodes:
        editing_existing = True
        current_node = st.session_state.nodes[st.session_state.editing_node_id]
        node_id_default = st.session_state.editing_node_id
        st.info(f"Editing Node: {node_id_default}")
    else:
        node_id_default = f"N{st.session_state.node_counter}"
    
    # Node ID - Non-editable when editing, number input when creating new
    if editing_existing:
        st.text_input("Node ID", value=node_id_default, disabled=True)
        node_id = node_id_default
    else:
        node_prefix = "N"
        node_number = st.number_input("Node Number", value=st.session_state.node_counter, min_value=1, step=1, format="%d")
        node_id = f"{node_prefix}{node_number}"
        st.write(f"Node ID: {node_id}")
    
    # Node coordinates
    st.subheader("Coordinates")
    x = st.number_input("X (m)", value=current_node.xcoordinate if current_node else 0.0, step=0.1)
    y = st.number_input("Y (m)", value=current_node.ycoordinate if current_node else 0.0, step=0.1)
    z = st.number_input("Z (m)", value=0.0, step=0.1, disabled=True, help="Currently only supporting 2D structures")
    
    # Node support conditions - taken directly from the Node class
    st.subheader("Support Condition")
    support_options = ["Hinged Support", "Fixed Support", "Rigid Joint", "Roller in X-plane", 
                       "Roller in Y-plane", "Hinge Joint", "Glided Support", "Hinged Joint Support", 
                       "Roller in X-plane-Hinge"]
    
    default_index = 0
    if current_node:
        if current_node.support_condition in support_options:
            default_index = support_options.index(current_node.support_condition)
    
    support_condition = st.selectbox(
        "Support Type", 
        support_options,
        index=default_index
    )
    
    # Button to add node
    if st.button("Add/Update Node"):
        # Create node data using the Node class
        node_number = current_node.node_number if current_node else st.session_state.node_counter
        node = Node(node_number, x, y, support_condition)
        
        # Add to session state
        st.session_state.nodes[node_id] = node
        
        # Increment counter for next node if this is a new node and not an edit
        if not editing_existing and node_id == f"N{st.session_state.node_counter}":
            st.session_state.node_counter += 1
            
        st.success(f"Node {node_id} {'updated' if editing_existing else 'added'}!")
        
        # Reset editing state
        st.session_state.editing_node_id = None
        st.rerun()
    
    # Button to delete node
    if st.button("Delete Node"):
        if node_id in st.session_state.nodes:
            del st.session_state.nodes[node_id]
            st.success(f"Node {node_id} deleted!")
            
            # Reset editing state
            if st.session_state.editing_node_id == node_id:
                st.session_state.editing_node_id = None
                st.rerun()
        else:
            st.error(f"Node {node_id} not found!")
    
    # Button to cancel editing
    if editing_existing and st.button("Cancel Editing"):
        st.session_state.editing_node_id = None
        st.rerun()
    
    # Save and load buttons
    col_save, col_load = st.columns(2)
    
    with col_save:
        if st.button("Save Nodes"):
            save_nodes()
    
    with col_load:
        if st.button("Load Nodes"):
            load_nodes()

with col2:
    st.subheader("Nodes Table")
    
    if st.session_state.nodes:
        # Convert nodes to DataFrame for display
        node_data = []
        for node_id, node in st.session_state.nodes.items():
            node_data.append({
                "Node ID": node_id,
                "Node Number": node.node_number,
                "X (m)": node.xcoordinate,
                "Y (m)": node.ycoordinate,
                "Support Condition": node.support_condition,
                "DOFs": f"({node.dof_x}, {node.dof_y}, {node.dof_tita})"
            })
        
        df = pd.DataFrame(node_data)
        
        # Display nodes table
        st.dataframe(df, use_container_width=True)
        
        # Add selectbox for node editing instead of interactive table
        st.subheader("Edit Node")
        node_to_edit = st.selectbox(
            "Select a node to edit",
            options=list(st.session_state.nodes.keys()),
            help="Choose a node to populate the edit form"
        )
        
        if st.button("Load Node Data for Editing"):
            # Set the currently editing node
            st.session_state.editing_node_id = node_to_edit
            
            # Clear any session state values that might interfere with loading properties
            for key in list(st.session_state.keys()):
                if key.startswith('_'):
                    del st.session_state[key]
                    
            st.rerun()
    else:
        st.info("No nodes have been created yet. Add nodes using the form on the left.")

# Visualization
st.subheader("Structural Visualization")

if st.session_state.nodes:
    # Create 2D plot using Plotly
    fig = go.Figure()
    
    # Extract node coordinates
    node_x = []
    node_y = []
    node_texts = []
    
    for node_id, node in st.session_state.nodes.items():
        node_x.append(node.xcoordinate)
        node_y.append(node.ycoordinate)
        node_texts.append(node_id)
    
    # Add nodes
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
    
    # Add coordinate system origin
    fig.add_trace(go.Scatter(
        x=[0],
        y=[0],
        mode='markers',
        marker=dict(
            size=8,
            color='black',
            symbol='circle'
        ),
        name='Origin'
    ))
    
    # Add support visualization
    for node_id, node in st.session_state.nodes.items():
        coords = [node.xcoordinate, node.ycoordinate]
        support = node.support_condition
        
        # Different marker styles for different support types
        if support == "Fixed Support":
            fig.add_trace(go.Scatter(
                x=[coords[0]],
                y=[coords[1]],
                mode='markers',
                marker=dict(
                    size=15,
                    color='red',
                    symbol='square',
                    opacity=0.7
                ),
                name=f'Fixed Support at {node_id}'
            ))
        elif support == "Hinged Support" or support == "Hinged Joint Support":
            fig.add_trace(go.Scatter(
                x=[coords[0]],
                y=[coords[1]],
                mode='markers',
                marker=dict(
                    size=15,
                    color='green',
                    symbol='diamond',
                    opacity=0.7
                ),
                name=f'Hinged Support at {node_id}'
            ))
        elif "Roller" in support:
            fig.add_trace(go.Scatter(
                x=[coords[0]],
                y=[coords[1]],
                mode='markers',
                marker=dict(
                    size=15,
                    color='orange',
                    symbol='triangle-up',
                    opacity=0.7
                ),
                name=f'Roller at {node_id}'
            ))
        elif support == "Glided Support":
            fig.add_trace(go.Scatter(
                x=[coords[0]],
                y=[coords[1]],
                mode='markers',
                marker=dict(
                    size=15,
                    color='purple',
                    symbol='cross',
                    opacity=0.7
                ),
                name=f'Glided Support at {node_id}'
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
        height=500,
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
    st.info("Add nodes to see the visualization.") 