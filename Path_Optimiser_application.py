import tkinter as tk  # Import the tkinter library for creating GUI applications
from tkinter import ttk  # Import the ttk module for themed Tkinter widgets
import networkx as nx  # Import the NetworkX library for creating and manipulating graphs
import matplotlib.pyplot as plt  # Import the matplotlib library for plotting graphs
import json  # Import the JSON module for handling JSON data
import pyodbc  # Import the pyodbc module for connecting to SQL Server databases


# Function to store data in the SQL Server database and update JSON file
def store_data_in_database_and_update_json():
    # Read JSON data from file
    with open('new_update_data.json', 'r') as json_file:  # Open the JSON file in read mode
        existing_data = json.load(json_file)  # Load JSON data into a Python dictionary

    # Connect to SQL Server database using Windows authentication
    conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=LAPTOP-Q542RENJ; DATABASE=Atria_stdDb; Trusted_Connection=yes;')
    cursor = conn.cursor()  # Create a cursor object to execute SQL queries

    # Clear existing data in the table
    cursor.execute("DELETE FROM GraphData")  # Execute SQL query to delete all rows from GraphData table
    conn.commit()  # Commit the transaction to apply changes

    # Insert data from JSON file into the table
    for node, connections in existing_data.items():  # Iterate over nodes and their connections in the JSON data
        for neighbor, neighbor_data in connections.items():  # Iterate over neighbors and their data
            distance = neighbor_data['distance']  # Get distance from current node to neighbor
            direction = neighbor_data['direction']  # Get direction from current node to neighbor
            try:
                cursor.execute("INSERT INTO GraphData (Node, Neighbor, Distance, Direction) VALUES (?, ?, ?, ?)", (node, neighbor, distance, direction))
                # Execute SQL query to insert data into GraphData table
                conn.commit()  # Commit the transaction to apply changes
            except pyodbc.IntegrityError:
                print("Duplicate entry detected. Skipping insertion.")  # Print message if duplicate entry is detected

    cursor.close()  # Close the cursor
    conn.close()  # Close the database connection

    return existing_data  # Return the updated data

# Function to update the JSON file when a new row is added to the SQL Server database
def update_json_when_new_row_added(node, neighbor, distance, direction):
    with open('new_update_data.json', 'r') as json_file:  # Open the JSON file in read mode
        existing_data = json.load(json_file)  # Load JSON data into a Python dictionary

    if node not in existing_data:  # Check if node does not exist in existing data
        existing_data[node] = {}  # Create an empty dictionary for the node
    existing_data[node][neighbor] = {'distance': distance, 'direction': direction}  # Add neighbor data to node

    with open('new_update_data.json', 'w') as json_file:  # Open the JSON file in write mode
        json.dump(existing_data, json_file)  # Write updated data to JSON file

    return existing_data  # Return the updated data

# Function to find the shortest path and total distance
def find_shortest_path(start, end, graph):
    if end == 'H':  # Check if the end node is 'H'
        return "There is no possible way to go from {} to {}".format(start, end), None
        # Return message if there is no path to 'H'
    visited = set()  # Initialize a set to keep track of visited nodes
    queue = [[start]]  # Initialize a queue for BFS traversal
    while queue:
        path = queue.pop(0)  # Get the first path from the queue
        node = path[-1]  # Get the last node of the path
        if node == end:  # Check if the current node is the end node
            total_distance = sum(graph[path[i]][path[i+1]]['distance'] for i in range(len(path)-1))
            # Calculate the total distance of the path
            return path, total_distance  # Return the shortest path and its total distance
        elif node not in visited:  # Check if the current node is not visited
            for neighbor in graph[node]:  # Iterate over neighbors of the current node
                new_path = list(path)  # Create a new path by appending the neighbor
                new_path.append(neighbor)
                queue.append(new_path)  # Add the new path to the queue
            visited.add(node)  # Mark the current node as visited
    return "There is no possible way to go from {} to {}".format(start, end), None
    # Return message if no path is found to the end node

# Function to draw the graph
def draw_graph(graph, shortest_path=None):
    G = nx.DiGraph()  # Create a directed graph
    for node in graph:  # Add nodes to the graph
        G.add_node(node)
    for node, neighbors in graph.items():  # Add edges to the graph
        for neighbor, data in neighbors.items():
            if not isinstance(data, int):  # Check if the data is not an integer (indicating bidirectional edge)
                distance = data['distance']  # Get the distance between nodes
                bidirectional = data['direction']  # Check if the edge is bidirectional
                G.add_edge(node, neighbor, weight=distance, bidirectional=bidirectional)
                # Add the edge with weight and bidirectional attribute
            else:
                G.add_edge(node, neighbor, weight=data)  # Add the edge with weight
    plt.figure(figsize=(8, 6))  # Create a plot with specified size
    pos = nx.spring_layout(G, seed=42)  # Compute node positions using spring layout algorithm

    # # Manually adjust the position of specific nodes
    pos['A'] = (-0.885, 0.357)     # Adjusting the position of node A
    pos['B'] = (-0.429, 0.023)     # Adjusting the position of node B
    pos['G'] = (0.719, -0.323)     # Adjusting the position of node G
    pos['D'] = (-0.637, -0.511)    # Adjusting the position of node D
    pos['F'] = (-0.011, -0.522)    # Adjusting the position of node F
    pos['I'] = (0.156, -0.106)     # Adjusting the position of node I

    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=12, font_weight='bold', arrowsize=20)
    # Draw the graph with labels, node size, color, font size, font weight, and arrow size
    edge_labels = nx.get_edge_attributes(G, 'weight')  # Get edge labels (distances)
    if shortest_path:  # Check if shortest path is provided
        shortest_path_edges = [(shortest_path[i], shortest_path[i+1]) for i in range(len(shortest_path)-1)]
        # Extract edges of the shortest path
        nx.draw_networkx_edges(G, pos, edgelist=shortest_path_edges, width=3, edge_color='red', arrowsize=20)
        # Draw shortest path edges with red color
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')  # Draw edge labels with red color
    plt.title("Graph of Locations")  # Set plot title
    plt.show()  # Display the plot

# Function to handle button click event
def on_click():
    start = start_var.get()  # Get the selected starting location
    end = end_var.get()  # Get the selected ending location
    shortest_path, total_distance = find_shortest_path(start, end, graph)  # Find the shortest path
    if shortest_path:  # Check if a shortest path exists
        result_label.config(text="Shortest path from {} to {}: {}\nTotal distance: {}".format(start, end, shortest_path, total_distance))
        # Update result label with shortest path and total distance
    else:
        result_label.config(text="There is no possible way to go from {} to {}".format(start, end))
        # Update result label with message if no path exists
    draw_graph(graph, shortest_path)  # Draw the graph with or without shortest path

# Create the main window
root = tk.Tk()  # Create a Tkinter window
root.title("Shortest Path Finder")  # Set window title

# Create and pack frames
input_frame = ttk.Frame(root, padding="20")  # Create a frame for input elements
input_frame.pack()  # Pack the input frame

# Create labels
start_label = ttk.Label(input_frame, text="Starting Location:")  # Create a label for starting location
start_label.grid(row=0, column=0, sticky="w")  # Grid the starting location label
end_label = ttk.Label(input_frame, text="Ending Location:")  # Create a label for ending location
end_label.grid(row=1, column=0, sticky="w")  # Grid the ending location label
result_label = ttk.Label(input_frame, text="")  # Create a label for displaying result
result_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))  # Grid the result label

# Create dropdowns
graph = store_data_in_database_and_update_json()  # Get the graph data from the database and update JSON file
locations = list(graph.keys())  # Get the list of locations
start_var = tk.StringVar(value=locations[0])  # Create a StringVar for starting location with default value
start_dropdown = ttk.Combobox(input_frame, textvariable=start_var, values=locations)  # Create a dropdown for starting location
start_dropdown.grid(row=0, column=1, pady=(0, 10))  # Grid the starting location dropdown
end_var = tk.StringVar(value=locations[1])  # Create a StringVar for ending location with default value
end_dropdown = ttk.Combobox(input_frame, textvariable=end_var, values=locations)  # Create a dropdown for ending location
end_dropdown.grid(row=1, column=1, pady=(10, 0))  # Grid the ending location dropdown

# Create button
find_button = ttk.Button(input_frame, text="Find Shortest Path", command=on_click)  # Create a button for finding the shortest path
find_button.grid(row=3, column=0, columnspan=2, pady=(10, 0))  # Grid the find button

root.mainloop()  # Start the Tkinter event loop




