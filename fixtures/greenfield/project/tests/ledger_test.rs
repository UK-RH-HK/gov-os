use orders_ledger::{Ledger, Order};

#[test]
fn appends_and_totals() {
    let mut l = Ledger::new();
    l.append(Order { id: 1, sku: "A".into(), quantity: 2, unit_cents: 150 }).unwrap();
    l.append(Order { id: 2, sku: "B".into(), quantity: 1, unit_cents: 99 }).unwrap();
    assert_eq!(l.total_cents(), 399);
    assert_eq!(l.len(), 2);
}

#[test]
fn rejects_duplicates_and_zero_quantity() {
    let mut l = Ledger::new();
    l.append(Order { id: 1, sku: "A".into(), quantity: 1, unit_cents: 1 }).unwrap();
    assert!(l.append(Order { id: 1, sku: "A".into(), quantity: 1, unit_cents: 1 }).is_err());
    assert!(l.append(Order { id: 3, sku: "C".into(), quantity: 0, unit_cents: 1 }).is_err());
}
