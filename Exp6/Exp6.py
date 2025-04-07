from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)
EXCEL_FILE = 'supplier_data.xlsx'

# Load or create Excel file
def load_data():
    if not os.path.exists(EXCEL_FILE):
        data = {'ProductID': [1, 2], 'ProductName': ['Pen', 'Notebook'], 'Stock': [100, 50], 'Price': [5, 30]}
        pd.DataFrame(data).to_excel(EXCEL_FILE, index=False)
    return pd.read_excel(EXCEL_FILE)

# Save data back to Excel
def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

@app.route('/')
def home():
    return "Use /api/products to view products or /api/order to place an order."

@app.route('/api/products', methods=['GET'])
def get_products():
    df = load_data()
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/order', methods=['POST'])
def order_product():
    data = request.get_json()
    if not data or 'ProductID' not in data or 'Quantity' not in data:
        return jsonify({'error': 'ProductID and Quantity required'}), 400

    df = load_data()
    row = df[df['ProductID'] == data['ProductID']]

    if row.empty:
        return jsonify({'error': 'Product not found'}), 404

    i = row.index[0]
    if df.at[i, 'Stock'] < data['Quantity']:
        return jsonify({'error': 'Not enough stock'}), 400

    df.at[i, 'Stock'] -= data['Quantity']
    save_data(df)

    return jsonify({'message': 'Order placed', 'remaining_stock': int(df.at[i, 'Stock'])})

if __name__ == '__main__':
    app.run(debug=True)
