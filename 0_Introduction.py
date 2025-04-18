import streamlit as st
import os
import sys
import json
import base64
import tempfile
from datetime import datetime

# Add the app's directory to the path
sys.path.append('.')

# Initialize session state
if 'nodes' not in st.session_state:
    st.session_state.nodes = {}

if 'members' not in st.session_state:
    st.session_state.members = {}

if 'loads' not in st.session_state:
    st.session_state.loads = []

# Main page
st.set_page_config(
    page_title="Structural Analysis App", 
    page_icon="🏗️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add save/load functionality
with st.sidebar:
    # Project Management section
    st.subheader("Project Management")
    
    col1, col2 = st.columns(2)
    
    # Save structure to external folder
    with col1:
        if st.button("Save Structure", key="save_structure"):
            if not st.session_state.nodes or not st.session_state.members:
                st.sidebar.error("No structure to save. Please create nodes and members first.")
            else:
                # Prepare structure data for export
                structure_data = {
                    "nodes": {},
                    "members": {},
                    "loads": []
                }
                
                # Convert nodes to serializable format
                for node_id, node in st.session_state.nodes.items():
                    structure_data["nodes"][node_id] = {
                        "node_number": node.node_number,
                        "xcoordinate": node.xcoordinate,
                        "ycoordinate": node.ycoordinate,
                        "support_condition": node.support_condition
                    }
                
                # Convert members to serializable format
                for member_id, member in st.session_state.members.items():
                    structure_data["members"][member_id] = {
                        "beam_number": member.Beam_Number,
                        "start_node_id": next(key for key, value in st.session_state.nodes.items() 
                                         if value.node_number == member.Start_Node.node_number),
                        "end_node_id": next(key for key, value in st.session_state.nodes.items() 
                                       if value.node_number == member.End_Node.node_number),
                        "area": member.area,
                        "youngs_modulus": member.youngs_modulus,
                        "moment_of_inertia": member.moment_of_inertia,
                        "density": member.Density
                    }
                
                # Convert loads to serializable format
                for load in st.session_state.loads:
                    load_data = {
                        "type": load.type,
                        "magnitude": load.Magnitude,
                        "distance1": load.Distance1,
                        "distance2": load.Distance2 if hasattr(load, 'Distance2') else None,
                        "assigned_to": load.AssignedTo
                    }
                    structure_data["loads"].append(load_data)
                
                # Convert to formatted text
                formatted_text = json.dumps(structure_data, indent=2)
                
                # Create filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"structure_{timestamp}.txt"
                
                # Create download button
                download_button = f"""
                    <a href="data:file/txt;base64,{base64.b64encode(formatted_text.encode()).decode()}" 
                    download="{filename}" 
                    style="display: inline-block; padding: 0.5em 1em; color: white; background-color: #4CAF50; 
                    text-decoration: none; border-radius: 3px; border: none; 
                    font-weight: bold; text-align: center; cursor: pointer;">
                    Save As...</a>
                """
                st.sidebar.markdown(download_button, unsafe_allow_html=True)
                st.sidebar.markdown("**Note:** When the browser download dialog appears, please select where to save the file on your PC.")
                
                st.sidebar.success("Structure prepared for download.")
    
    # Load structure from external folder
    with col2:
        uploaded_file = st.file_uploader("Load Structure", type=["txt"], key="load_structure")
        if uploaded_file is not None:
            try:
                structure_data = json.loads(uploaded_file.read().decode('utf-8'))
                
                # Clear existing data
                st.session_state.nodes = {}
                st.session_state.members = {}
                st.session_state.loads = []
                
                # Create a message to hold import results
                import_message = []
                
                # Import nodes
                from StructuralElements import Node
                if "nodes" in structure_data:
                    for node_id, node_data in structure_data["nodes"].items():
                        node = Node(
                            node_data["node_number"],
                            node_data["xcoordinate"],
                            node_data["ycoordinate"],
                            node_data["support_condition"]
                        )
                        st.session_state.nodes[node_id] = node
                    import_message.append(f"✅ Imported {len(structure_data['nodes'])} nodes")
                
                # Import members
                from StructuralElements import Member
                if "members" in structure_data and len(st.session_state.nodes) > 0:
                    for member_id, member_data in structure_data["members"].items():
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
                    import_message.append(f"✅ Imported {len(structure_data['members'])} members")
                
                # Import loads
                from Loads import NeumanBC
                if "loads" in structure_data and len(st.session_state.members) > 0:
                    members_list = list(st.session_state.members.values())
                    
                    for load_data in structure_data["loads"]:
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
                    import_message.append(f"✅ Imported {len(structure_data['loads'])} loads")
                
                # Save to data files
                os.makedirs('data', exist_ok=True)
                
                # Save nodes to file
                with open('data/nodes.json', 'w') as f:
                    json.dump({node_id: {
                        "node_number": node.node_number,
                        "xcoordinate": node.xcoordinate,
                        "ycoordinate": node.ycoordinate,
                        "support_condition": node.support_condition
                    } for node_id, node in st.session_state.nodes.items()}, f)
                
                # Save members to file
                with open('data/members.json', 'w') as f:
                    json.dump({member_id: {
                        "beam_number": member.Beam_Number,
                        "start_node_id": next(key for key, value in st.session_state.nodes.items() 
                                         if value.node_number == member.Start_Node.node_number),
                        "end_node_id": next(key for key, value in st.session_state.nodes.items() 
                                       if value.node_number == member.End_Node.node_number),
                        "area": member.area,
                        "youngs_modulus": member.youngs_modulus,
                        "moment_of_inertia": member.moment_of_inertia,
                        "density": member.Density
                    } for member_id, member in st.session_state.members.items()}, f)
                
                # Save loads to file
                with open('data/loads.json', 'w') as f:
                    json.dump([{
                        "type": load.type,
                        "magnitude": load.Magnitude,
                        "distance1": load.Distance1,
                        "distance2": load.Distance2 if hasattr(load, 'Distance2') else None,
                        "assigned_to": load.AssignedTo
                    } for load in st.session_state.loads], f)
                
                # Display success message
                st.sidebar.success("Structure imported successfully!\n" + "\n".join(import_message))
                
                # Add a restart suggestion
                st.sidebar.info("Please navigate to any page to see the imported structure.")
                
            except Exception as e:
                st.sidebar.error(f"Error importing structure: {str(e)}")

# Main content
st.title("Structural Analysis Application")
st.markdown("""
Welcome to the Structural Analysis Application! This tool helps you analyze and visualize structural frames and trusses.

### Getting Started:
1. Use the sidebar to navigate between pages
2. Start by creating nodes in the **Node Input** page
3. Create members connecting these nodes in the **Member Input** page
4. Add loads in the **Load Input** page
5. Perform analysis in the **First Order Analysis** or **Second Order Analysis** pages
6. Compare results in the **Comparison** page
7. Perform dynamic analysis in the **Dynamic Analysis** page

### Key Features:
- First and second order structural analysis
- Dynamic modal analysis
- Buckling analysis
- Automatic visualization of results
- Save and load structures
""")

# Display app version and creator info at the bottom
st.markdown("---")
st.markdown("#### Version 1.1.0")
st.markdown("Created for structural analysis education and research.")

# Hide streamlit default menu and footer
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Create directory for data if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data') 