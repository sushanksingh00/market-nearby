erDiagram
  ACCOUNTS_USER {
    bigint id PK
    varchar username
    varchar email
    varchar user_type
    varchar phone
    text address
  }

  SHOPS_SHOP {
    bigint id PK
    varchar name
    text address
    varchar phone
    decimal latitude
    decimal longitude
    boolean is_open
    time opening_time
    time closing_time
    decimal rating
    datetime created_at
    datetime updated_at
    bigint owner_id FK
  }

  SHOPS_CATEGORY {
    bigint id PK
    varchar name "UNIQUE"
    text description
  }

  SHOPS_SHOPCATEGORY {
    bigint id PK
    bigint shop_id FK
    bigint category_id FK
    %% UNIQUE(shop_id, category_id)
  }

  SHOPS_PRODUCT {
    bigint id PK
    varchar name
    decimal price
    decimal original_price
    text description
    boolean in_stock
    int stock_quantity
    decimal rating
    datetime created_at
    datetime updated_at
    bigint shop_id FK
    bigint category_id FK
  }

  SHOPS_REVIEW {
    bigint id PK
    int rating
    text comment
    datetime created_at
    bigint user_id FK
    bigint shop_id FK "NULLABLE"
    bigint product_id FK "NULLABLE"
    %% UNIQUE(user_id, shop_id) and UNIQUE(user_id, product_id)
  }

  ACCOUNTS_USER ||--o{ SHOPS_SHOP : owns
  SHOPS_SHOP ||--o{ SHOPS_PRODUCT : has
  SHOPS_CATEGORY ||--o{ SHOPS_PRODUCT : categorizes
  SHOPS_SHOP ||--o{ SHOPS_SHOPCATEGORY : links
  SHOPS_CATEGORY ||--o{ SHOPS_SHOPCATEGORY : links
  ACCOUNTS_USER ||--o{ SHOPS_REVIEW : writes
  SHOPS_SHOP ||--o{ SHOPS_REVIEW : receives
  SHOPS_PRODUCT ||--o{ SHOPS_REVIEW : receives