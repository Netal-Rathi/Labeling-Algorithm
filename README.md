# 🧠 TAC to DAG Visualizer (Register Allocation Optimizer)

This project provides a **web-based tool** to convert either an **infix expression** or a **three-address code (TAC)** into a **Directed Acyclic Graph (DAG)** for optimization and register allocation. It computes labels for the DAG nodes and visualizes the result, providing insights into how many registers are needed for evaluation.

---

## 🔧 Features

- ✅ Accepts either:
  - Infix arithmetic expressions (e.g., `a = b + c * d`)
  - Three-address code instructions (e.g., `t1 = b * d`)
- 🧮 Converts expressions to TAC automatically if required
- 📈 Constructs and visualizes the **DAG** for the computation
- 🧠 Computes labels for each node to determine **minimum register usage**
- 🖼️ Generates and returns the DAG image (Base64)
- 📦 Flask backend for processing and logic

---

## 📦 Project Structure

```
.
├── app.py               # Main Flask application
├── templates/
│   └── index.html       # Frontend template (not included here)
├── static/              # Static assets if needed
├── README.md            # You're here!
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/tac-dag-visualizer.git
cd tac-dag-visualizer
```

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install flask matplotlib networkx
```

### 4. Run the application

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## 🧾 API Usage

### POST `/generate`

**Request JSON:**

```json
{
  "input_type": "expression" | "tac",
  "input_data": "a = b + c * d"
}
```

- `input_type`: `"expression"` for infix, `"tac"` for three-address code.
- `input_data`: The actual code or expression.

**Response JSON:**

```json
{
  "image": "<base64-encoded DAG image>",
  "min_registers": 2,
  "node_details": "Node  0: Label#: 1\nNode  1: Label#: 0\n...",
  "tac_instructions": ["t1 = c * d", "t2 = b + t1", "a = t2"]
}
```

---

## 🧮 Example

Input expression:

```
a = b + c * d
```

TAC conversion:

```
t1 = c * d
t2 = b + t1
a = t2
```

Output includes:
- **DAG visualization** in Base64
- Computed labels for each node
- Minimum registers needed to evaluate: `2`

---

## 🧠 Core Concepts

- **DAG Construction**: Common subexpressions are merged.
- **Labeling Algorithm**: Assigns numeric labels to nodes based on evaluation order.
- **Register Allocation**: The maximum label among root nodes represents the minimum number of registers needed.

---

## 🧑‍💻 Technologies Used

- Python
- Flask
- NetworkX
- Matplotlib
- HTML (Jinja templates)

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Feel free to open issues or pull requests to improve this project.
