//! orders-ledger: a tiny append-only ledger of orders (synthetic fixture product).

#[derive(Debug, Clone, PartialEq)]
pub struct Order {
    pub id: u64,
    pub sku: String,
    pub quantity: u32,
    pub unit_cents: u64,
}

impl Order {
    pub fn total_cents(&self) -> u64 {
        self.quantity as u64 * self.unit_cents
    }
}

#[derive(Default)]
pub struct Ledger {
    orders: Vec<Order>,
}

impl Ledger {
    pub fn new() -> Self {
        Ledger::default()
    }
    pub fn append(&mut self, order: Order) -> Result<(), String> {
        if order.quantity == 0 {
            return Err("quantity must be positive".into());
        }
        if self.orders.iter().any(|o| o.id == order.id) {
            return Err(format!("duplicate order id {}", order.id));
        }
        self.orders.push(order);
        Ok(())
    }
    pub fn total_cents(&self) -> u64 {
        self.orders.iter().map(Order::total_cents).sum()
    }
    pub fn len(&self) -> usize {
        self.orders.len()
    }
    pub fn is_empty(&self) -> bool {
        self.orders.is_empty()
    }
}
