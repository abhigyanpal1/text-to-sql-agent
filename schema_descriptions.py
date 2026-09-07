schema_descriptions = {
    "customers": "Stores customer account information including name, email, and phone. Use for queries about customer details, contact information, or looking up a specific customer.",
    "addresses": "Stores multiple delivery addresses per customer with labels like home or work. Use for queries about where orders are shipped or a customer's saved locations.",
    "categories": "Stores product category names like electronics or clothing. Use for queries filtering or grouping products by category.",
    "products": "Stores product listings including title, description, current price, and stock quantity. Use for queries about product details, pricing, or inventory availability",
    "sellers": "Stores seller account information including store name, contact details, and shipping origin. Use for queries about who sells a product or seller details.",
    "product_sellers": "Links products to sellers with seller-specific pricing. Use for queries about which sellers offer a product or comparing prices across sellers.",
    "orders": "Stores customer orders with current status (pending, in transit, delivered) and order date. Use for queries about order history, delivery status, or recent purchases.",
    "order_items": "Links orders to specific products with quantity and price at the time of purchase. Use for queries about what products were in an order or historical purchase prices.",
    "cart_items": "Stores products currently in a customer's cart before checkout. Use for queries about pending carts or products a customer is considering.",
    "reviews": "Stores customer reviews and ratings for products. Use for queries about product feedback,ratings,or customer opinions.",
    "payments": "Stores payment transactions with amount, method and status (success,failed, pending). Use for queries about payment history or transaction status.",
    "returns": "Stores return requests with status, refund details, and scheduled pickup date. User for queries about return history or refund status."
}