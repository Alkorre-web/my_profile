---
title: "Топ-3 клиента по сумме заказов за месяц"
category: "analytics"
tags: ["postgresql", "join", "group by"]
erd_image: "top-clients.png"
---

## Описание задачи

Необходимо найти трёх клиентов с наибольшей суммой заказов в текущем месяце, исключая отменённые заказы.

## SQL Код

```sql
SELECT 
    c.customer_name, 
    SUM(o.total_amount) as total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.status != 'CANCELLED'
GROUP BY c.id, c.customer_name
ORDER BY total_spent DESC
LIMIT 3;
```