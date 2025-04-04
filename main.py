import networkx as nx
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def precedence(op):
    if op in ['*', '/']:
        return 2
    elif op in ['+', '-']:
        return 1
    return 0

def apply_op(a, b, op):
    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/': return a // b

def evaluate(tokens):
    values = []
    ops = []
    i = 0
    while i < len(tokens):
        if tokens[i] == ' ':
            i += 1
            continue
        elif tokens[i] == '(':
            ops.append(tokens[i])
        elif tokens[i].isdigit():
            val = 0
            while i < len(tokens) and tokens[i].isdigit():
                val = (val * 10) + int(tokens[i])
                i += 1
            values.append(str(val))
            continue
        elif tokens[i] == ')':
            while len(ops) != 0 and ops[-1] != '(':
                val2 = values.pop()
                val1 = values.pop()
                op = ops.pop()
                values.append(apply_op(val1, val2, op))
            ops.pop()  # Remove the '('
        else:
            while (len(ops) != 0 and precedence(ops[-1]) >= precedence(tokens[i])):
                val2 = values.pop()
                val1 = values.pop()
                op = ops.pop()
                values.append(apply_op(val1, val2, op))
            ops.append(tokens[i])
        i += 1

    while len(ops) != 0:
        val2 = values.pop()
        val1 = values.pop()
        op = ops.pop()
        values.append(apply_op(val1, val2, op))

    return values[-1]

def infix_to_tac(expression):
    expression = expression.replace(" ", "")
    tokens = []
    i = 0
    while i < len(expression):
        if expression[i] in '+-*/()':
            tokens.append(expression[i])
            i += 1
        else:
            j = i
            while j < len(expression) and expression[j] not in '+-*/()':
                j += 1
            tokens.append(expression[i:j])
            i = j

    temp_count = 1
    tac = []
    stack = []
    op_stack = []

    for token in tokens:
        if token not in '+-*/()':
            stack.append(token)
        elif token == '(':
            op_stack.append(token)
        elif token == ')':
            while op_stack[-1] != '(':
                op = op_stack.pop()
                right = stack.pop()
                left = stack.pop()
                temp_var = f't{temp_count}'
                temp_count += 1
                tac.append(f"{temp_var} = {left} {op} {right}")
                stack.append(temp_var)
            op_stack.pop()
        else:
            while (op_stack and op_stack[-1] != '(' and
                   precedence(op_stack[-1]) >= precedence(token)):
                op = op_stack.pop()
                right = stack.pop()
                left = stack.pop()
                temp_var = f't{temp_count}'
                temp_count += 1
                tac.append(f"{temp_var} = {left} {op} {right}")
                stack.append(temp_var)
            op_stack.append(token)

    while op_stack:
        op = op_stack.pop()
        right = stack.pop()
        left = stack.pop()
        temp_var = f't{temp_count}'
        temp_count += 1
        tac.append(f"{temp_var} = {left} {op} {right}")
        stack.append(temp_var)

    if '=' in expression:
        var_part, expr_part = expression.split('=')
        tac.append(f"{var_part} = {stack[-1]}")

    return tac

def create_operation_node(operation, left_input, right_input, dag_nodes):
    node = {
        "op": operation,
        "left": left_input,
        "right": right_input,
        "labels": []
    }
    dag_nodes.append(node)
    return len(dag_nodes) - 1

def find_existing_node(operation, left_input, right_input, dag_nodes):
    for idx, node in enumerate(dag_nodes):
        if node["op"] == operation and node["left"] == left_input and node["right"] == right_input:
            return idx
    return None

def ensure_and_assign_label(label, dag_nodes, label_to_index):
    if label not in label_to_index:
        idx = create_operation_node(None, None, None, dag_nodes)
        dag_nodes[idx]["labels"].append(label)
        label_to_index[label] = idx
    else:
        idx = label_to_index[label]

    if label not in dag_nodes[idx]["labels"]:
        dag_nodes[idx]["labels"].append(label)
    
    return idx

def parse_three_address_instruction(instruction):
    if instruction.count("=") != 1:
        raise ValueError(f"Invalid instruction format: '{instruction}'. Expected exactly one '='.")
    
    lhs, rhs = instruction.split("=")
    result_var = lhs.strip()
    rhs = rhs.strip()

    if "[" in rhs and "]" in rhs:
        array_name, index_expr = rhs.split("[")
        return (result_var, "[]", array_name.strip(), index_expr.replace("]", "").strip())

    tokens = rhs.split()
    if len(tokens) == 3:
        operand1, operator, operand2 = tokens
        return (result_var, operator, operand1, operand2)
    elif len(tokens) == 2:
        operator, operand = tokens
        return (result_var, operator, operand, None)
    else:
        return (result_var, None, rhs, None)

def handle_instruction(result_var, operation, operand1, operand2, dag_nodes, label_to_index):
    left_index = ensure_and_assign_label(operand1, dag_nodes, label_to_index) if operand1 is not None else None
    right_index = ensure_and_assign_label(operand2, dag_nodes, label_to_index) if operand2 is not None else None
    if operation is None:
        node_index = left_index
    else:
        existing_node = find_existing_node(operation, left_index, right_index, dag_nodes)
        node_index = existing_node if existing_node is not None else create_operation_node(operation, left_index, right_index, dag_nodes)
    assign_label_to_node(result_var, node_index, dag_nodes, label_to_index)

def build_dag_from_instructions(instruction_list):
    dag_nodes = []
    label_to_index = {}
    
    for instr in instruction_list:
        try:
            result_var, operation, operand1, operand2 = parse_three_address_instruction(instr)
            handle_instruction(result_var, operation, operand1, operand2, dag_nodes, label_to_index)
        except ValueError as ve:
            raise ValueError(f"Error in instruction '{instr}': {str(ve)}")
    return dag_nodes

def hierarchical_positioning(graph):
    node_levels = {}
    for node in nx.topological_sort(graph):
        if graph.in_degree(node) == 0:
            node_levels[node] = 0
        else:
            node_levels[node] = max(node_levels[p] for p in graph.predecessors(node)) + 1

    levels_dict = {}
    for node, level in node_levels.items():
        levels_dict.setdefault(level, []).append(node)

    pos = {}
    for level, nodes_at_level in levels_dict.items():
        count = len(nodes_at_level)
        spacing = 1.0 / (count + 1)
        for i, node in enumerate(sorted(nodes_at_level)):
            pos[node] = ((i + 1) * spacing, -level)
    return pos

def draw_dag(dag_nodes):
    graph = nx.DiGraph()
    for idx, node in enumerate(dag_nodes):
        computed = node.get("computed_label", "")
        label = f"{node['op']}\n({', '.join(node['labels'])})\nLabel: {computed}" if node['op'] else f"{', '.join(node['labels'])}\nLabel: {computed}"
        graph.add_node(idx, label=label)
    for idx, node in enumerate(dag_nodes):
        if node["left"] is not None:
            graph.add_edge(idx, node["left"])
        if node["right"] is not None:
            graph.add_edge(idx, node["right"])
    
    pos = hierarchical_positioning(graph)
    labels = nx.get_node_attributes(graph, 'label')
    
    plt.figure(figsize=(10, 7))
    nx.draw(graph, pos, labels=labels, node_color='lightgreen', node_size=2200,
            font_size=10, arrows=True)
    plt.title("Three-Address Code DAG")
    
    # Save the plot to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    # Convert to base64
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_str

def label_dag(dag_nodes):
    G = nx.DiGraph()
    for idx, node in enumerate(dag_nodes):
        if node["left"] is not None:
            G.add_edge(idx, node["left"])
        if node["right"] is not None:
            G.add_edge(idx, node["right"])

    parent_map = {i: set() for i in range(len(dag_nodes))}
    for i, node in enumerate(dag_nodes):
        if node["left"] is not None:
            parent_map[node["left"]].add((i, "left"))
        if node["right"] is not None:
            parent_map[node["right"]].add((i, "right"))

    for idx, parents in parent_map.items():
        if not parents: 
            continue
        for parent_idx, side in parents:
            if dag_nodes[idx].get('computed_label') is None:
                if side == "left":
                    dag_nodes[idx]["computed_label"] = 1
                elif side == "right":
                    dag_nodes[idx]["computed_label"] = 0

    rev_topo_order = list(reversed(list(nx.topological_sort(G))))
    for idx in rev_topo_order:
        node = dag_nodes[idx]
        left = node["left"]
        right = node["right"]

        left_label = dag_nodes[left].get('computed_label') if left is not None else None
        right_label = dag_nodes[right].get('computed_label') if right is not None else None

        if left_label is not None and right_label is not None:
            if left_label == right_label:
                node['computed_label'] = left_label + 1
            else:
                node['computed_label'] = max(left_label, right_label)
        elif left_label is not None:
            node['computed_label'] = left_label
        elif right_label is not None:
            node['computed_label'] = right_label

    for idx, node in enumerate(dag_nodes):
        parent_indices = [i for i, n in enumerate(dag_nodes) if n["left"] == idx or n["right"] == idx]
        if not parent_indices:
            continue
        for parent_idx in parent_indices:
            parent = dag_nodes[parent_idx]
            if parent["left"] == idx and dag_nodes[idx].get('computed_label') is None:
                dag_nodes[idx]['computed_label'] = 1
            elif parent["right"] == idx and dag_nodes[idx].get('computed_label') is None:
                dag_nodes[idx]['computed_label'] = 0

def assign_label_to_node(label, node_index, dag_nodes, label_to_index):
    if label not in dag_nodes[node_index]["labels"]:
        dag_nodes[node_index]["labels"].append(label)
    label_to_index[label] = node_index

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        input_type = data.get('input_type', 'tac')  # 'tac' or 'expression'
        input_data = data.get('input_data', '')
        
        if not input_data:
            return jsonify({'error': 'No input provided'}), 400
        
        if input_type == 'expression':
            # Convert expression to TAC
            instructions = infix_to_tac(input_data)
        else:
            # Use TAC directly
            instructions = input_data.split('\n')
        
        # Build and label the DAG
        dag = build_dag_from_instructions(instructions)
        label_dag(dag)
        
        # Generate the visualization
        image_base64 = draw_dag(dag)
        
        # Calculate minimum registers
        used_as_children = set()
        for node in dag:
            if node["left"] is not None:
                used_as_children.add(node["left"])
            if node["right"] is not None:
                used_as_children.add(node["right"])

        root_nodes = [idx for idx in range(len(dag)) if idx not in used_as_children]
        min_registers = max(dag[idx].get("computed_label", 0) for idx in root_nodes) if root_nodes else 0
        
        # Prepare node details
        node_details = []
        for idx, node in enumerate(dag):
            labels = ', '.join(node['labels']) if node['labels'] else "None"
            op = node['op'] if node['op'] else "Leaf/Value"
            left = f"{node['left']}" if node['left'] is not None else "None"
            right = f"{node['right']}" if node['right'] is not None else "None"
            computed = node.get('computed_label', "None")
            node_details.append(f"Node {idx:2}: Label#: {computed}")
        
        return jsonify({
            'image': image_base64,
            'min_registers': min_registers,
            'node_details': '\n'.join(node_details),
            'tac_instructions': instructions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)