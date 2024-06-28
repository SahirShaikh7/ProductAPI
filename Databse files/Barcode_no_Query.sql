CREATE TABLE product (
    barcode_number VARCHAR(255) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL
);
CREATE TABLE ingredient (
    ingredient_id SERIAL PRIMARY KEY,
    ingredient_name VARCHAR(255) NOT NULL,
    ingredient_component VARCHAR(1000),
    ingredient_hazard VARCHAR(1000),
    ingredient_allergy VARCHAR(1000)
);


CREATE TABLE product_ingredient (
    barcode_number VARCHAR(255),
    ingredient_id INT,
    PRIMARY KEY (barcode_number, ingredient_id),
    FOREIGN KEY (barcode_number) REFERENCES product(barcode_number),
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id)
);

CREATE OR REPLACE PROCEDURE insert_product_and_ingredients(
    in_barcode_number VARCHAR(255),
    in_product_name VARCHAR(255),
    in_ingredients VARCHAR[], -- Array of ingredient names
    in_components VARCHAR[] DEFAULT NULL, -- Optional array of components
    in_hazards VARCHAR[] DEFAULT NULL, -- Optional array of hazards
    in_allergies VARCHAR[] DEFAULT NULL -- Optional array of allergies
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_ingredient_id INT;
    v_ingredient_name VARCHAR(255);
    v_component VARCHAR(1000);
    v_hazard VARCHAR(1000);
    v_allergy VARCHAR(1000);
    i INT; -- Loop counter
BEGIN
    -- Check if the product already exists
    IF NOT EXISTS (
        SELECT 1 FROM product WHERE barcode_number = in_barcode_number
    ) THEN
        INSERT INTO product (barcode_number, product_name)
        VALUES (in_barcode_number, in_product_name);
    END IF;

    -- Iterate over each ingredient
    FOR i IN 1 .. array_length(in_ingredients, 1)
    LOOP
        v_ingredient_name := in_ingredients[i];

        -- Assign component, hazard, and allergy if corresponding arrays are not NULL and index i is within bounds
        IF in_components IS NOT NULL AND i <= array_length(in_components, 1) THEN
            v_component := in_components[i];
        ELSE
            v_component := NULL;
        END IF;

        IF in_hazards IS NOT NULL AND i <= array_length(in_hazards, 1) THEN
            v_hazard := in_hazards[i];
        ELSE
            v_hazard := NULL;
        END IF;

        IF in_allergies IS NOT NULL AND i <= array_length(in_allergies, 1) THEN
            v_allergy := in_allergies[i];
        ELSE
            v_allergy := NULL;
        END IF;

        -- Check if the ingredient already exists
        SELECT ingredient_id INTO v_ingredient_id
        FROM ingredient
        WHERE ingredient_name = v_ingredient_name;

        -- If the ingredient does not exist, insert it
        IF v_ingredient_id IS NULL THEN
            INSERT INTO ingredient (ingredient_name, ingredient_component, ingredient_hazard, ingredient_allergy)
            VALUES (v_ingredient_name, v_component, v_hazard, v_allergy)
            RETURNING ingredient_id INTO v_ingredient_id;
        END IF;

        -- Insert into product_ingredient table
        INSERT INTO product_ingredient (barcode_number, ingredient_id)
        VALUES (in_barcode_number, v_ingredient_id)
        ON CONFLICT DO NOTHING; -- Ensure no duplicates in product_ingredient
    END LOOP;
END;
$$;

CALL insert_product_and_ingredients(
    '1234567890', -- Example barcode number
    'Soft Drink', 
    ARRAY['Sugar', 'Carbonated Water', 'Colors', 'Flavoring'],
    ARRAY['', '', 'Natural', 'Artificial'], 
    ARRAY['', '', 'May cause hyperactivity', 'None'], 
    ARRAY['', '', 'None', 'None']
);

select * from product;
select * from ingredient;
select * from product_ingredient;


CREATE OR REPLACE FUNCTION retrieve_products_and_ingredients(
    in_barcode_number VARCHAR(255)
)
RETURNS TABLE(
    product_name VARCHAR(255),
    ingredient_id INT,
    ingredient_name VARCHAR(255),
    component VARCHAR(1000),
    hazard VARCHAR(1000),
    allergy VARCHAR(1000)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Fetch product name for the given barcode_number
    RETURN QUERY
    SELECT
        p.product_name,
        i.ingredient_id,
        i.ingredient_name,
        i.ingredient_component,
        i.ingredient_hazard,
        i.ingredient_allergy
    FROM product p
    LEFT JOIN product_ingredient pi ON p.barcode_number = pi.barcode_number
    LEFT JOIN ingredient i ON pi.ingredient_id = i.ingredient_id
    WHERE p.barcode_number = in_barcode_number;
END;
$$;


CALL retrieve_products_and_ingredients('1234567890');