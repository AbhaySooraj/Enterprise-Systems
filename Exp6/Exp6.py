from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Path to the Excel file
EXCEL_FILE = 'supplier_data.xlsx'

# Load the Excel file if it exists, otherwise create a new one
def load_excel():
    if not os.path.exists(EXCEL_FILE):
        data = {
            'ProductID': [1, 2, 3],
            'ProductName': ['Pen', 'Notebook', 'Eraser'],
            'Stock': [100, 50, 200],
            'Price': [5, 30, 2]
        }
        df = pd.DataFrame(data)
        df.to_excel(EXCEL_FILE, index=False)
    return pd.read_excel(EXCEL_FILE)

# Function to save the updated data to the Excel file
def save_excel(df):
    df.to_excel(EXCEL_FILE, index=False)

# Home route
@app.route('/')
def home():
    return "Welcome to the Mock Supplier API! Use /api/products to get stock details or /api/order to place an order."

# Route to get all products from the supplier
@app.route('/api/products', methods=['GET'])
def get_products():
    df = load_excel()
    return jsonify(df.astype(object).to_dict(orient='records'))  # Convert all columns to standard Python types

@app.route('/api/order', methods=['POST'])
def place_order():
    order_data = request.get_json()

    if not order_data or 'ProductID' not in order_data or 'Quantity' not in order_data:
        return jsonify({'error': 'Invalid request. ProductID and Quantity are required.'}), 400

    product_id = order_data['ProductID']
    quantity = order_data['Quantity']

    df = load_excel()

    if product_id not in df['ProductID'].values:
        return jsonify({'error': 'Product not found'}), 404

    product_index = df[df['ProductID'] == product_id].index[0]
    available_stock = df.at[product_index, 'Stock']

    if available_stock < quantity:
        return jsonify({'error': 'Not enough stock available'}), 400

    df.at[product_index, 'Stock'] -= quantity
    save_excel(df)

    return jsonify({
        'message': 'Order placed successfully',
        'remaining_stock': int(df.at[product_index, 'Stock'])  # Convert to Python int
    })
if __name__ == '__main__':
    app.run(debug=True)
